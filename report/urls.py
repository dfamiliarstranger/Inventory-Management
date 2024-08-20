from django.urls import path
from .views import business_statement

urlpatterns = [
    path('business-statement/', business_statement, name='business_statement'),
]
