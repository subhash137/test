from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Receipt, ReceiptItem, ChatMessage
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from django.conf import settings
import base64
from PIL import Image
import io
from .models import *
from .utils.rag_utils import RAGChain
from django.core.serializers.json import DjangoJSONEncoder
import json


rag_chain = RAGChain()



def home(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('home')
        messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        messages.error(request, 'Error creating account')
    else:
        form = UserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')



@csrf_exempt
@login_required
def upload_receipt(request):
    if request.method == 'POST':
        try:
            # Get the uploaded image
            image_file = request.FILES['receipt_image']
            
            # Create Receipt instance
            receipt = Receipt.objects.create(image=image_file)
            
            # Convert image to base64
            image_file.seek(0)
            
            # Read the image file and convert to RGB if necessary
            image = Image.open(image_file)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create a byte buffer to store the JPEG image
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Initialize OpenAI client
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Prepare the prompt
            standard_prompt = """
            Extract information from this document and if any key not in the image you can give None to its value and provide it in the following JSON format:
            {
                "merchant_name": "Store or company name if not provided give None",
                "date": "Date of purchase or invoice date in YYYY-MM-DD format",
                "document_number": "Receipt/Bill/Invoice number",
                "total_items": Number of unique items,
                "items": [
                    {
                        "name": "Item description",
                        "quantity": Number of units,
                        "unit_price": Price per unit,
                        "total_price": Total price for this item
                    }


                ],
                "subtotal": "Subtotal before tax",
                "tax": "Tax amount",
                "total": "Final total amount",
                "additional_charges": [
                    {
                        "description": "Charge description",
                        "amount": "Amount"
                    }
                ],
                "payment_method": "Method of payment",
                "payment_status": "Paid/Unpaid/Partial"
            }
            Ensure the response is a valid JSON object.
            """
            
            # Call OpenAI API
            response_content = client.chat.completions.create(
                model="gpt-4o-mini",  # Using correct model name
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": standard_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            response_content = response_content.choices[0].message.content
            print(response_content)
            try:
                # Try to parse the JSON response
                receipt_data = json.loads(response_content)
            except json.JSONDecodeError as je:
                # If JSON parsing fails, try to clean the response
                cleaned_content = response_content.strip()
                # Remove any markdown code block indicators if present
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
                cleaned_content = cleaned_content.strip()
                
             
                receipt_data = json.loads(cleaned_content)
            
            # Write response to file for debugging
            with open('fr.txt', 'w') as f:
                f.write(json.dumps(receipt_data, indent=2))
            
            # Update Receipt instance
            receipt.merchant_name = receipt_data.get('merchant_name')
            receipt.date = receipt_data.get('date')
            receipt.document_number = receipt_data.get('document_number')
            receipt.total_items = receipt_data.get('total_items')
            receipt.subtotal = receipt_data.get('subtotal')
            receipt.tax = receipt_data.get('tax')
            receipt.total = receipt_data.get('total')
            receipt.payment_method = receipt_data.get('payment_method')
            receipt.payment_status = receipt_data.get('payment_status')
            receipt.raw_json = receipt_data
            receipt.save()
            
            # Create related objects
            for item in receipt_data.get('items', []):
                ReceiptItem.objects.create(
                    receipt=receipt,
                    name=item['name'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    total_price=item['total_price']
                )
            
            for charge in receipt_data.get('additional_charges', []):
                AdditionalCharge.objects.create(
                    receipt=receipt,
                    description=charge['description'],
                    amount=charge['amount']
                )
            
            return JsonResponse({
                'status': 'success',
                'receipt_id': receipt.id,
                'data': receipt_data
            })
            
        except Exception as e:
          
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return render(request, 'ai_vision/reciept_parser.html')


@login_required
def receipt_list(request):
    receipts = Receipt.objects.all().order_by('-created_at')
    return render(request, 'ai_vision/reciept_list.html', {'receipts': receipts})





@login_required
# def dashboard(request):
#     # Chart 1: Units Produced per Laptop Model
#     laptops = Laptop.objects.all()
#     units_produced_data = {
#         "labels": [laptop.model_name for laptop in laptops],
#         "values": [laptop.units_produced for laptop in laptops],
#     }

#     # Chart 2: Order Status Distribution
#     orders = Order.objects.all()
#     status_counts = orders.values('status').annotate(count=models.Count('status'))
#     order_status_data = {
#         "labels": [status['status'] for status in status_counts],
#         "values": [status['count'] for status in status_counts],
#     }

#     # Chart 3: Inventory Distribution
#     inventories = Inventory.objects.all()
#     warehouse_counts = inventories.values('warehouse_location').annotate(total=models.Sum('quantity'))
#     inventory_data = {
#         "labels": [warehouse['warehouse_location'] for warehouse in warehouse_counts],
#         "values": [warehouse['total'] for warehouse in warehouse_counts],
#     }

#     # Data Table: Recent Orders
#     recent_orders = Order.objects.all()
#     print("Recent_orsers: ", json.dumps(recent_orders))
#     print("units_produced_data", json.dumps(units_produced_data))
#     print("order_status_data", json.dumps(order_status_data))
#     print("inventory_data", json.dumps(inventory_data))
#     ert = {
#         'units_produced_data': units_produced_data,
#         'order_status_data': order_status_data,
#         'inventory_data': inventory_data,
#         'recent_orders': recent_orders,
#     }

#     # Pass data as JSON to the template
#     return render(request, 'dashboard.html', ert)


# def dashboard(request):
#     # Chart 1: Units Produced per Laptop Model
#     laptops = Laptop.objects.all()
#     units_produced_data = {
#         "labels": [laptop.model_name for laptop in laptops],
#         "values": [laptop.units_produced for laptop in laptops],
#     }

#     # Chart 2: Order Status Distribution
#     orders = Order.objects.all()
#     status_counts = orders.values('status').annotate(count=models.Count('status'))
#     order_status_data = {
#         "labels": [status['status'] for status in status_counts],
#         "values": [status['count'] for status in status_counts],
#     }

#     # Chart 3: Inventory Distribution
#     inventories = Inventory.objects.all()
#     warehouse_counts = inventories.values('warehouse_location').annotate(total=models.Sum('quantity'))
#     inventory_data = {
#         "labels": [warehouse['warehouse_location'] for warehouse in warehouse_counts],
#         "values": [warehouse['total'] for warehouse in warehouse_counts],
#     }

#     # Recent Orders as a list of dictionaries
#     recent_orders = list(Order.objects.all().values())
#     print("Recent_orsers: ", recent_orders)
#     print("units_produced_data", units_produced_data)
#     # print("order_status_data", json.dumps(order_status_data))
#     # print("inventory_data", json.dumps(inventory_data))
#     context = {
#         'units_produced_data': units_produced_data,
#         'order_status_data': order_status_data,
#         'inventory_data': inventory_data,
#         'recent_orders': recent_orders,
#     }

#     return render(request, 'dashboard.html', context)



def dashboard(request):
    # Chart 1: Units Produced per Laptop Model
    laptops = Laptop.objects.all()
    units_produced_data = {
        "labels": [laptop.model_name for laptop in laptops],
        "values": [laptop.units_produced for laptop in laptops],
    }

    # Chart 2: Order Status Distribution
    status_counts = Order.objects.values('status').annotate(count=Count('status'))
    order_status_data = {
        "labels": [status['status'] for status in status_counts],
        "values": [status['count'] for status in status_counts],
    }

    # Chart 3: Inventory Distribution
    warehouse_counts = Inventory.objects.values('warehouse_location').annotate(total=Sum('quantity'))
    inventory_data = {
        "labels": [warehouse['warehouse_location'] for warehouse in warehouse_counts],
        "values": [warehouse['total'] for warehouse in warehouse_counts],
    }

    # Recent Orders with related laptop information
    recent_orders = Order.objects.select_related('laptop').order_by('-order_date')[:20]

    # Prepare context with safe JSON serialization
    context = {
        'units_produced_data': json.dumps(units_produced_data, cls=DjangoJSONEncoder),
        'order_status_data': json.dumps(order_status_data, cls=DjangoJSONEncoder),
        'inventory_data': json.dumps(inventory_data, cls=DjangoJSONEncoder),
        'recent_orders': recent_orders,
    }

    return render(request, 'dashboard.html', context)





# @login_required
def chat_home(request):
    messages = ChatMessage.objects.all()
    return render(request, 'rag/document_reader.html', {'messages': messages})

@csrf_exempt
# @login_required
def chat_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Save user message
        ChatMessage.objects.create(
            sender='USER',
            message=user_message
        )
        
        # Get bot response
        try:
            bot_response = rag_chain.get_response(user_message)
            
            # Save bot response
            ChatMessage.objects.create(
                sender='BOT',
                message=bot_response
            )
            
            return JsonResponse({
                'status': 'success',
                'message': bot_response
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
