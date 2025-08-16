from django.urls import path
from . import views


urlpatterns =[
   
    path('upload_pdf/', views.PDFChatAPIView, name = 'upload_pdf'),
    path('query_pdf/', views.query_pdf, name = 'query_pdf'),
]