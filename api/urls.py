from django.urls import path
from . import views


urlpatterns =[
   
    path('pdf/', views.PDFChatAPIView, name = 'upload_pdf'),
]