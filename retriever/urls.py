from django.urls import path
# from .views import document_upload, search

from .views import upload_files, searchView,ViewDocuments,deleteDocumentView
from . import views
urlpatterns = [
    path('upload/', upload_files, name='upload'),
    path('', ViewDocuments, name='uploaded_documents'),
    path('search/', searchView, name='search'),
    path("delete_documents/", deleteDocumentView, name="delete_documents"),
     path('add-query-history-api/', views.addQueryHistory, name='add-query-history-api'),
     path('delete-query-history-api/', views.deleteQueryHistory, name='delete-query-history-api'),
] 