from django.urls import path
from . import views

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('upload/', views.upload_csv, name='upload_csv'),
    path('summary/', views.get_summary, name='get_summary'),
    path('equipment/', views.get_equipment_list, name='get_equipment'),
    path('history/', views.get_history, name='get_history'),
    path('generate-report/', views.generate_pdf_report, name='generate_report'),
    path('export-excel/', views.export_excel, name='export_excel'),

]
