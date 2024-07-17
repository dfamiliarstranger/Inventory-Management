from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [ 
    path('form/', views.sale_create_view, name='sale_form'), 
    path('<int:pk>/delete/', views.sale_delete, name='sale_delete'),
    path('list/', views.sale_list, name='sale_list'),
]

