"""
Servicio para generar reportes PDF de cultivos con mapas y detalles.
"""
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from datetime import datetime
import requests
from PIL import Image as PILImage, ImageDraw, ImageFont
from django.conf import settings
import urllib.parse


def generate_crop_pdf(crop, weather_data=None):
    """
    Genera un PDF con detalles del cultivo, mapa y clima.
    Retorna un BytesIO con el PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=0.5*inch, leftMargin=0.5*inch,
                          topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    story = []
    
    # Título
    title = Paragraph(f'Reporte de Cultivo: {crop.name}', title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Información del cultivo
    story.append(Paragraph('Información del Cultivo', heading_style))
    
    crop_info = [
        ['Campo', 'Valor'],
        ['Nombre', crop.name or 'N/A'],
        ['Propietario (Email)', crop.user.email],
        ['País', crop.country_code],
        ['Latitud', f'{crop.latitude:.4f}' if crop.latitude else 'N/A'],
        ['Longitud', f'{crop.longitude:.4f}' if crop.longitude else 'N/A'],
        ['Ubicación en Mapa', f'{crop.latitude:.4f}, {crop.longitude:.4f}\n({crop.user.email})' if crop.latitude and crop.longitude else 'N/A'],
        ['Fecha de Siembra', crop.sowing_date.strftime('%d/%m/%Y') if crop.sowing_date else 'N/A'],
        ['Creado', crop.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Descripción', crop.description or 'Sin descripción'],
    ]
    
    crop_table = Table(crop_info, colWidths=[2*inch, 3.5*inch])
    crop_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    story.append(crop_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Mapa estático
    if crop.latitude and crop.longitude:
        story.append(Paragraph('Ubicación en Mapa', heading_style))
        try:
            map_url = generate_map_image(crop.latitude, crop.longitude, crop.name, crop.user.email)
            if map_url:
                img = Image(map_url, width=5*inch, height=3.5*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            story.append(Paragraph(f'<i>No se pudo generar el mapa: {str(e)}</i>', normal_style))
    
    # Información del clima (si disponible)
    if weather_data and weather_data.get('ok'):
        story.append(PageBreak())
        story.append(Paragraph('Datos Climáticos Actuales', heading_style))
        
        weather_info = [
            ['Parámetro', 'Valor'],
            ['Temperatura', f"{weather_data.get('temperature', 'N/A')} °C"],
            ['Humedad', f"{weather_data.get('humidity', 'N/A')} %"],
            ['Lluvia (mm)', f"{weather_data.get('rain_mm', 'N/A')} mm"],
            ['Viento', f"{weather_data.get('wind_ms', 'N/A')} m/s"],
        ]
        
        if 'recommendation' in weather_data:
            weather_info.append(['Recomendación', weather_data['recommendation']])
        
        weather_table = Table(weather_info, colWidths=[2*inch, 3.5*inch])
        weather_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
        ]))
        story.append(weather_table)
    
    # Pie de página
    story.append(Spacer(1, 0.3*inch))
    footer_text = f'Reporte generado el {datetime.now().strftime("%d/%m/%Y %H:%M")} por AgroSmart'
    story.append(Paragraph(f'<i>{footer_text}</i>', normal_style))
    
    # Generar PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_map_image(lat, lon, crop_name, owner_email=None):
    """
    Genera una imagen del mapa estático usando Google Maps Static API.
    Zoom moderado (zoom=14) para ver el área sin estar muy cerca ni muy alejado.
    """
    try:
        width = 600
        height = 500
        zoom = 14  # Zoom moderado - perfecto para ver cultivo y alrededores
        
        # Obtener API key de Google Maps desde settings
        google_maps_api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        
        if not google_maps_api_key:
            print("[WARNING] GOOGLE_MAPS_API_KEY no configurada. Usando fallback con Bing Maps Static.")
            # Usar Bing Maps Static como alternativa (no requiere API key)
            return generate_map_image_bing(lat, lon, crop_name, owner_email, width, height, zoom)
        
        # URL de Google Maps Static API
        # Parámetros:
        # - center=LAT,LON: Centro del mapa
        # - zoom=14: Zoom moderado
        # - size=600x500: Tamaño de la imagen
        # - markers=color:red|LAT,LON: Marcador rojo en la ubicación
        # - style: Estilo del mapa
        
        markers = f"color:red|size:mid|{lat},{lon}"
        google_maps_url = (
            f"https://maps.googleapis.com/maps/api/staticmap?"
            f"center={lat},{lon}"
            f"&zoom={zoom}"
            f"&size={width}x{height}"
            f"&markers={markers}"
            f"&style=feature:road|visibility:on"
            f"&style=feature:water|color:0xb3d9ff"
            f"&style=feature:landscape|color:0xf3f3f3"
            f"&key={google_maps_api_key}"
        )
        
        print(f"[DEBUG] Descargando mapa de Google Maps: {google_maps_url[:80]}...")
        
        try:
            response = requests.get(google_maps_url, timeout=8)
            if response.status_code == 200 and len(response.content) > 5000:
                print(f"[DEBUG] Mapa Google Maps descargado exitosamente ({len(response.content)} bytes)")
                
                # Abrir imagen y agregar texto
                map_img = PILImage.open(BytesIO(response.content))
                draw = ImageDraw.Draw(map_img)
                
                # Panel inferior con información
                try:
                    font = ImageFont.truetype("arial.ttf", 11)
                except:
                    font = ImageFont.load_default()
                
                text_info = f"{crop_name} | Lat: {lat:.6f}, Lon: {lon:.6f}"
                if owner_email:
                    text_info += f" | {owner_email}"
                
                # Panel oscuro para legibilidad
                bbox = draw.textbbox((10, height - 40), text_info, font=font)
                draw.rectangle([5, bbox[1] - 5, width - 5, bbox[3] + 5], 
                              fill=(0, 0, 0, 220))
                draw.text((10, height - 35), text_info, fill=(255, 255, 255), font=font)
                
                result_buffer = BytesIO()
                map_img.save(result_buffer, format='PNG')
                result_buffer.seek(0)
                return result_buffer
            else:
                print(f"[ERROR] Google Maps retornó status {response.status_code}")
                raise Exception("Error en respuesta de Google Maps")
        except Exception as e:
            print(f"[ERROR] Error con Google Maps: {e}")
            raise
        
    except Exception as e:
        print(f"[ERROR] generate_map_image falló: {e}")
        # Fallback a mapa personalizado
        return generate_map_image_fallback(lat, lon, crop_name, owner_email)


def generate_map_image_bing(lat, lon, crop_name, owner_email=None, width=600, height=500, zoom=14):
    """
    Genera mapa usando Bing Maps Static (sin API key requerida, pero con limitaciones).
    """
    try:
        print(f"[DEBUG] Intentando Bing Maps Static...")
        
        # Bing Maps Static (requiere API key también, pero lo intentamos)
        bing_url = f"https://dev.virtualearth.net/REST/v1/Imagery/Map/Road/{lat},{lon}/{zoom}?mapSize={width},{height}"
        
        response = requests.get(bing_url, timeout=8)
        if response.status_code == 200 and len(response.content) > 5000:
            print(f"[DEBUG] Mapa Bing Maps descargado")
            map_img = PILImage.open(BytesIO(response.content))
            
            # Agregar texto
            draw = ImageDraw.Draw(map_img)
            try:
                font = ImageFont.truetype("arial.ttf", 11)
            except:
                font = ImageFont.load_default()
            
            text_info = f"{crop_name} | Lat: {lat:.6f}, Lon: {lon:.6f}"
            if owner_email:
                text_info += f" | {owner_email}"
            
            bbox = draw.textbbox((10, height - 40), text_info, font=font)
            draw.rectangle([5, bbox[1] - 5, width - 5, bbox[3] + 5], 
                          fill=(0, 0, 0, 220))
            draw.text((10, height - 35), text_info, fill=(255, 255, 255), font=font)
            
            result_buffer = BytesIO()
            map_img.save(result_buffer, format='PNG')
            result_buffer.seek(0)
            return result_buffer
    except:
        pass
    
    # Si todo falla, usar fallback
    return generate_map_image_fallback(lat, lon, crop_name, owner_email)


def generate_map_image_fallback(lat, lon, crop_name, owner_email=None, width=600, height=500):
    """
    Fallback: Genera mapa personalizado profesional.
    """
    try:
        print(f"[DEBUG] Usando mapa personalizado fallback")
        
        # Crear gradiente de fondo: cielo azul arriba, verde abajo
        img = PILImage.new('RGB', (width, height), color=(100, 200, 100))
        pixels = img.load()
        
        # Gradiente: azul cielo en top, verde tierra en bottom
        for y in range(height):
            ratio = y / height
            if ratio < 0.3:
                # Cielo: azul claro
                r = int(135 + (100 - 135) * (ratio / 0.3))
                g = int(206 + (180 - 206) * (ratio / 0.3))
                b = int(235 + (120 - 235) * (ratio / 0.3))
            else:
                # Tierra: verde
                r = int(100 + (34 - 100) * ((ratio - 0.3) / 0.7))
                g = int(200 + (139 - 200) * ((ratio - 0.3) / 0.7))
                b = int(100 + (34 - 100) * ((ratio - 0.3) / 0.7))
            
            for x in range(width):
                pixels[x, y] = (r, g, b)
        
        draw = ImageDraw.Draw(img)
        
        # Grid de referencia
        for i in range(0, width, 75):
            draw.line([(i, 0), (i, height)], fill=(150, 150, 150), width=1)
        for i in range(0, height, 75):
            draw.line([(0, i), (width, i)], fill=(150, 150, 150), width=1)
        
        # Marcador PIN rojo en el centro (donde está la ubicación)
        center_x = width // 2
        center_y = height // 2
        
        # PIN rojo estilo Google Maps
        # Triángulo/gota
        draw.polygon([(center_x, center_y - 30), (center_x - 20, center_y + 15), 
                     (center_x, center_y + 30), (center_x + 20, center_y + 15)], 
                    fill=(255, 0, 0), outline=(220, 0, 0))
        # Círculo interior blanco
        draw.ellipse([center_x - 12, center_y - 12, center_x + 12, center_y + 12], 
                    fill=(255, 255, 255), outline=(255, 0, 0), width=2)
        
        # Panel superior: título y coordenadas
        try:
            font_title = ImageFont.truetype("arial.ttf", 14)
            font_text = ImageFont.truetype("arial.ttf", 11)
            font_small = ImageFont.truetype("arial.ttf", 9)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Fondo oscuro superior
        draw.rectangle([0, 0, width, 70], fill=(20, 20, 20, 220))
        draw.text((10, 5), f"📍 {crop_name}", fill=(255, 255, 0), font=font_title)
        draw.text((10, 35), f"Lat: {lat:.6f}  |  Lon: {lon:.6f}", fill=(255, 255, 255), font=font_text)
        
        # Fondo oscuro inferior
        info_text = f"Zoom: x14 (moderado) | {owner_email if owner_email else 'Propietario'}"
        draw.rectangle([0, height - 50, width, height], fill=(20, 20, 20, 220))
        draw.text((10, height - 38), "Punto exacto con PIN rojo", fill=(255, 255, 255), font=font_text)
        draw.text((10, height - 18), info_text, fill=(200, 200, 200), font=font_small)
        
        result_buffer = BytesIO()
        img.save(result_buffer, format='PNG')
        result_buffer.seek(0)
        print(f"[DEBUG] Mapa personalizado generado exitosamente")
        return result_buffer
        
    except Exception as e:
        print(f"[ERROR] Fallback de mapa falló: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_crops_batch_pdf(crops_list):
    """
    Genera un PDF con múltiples cultivos.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=0.5*inch, leftMargin=0.5*inch,
                          topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph('Reporte de Cultivos - AgroSmart', title_style))
    story.append(Paragraph(f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla resumen
    summary_data = [['Cultivo', 'Propietario (Email)', 'País', 'Ubicación (Lat, Lon)']]
    for crop in crops_list:
        location = f"({crop.latitude:.2f}, {crop.longitude:.2f})\n{crop.user.email}" if crop.latitude and crop.longitude else "N/A"
        summary_data.append([crop.name, crop.user.email, crop.country_code, location])
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    story.append(summary_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer
