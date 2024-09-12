from django.urls import path
from .views import *

urlpatterns = [
    path('business-statement/', business_statement, name='business_statement'),
    path('business-report/', business_report_view , name='business_report'),
    path('report/sales/<int:month>/<int:year>/', sales_report, name='sales_report'),
    path('reports/purchases/<int:month>/<int:year>/', purchases_report, name='purchases_report'),
    path('reports/production/<int:month>/<int:year>/', production_report, name='production_report'),
    path('reports/business/<int:month>/<int:year>/', business_report_detail_view, name='business_report_view'),
]
