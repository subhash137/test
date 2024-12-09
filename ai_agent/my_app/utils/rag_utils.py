import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from django.conf import settings

class RAGChain:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        self.embeddings = OpenAIEmbeddings()
        self.prompt = hub.pull("rlm/rag-prompt")
        
        # Initialize the vector store
        self.initialize_vectorstore()
    
    def initialize_vectorstore(self):
        # Path to your documents directory
        docs_dir = 'my_app/documents'
        
        # Read all text files from the documents directory
        documents = []
        for filename in os.listdir(docs_dir):
            if filename.endswith('.txt'):
                with open(os.path.join(docs_dir, filename), 'r', encoding='utf-8') as file:
                    content = file.read()
                    documents.append({
                        'page_content': content,
                        'metadata': {'source': filename}
                    })
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.create_documents(
            [doc['page_content'] for doc in documents],
            metadatas=[doc['metadata'] for doc in documents]
        )
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings
        )
        
        # Initialize retriever
        self.retriever = self.vectorstore.as_retriever()
    
    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    def get_response(self, question):
        rag_chain = (
            {
                "context": self.retriever | self.format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain.invoke(question)