from django.urls import path
from .views import DocIngestionView


urlpatterns =[
   
    path('upload_doc/',DocIngestionView.as_view(), name ='upload_doc'),
]