# ai_agent/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),  # This is the home page
    path('logout/', views.logout_view, name='logout'),
    path('document-reader/', views.chat_home, name='document_reader'),
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipt-parser/', views.upload_receipt, name='receipt_parser'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('message/', views.chat_message, name='message'),
    path('document-reader/message/', views.chat_message, name='chat_message'),

]