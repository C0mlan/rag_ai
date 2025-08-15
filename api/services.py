import os
from django.core.files.storage import default_storage
from django.core.cache import cache
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def process_pdf_upload(pdf_file):
 
    old_file_path = cache.get("last_uploaded_pdf")
    if old_file_path and os.path.exists(old_file_path):
        os.remove(old_file_path)

    file_path = default_storage.save(pdf_file.name, pdf_file)
    cache.set("last_uploaded_pdf", file_path)

   
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(docs)


    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)

    return vector_store.as_retriever()