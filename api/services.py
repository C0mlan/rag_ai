import os
import chromadb
from google import genai
from django.core.files.storage import FileSystemStorage
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# load_dotenv()
client = genai.Client(api_key= os.environ.get('google_api_key'))
DATA_PATH = r'./data'
CHROMA_PATH = r"./chroma_db1"


def load_pdf():
    '''STEP 1: Load pdf from directory
    '''
    loader = PyPDFDirectoryLoader(DATA_PATH)
    docs = loader.load()
    return docs

def process_pdf_upload(docs):
    '''STEP 2: Process PDF documents for RAG pipeline

    '''
    documents =[]
    metadata = []
    ids = []
    embedding = []
    i = 0
    #splitter to break documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,    
    chunk_overlap=100   
    )
    chunks = text_splitter.split_documents(docs)

    for chunk in chunks:
        ids.append("ID"+ str(i))
        documents.append(chunk.page_content)
        metadata.append(chunk.metadata)
        i += 1
        
        emb = embedding_pdf(chunk)
        embedding.append(emb)
        chroma_db(ids, documents, metadata, embedding)
    
    return  ids, documents, metadata, embedding


def embedding_pdf(chunk):
     """Generates an embedding for a text chunk using the Gemini model."""
    result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk.page_content
        )
    emb = result.embeddings[0].values
    # print(emb)
    return emb          
                
def chroma_db(ids, documents, metadata, embedding):
     """Adds the provided data to Chromadb"""
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name="words")
    
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadata,
        embeddings=embedding
    )
    return collection

# collection.upsert(
#     documents= documents,
#     metadatas = metadata,
#     ids = ids
# )
def init():
    docs = load_pdf()
    process = process_pdf_upload(docs)
    
    
    return process
# init()