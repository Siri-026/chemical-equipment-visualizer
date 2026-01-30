import pandas as pd
import io
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Equipment, UploadHistory
from .serializers import EquipmentSerializer, UploadHistorySerializer, UserSerializer
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(username=username, password=password, email=email)
    token = Token.objects.create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_csv(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    
    if not csv_file.name.endswith('.csv'):
        return Response({'error': 'File must be CSV format'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        df = pd.read_csv(csv_file)
        
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        if not all(col in df.columns for col in required_columns):
            return Response({'error': f'CSV must contain columns: {", ".join(required_columns)}'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        df = df.dropna()
        
        avg_flowrate = df['Flowrate'].mean()
        avg_pressure = df['Pressure'].mean()
        avg_temperature = df['Temperature'].mean()
        total_count = len(df)
        
        user = request.user if request.user.is_authenticated else None
        
        upload_history = UploadHistory.objects.create(
            filename=csv_file.name,
            total_count=total_count,
            avg_flowrate=avg_flowrate,
            avg_pressure=avg_pressure,
            avg_temperature=avg_temperature,
            user=user
        )
        
        equipment_objects = []
        for _, row in df.iterrows():
            equipment_objects.append(Equipment(
                upload_history=upload_history,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=row['Flowrate'],
                pressure=row['Pressure'],
                temperature=row['Temperature']
            ))
        
        Equipment.objects.bulk_create(equipment_objects)
        
        if user:
            user_uploads = UploadHistory.objects.filter(user=user).order_by('-uploaded_at')
            if user_uploads.count() > 5:
                old_uploads = user_uploads[5:]
                for old_upload in old_uploads:
                    old_upload.delete()
        else:
            guest_uploads = UploadHistory.objects.filter(user__isnull=True).order_by('-uploaded_at')
            if guest_uploads.count() > 5:
                old_uploads = guest_uploads[5:]
                for old_upload in old_uploads:
                    old_upload.delete()
        
        type_distribution = df['Type'].value_counts().to_dict()
        
        return Response({
            'message': 'File uploaded successfully',
            'upload_id': upload_history.id,
            'summary': {
                'total_count': total_count,
                'avg_flowrate': round(avg_flowrate, 2),
                'avg_pressure': round(avg_pressure, 2),
                'avg_temperature': round(avg_temperature, 2),
                'type_distribution': type_distribution
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_summary(request):
    upload_id = request.query_params.get('upload_id')
    
    user = request.user if request.user.is_authenticated else None
    
    if not upload_id:
        if user:
            latest_upload = UploadHistory.objects.filter(user=user).order_by('-uploaded_at').first()
        else:
            latest_upload = UploadHistory.objects.filter(user__isnull=True).order_by('-uploaded_at').first()
        
        if not latest_upload:
            return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        upload_id = latest_upload.id
    
    try:
        upload = UploadHistory.objects.get(id=upload_id)
        
        if user and upload.user != user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif not user and upload.user is not None:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        equipment_list = Equipment.objects.filter(upload_history=upload)
        
        type_distribution = {}
        for eq in equipment_list:
            type_distribution[eq.equipment_type] = type_distribution.get(eq.equipment_type, 0) + 1
        
        return Response({
            'upload_id': upload.id,
            'filename': upload.filename,
            'uploaded_at': upload.uploaded_at,
            'total_count': upload.total_count,
            'avg_flowrate': round(upload.avg_flowrate, 2),
            'avg_pressure': round(upload.avg_pressure, 2),
            'avg_temperature': round(upload.avg_temperature, 2),
            'type_distribution': type_distribution
        })
    except UploadHistory.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_equipment_list(request):
    upload_id = request.query_params.get('upload_id')
    
    user = request.user if request.user.is_authenticated else None
    
    if not upload_id:
        if user:
            latest_upload = UploadHistory.objects.filter(user=user).order_by('-uploaded_at').first()
        else:
            latest_upload = UploadHistory.objects.filter(user__isnull=True).order_by('-uploaded_at').first()
        
        if not latest_upload:
            return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        upload_id = latest_upload.id
    
    try:
        upload = UploadHistory.objects.get(id=upload_id)
        
        if user and upload.user != user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif not user and upload.user is not None:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        equipment_list = Equipment.objects.filter(upload_history=upload)
        serializer = EquipmentSerializer(equipment_list, many=True)
        return Response(serializer.data)
    except UploadHistory.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_history(request):
    user = request.user if request.user.is_authenticated else None
    
    if user:
        uploads = UploadHistory.objects.filter(user=user).order_by('-uploaded_at')[:5]
    else:
        uploads = UploadHistory.objects.filter(user__isnull=True).order_by('-uploaded_at')[:5]
    
    serializer = UploadHistorySerializer(uploads, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_pdf_report(request):
    upload_id = request.data.get('upload_id')
    
    user = request.user if request.user.is_authenticated else None
    
    if not upload_id:
        if user:
            latest_upload = UploadHistory.objects.filter(user=user).order_by('-uploaded_at').first()
        else:
            latest_upload = UploadHistory.objects.filter(user__isnull=True).order_by('-uploaded_at').first()
        
        if not latest_upload:
            return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        upload_id = latest_upload.id
    
    try:
        upload = UploadHistory.objects.get(id=upload_id)
        
        if user and upload.user != user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif not user and upload.user is not None:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        equipment_list = Equipment.objects.filter(upload_history=upload)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{upload.id}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph("Chemical Equipment Analysis Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        info_data = [
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Dataset:', upload.filename],
            ['Upload Date:', upload.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Equipment:', str(upload.total_count)],
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        summary_title = Paragraph("Summary Statistics", styles['Heading2'])
        elements.append(summary_title)
        elements.append(Spacer(1, 0.1*inch))
        
        summary_data = [
            ['Metric', 'Average Value'],
            ['Flowrate', f"{upload.avg_flowrate:.2f}"],
            ['Pressure', f"{upload.avg_pressure:.2f}"],
            ['Temperature', f"{upload.avg_temperature:.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        equipment_title = Paragraph("Equipment Details", styles['Heading2'])
        elements.append(equipment_title)
        elements.append(Spacer(1, 0.1*inch))
        
        equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        
        for eq in equipment_list[:50]:
            equipment_data.append([
                eq.equipment_name,
                eq.equipment_type,
                f"{eq.flowrate:.2f}",
                f"{eq.pressure:.2f}",
                f"{eq.temperature:.2f}"
            ])
        
        equipment_table = Table(equipment_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        
        elements.append(equipment_table)
        
        doc.build(elements)
        return response
        
    except UploadHistory.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def export_excel(request):
    upload_id = request.data.get('upload_id')
    
    user = request.user if request.user.is_authenticated else None
    
    if not upload_id:
        if user:
            latest_upload = UploadHistory.objects.filter(user=user).order_by('-uploaded_at').first()
        else:
            latest_upload = UploadHistory.objects.filter(user__isnull=True).order_by('-uploaded_at').first()
        
        if not latest_upload:
            return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        upload_id = latest_upload.id
    
    try:
        upload = UploadHistory.objects.get(id=upload_id)
        
        if user and upload.user != user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        elif not user and upload.user is not None:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        equipment_list = Equipment.objects.filter(upload_history=upload)
        
        data = []
        for eq in equipment_list:
            data.append({
                'Equipment Name': eq.equipment_name,
                'Type': eq.equipment_type,
                'Flowrate': eq.flowrate,
                'Pressure': eq.pressure,
                'Temperature': eq.temperature
            })
        
        df = pd.DataFrame(data)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="equipment_data_{upload_id}.xlsx"'
        
        df.to_excel(response, index=False, engine='openpyxl')
        return response
        
    except UploadHistory.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)
