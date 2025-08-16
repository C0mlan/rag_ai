import os
from django.shortcuts import render
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .services import process_pdf_upload
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from langchain.prompts import PromptTemplate




@api_view(["POST"])
def PDFChatAPIView(request):
    pdf_file = request.FILES.get("pdf")
    if not pdf_file:
        return Response({"error": "PDF file is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        process_pdf_upload(pdf_file) # load, chuck and embed
        print("PDF upload & embedding complete")
        return Response({"status": "done"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(["POST"])
def query_pdf(request):
    
    query = request.data.get("query") # Get the query string from the request body
    if not query:
        return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Retrieve the saved FAISS vector store from cache
    vector_store = cache.get("pdf_vector_store")
    if not vector_store:
        return Response({"error": "No PDF uploaded yet"}, status=status.HTTP_400_BAD_REQUEST)

    retriever = vector_store.as_retriever()
   
    # intialize Groq llm
    llm = ChatGroq(
        temperature=0,
        groq_api_key= os.environ.get('groq_api_key'),
        model_name="llama-3.3-70b-versatile"
    )

    template = """You are given the following context from a document:
    {context}

    Question: {question}

    Instructions: If the question is not related to the context, reply:
    'The question does not relate to the document.'

    Answer:"""

    prompt = PromptTemplate(input_variables=["context", "question"], template=template)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",  # combine retrieved docs into one context
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain.invoke(query)

    return Response({"answer": result["result"]})