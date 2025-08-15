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
    

