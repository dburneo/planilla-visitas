import json, urllib.request
import requests
import textwrap
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, PageBreak, Image, Spacer, Paragraph, 
    Table, TableStyle, Spacer, Frame, BaseDocTemplate, PageTemplate, NextPageTemplate, 
    FrameBreak, Flowable)
from reportlab.platypus import CellStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
import os


with urllib.request.urlopen("https://xinternet.co/j/dailyforms.json") as url:
    data = json.loads(url.read().decode())

fileName = "Planilla-" + data['date']['value'] + ".pdf"

pagesize=(landscape(letter))

class PlanillaVisitas(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        doc = SimpleDocTemplate("planillavisitas/" + fileName,pagesize=pagesize, topMargin=1 * cm, bottomMargin=1 * cm)   # Directorio raíz de la app.

        # Código producción OK
                
        def encabezado(Story):
            """ Creación del encabezado que contiene el logo y nombre del informe. """

            I = Image("planillavisitas/dailyforms/static/dailyforms/logo-horizontal.jpg", width=136, height=42)
            titulo1 = Paragraph("RECOLECCIÓN Y TRANSPORTE", estilo['Titulo'])
            titulo2 = Paragraph("PLANILLA DE RECOLECCIÓN RUTA SANITARIA", estilo['Titulo'])
            titulo3 = Paragraph("LOG_FOR_001", estilo['Titulo'])
                            
            t = Table(
                data = [
                    [I, [titulo1, titulo2], titulo3]
                ],
                style=[
                    ('VALIGN',(1,0),(1,0),'CENTER'),
                    ('VALIGN',(2,0),(2,0),'BOTTOM'),
                    ('GRID',(0,0),(3,0),0.5,colors.gray),
                ], 
                colWidths=[144, 476, 130],
            )

            # Story.append(Spacer(0,1))
            Story.append(t)

            return Story

        
        def encabezado2(Story):
            """ Encabezado que identifica la ruta del informe y los nombres de los campos. """

            titulo1 = Paragraph(data['date']['display_name'] + ": " + data['date']['value'], estilo['Titulo1'])
            titulo2 = Paragraph("Ruta: " + data['route']['display_name'], estilo['Titulo2'])
            titulo3 = Paragraph(data['vehicle']['display_name'] + ": ", estilo['Titulo2'])
            titulo4 = Paragraph(data['telephone']['display_name'] + ": ", estilo['Titulo2'])
            titulo5 = Paragraph(data['aditional_forms']['display_name'] + ": ", estilo['Titulo2'])
            t = Table(
                data = [
                    [titulo1, titulo2, titulo3, titulo4, titulo5]
                ],
                style = [
                    ('VALIGN',(0,0),(4,0),'TOP'),
                    ('GRID',(0,0),(4,0),0.5,colors.gray),
                ], 
                colWidths = [144, 159, 159, 158, 130], 
                rowHeights = [11], 
            )
            Story.append(t)

            # Nombre de las columnas de los datos

            col1 = Paragraph("CÓDIGO", estilo['camposRegistro'])
            col2 = Paragraph("ENTIDAD", estilo['camposRegistro'])
            col3 = Paragraph("DIRECCIÓN", estilo['camposRegistro'])
            col4 = Paragraph("BARRIO", estilo['camposRegistro'])
            col5 = Paragraph("CAT", estilo['camposRegistro'])
            col6 = Paragraph("H_LLEGADA", estilo['camposRegistro'])
            col7 = Paragraph("H_SALIDA", estilo['camposRegistro'])
            col8 = Paragraph("KGBIO", estilo['camposRegistro'])
            col9 = Paragraph("KGANA", estilo['camposRegistro'])
            col10 = Paragraph("KGCORTO", estilo['camposRegistro'])
            col11 = Paragraph("KGANIMAL", estilo['camposRegistro'])
            col12 = Paragraph("NOMBRE_FUNCIONARIO_ENTREGA", estilo['camposRegistro'])
            col13 = Paragraph("ORDEN", estilo['camposRegistro'])

            t = Table(
                data = [
                    [col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13]
                ], 
                style=[
                    ('VALIGN',(0,0),(12,0),'TOP'),
                    ('GRID',(0,0),(12,0),0.5,colors.gray),
                ], 
                colWidths=[42, 83, 83, 65, 27, 56, 47, 35, 38, 48, 50, 138, 38], 
                rowHeights=11, # cellStyles=[...]
            )
            
            Story.append(t)

            return Story

        
        def finRuta(Story):
            """ Contenido del fin de ruta. """

            NombreConductor = Paragraph(data['driver_name']['display_name'] + ": ", estilo['finRuta'])
            FirmaConductor = Paragraph(data['driver_signature']['display_name'] + ": ", estilo['finRuta'])
            NombreAyudante = Paragraph(data['auxiliar_name']['display_name'] + ": ", estilo['finRuta'])
            FirmaAyudante = Paragraph(data['auxiliar_signature']['display_name'] + ": ", estilo['finRuta'])
            HoraSalidaBase = Paragraph(data['departure_time']['display_name'] + ": ", estilo['finRuta'])
            HoraLLegadaBase = Paragraph(data['arrival_time']['display_name'] + ": ", estilo['finRuta'])
            TotalKilosAna = Paragraph(data['total_ana']['display_name'] + ": ", estilo['finRuta'])
            TotalKilosBio = Paragraph(data['total_bio']['display_name'] + ": ", estilo['finRuta'])
            MicrosHabilitados = Paragraph(data['enabled_micros']['display_name'] + ": ", estilo['finRuta'])
            TotalManifiestos = Paragraph(data['total_manifests']['display_name'] + ": ", estilo['finRuta'])

            t = Table(
                data = [
                    [NombreConductor, FirmaConductor],
                    [NombreAyudante, FirmaAyudante],
                    [HoraSalidaBase, HoraLLegadaBase],
                    [TotalKilosAna, TotalKilosBio],
                    [MicrosHabilitados, TotalManifiestos]
                ], 
                style = [
                    ('VALIGN',(0,0),(1,0),'BOTTOM'),
                    ('GRID',(0,0),(-1,-1),0.5,colors.gray),
                ], 
                colWidths=[300],
            )
            Story.append(t)
            return Story


        # Código principal.

        estilo = getSampleStyleSheet()

        estilo.add(ParagraphStyle(name = "Titulo", alignment=TA_CENTER, fontSize=7, fontName="Helvetica-Bold"))
        estilo.add(ParagraphStyle(name = "Titulo1", alignment=TA_LEFT, fontSize=7, fontName="Helvetica-Bold"))
        estilo.add(ParagraphStyle(name = "Titulo2", alignment=TA_LEFT, fontSize=7, fontName="Helvetica"))

        # Estilo para cada registro

        estilo.add(ParagraphStyle(name = "camposRegistro", alignment=TA_CENTER, fontSize=7, fontName="Helvetica-Bold"))
        estilo.add(ParagraphStyle(name = "Registros", alignment=TA_LEFT, fontSize=6.5, fontName="Helvetica"))
        estilo.add(ParagraphStyle(name = "finRuta", alignment=TA_LEFT, fontSize=7, fontName="Helvetica"))

        Story=[]

        encabezado(Story)

        encabezado2(Story)

        # Extraer del Json los datos para los registros

        col = []
        dataColRegistros = []
        numRegistros = 0
        regSpace = " "

        for visita in data['visits']:
            dataCol1 = Paragraph(visita['code'], estilo['Registros'])
            dataCol2 = Paragraph(visita['client'], estilo['Registros'])
            dataCol3 = Paragraph(visita['address'], estilo['Registros'])
            dataCol4 = Paragraph(visita['city_division'], estilo['Registros'])
            dataCol5 = Paragraph(visita['category'], estilo['Registros'])
            dataCol6 = Paragraph(regSpace, estilo['Registros'])
            dataCol7 = Paragraph(regSpace, estilo['Registros'])
            dataCol8 = Paragraph(visita['bio_category'], estilo['Registros'])
            dataCol9 = Paragraph(visita['ana_category'], estilo['Registros'])
            dataCol10 = Paragraph(visita['cut_category'], estilo['Registros'])
            dataCol11 = Paragraph(visita['animal_category'], estilo['Registros'])
            dataCol12 = Paragraph(regSpace, estilo['Registros'])
            dataCol13 = Paragraph(visita['order'], estilo['Registros'])

            # Incluir el condicional para los colores de las celdas boolean

            t = Table (
                data = [
                    [dataCol1, dataCol2, dataCol3, dataCol4, dataCol5, dataCol6, dataCol7, dataCol8, dataCol9, dataCol10, 
                    dataCol11, dataCol12, dataCol13]
                ],
                style=[
                        ('VALIGN',(0,0),(12,0),'BOTTOM'),
                        ('GRID',(0,0),(12,0),0.5, colors.gray),
                ], 
                colWidths=[42, 83, 83, 65, 27, 56, 47, 35, 38, 48, 50, 138, 38],
            )
            
            Story.append(t)           # Se incluye registro * registro
            numRegistros += 1

            # Agregar saltos de página

            if numRegistros > 14:
                Story.append(PageBreak())

                encabezado(Story)
                encabezado2(Story)

                numRegistros = 0

        finRuta(Story)

        # Fin de código principal

        doc.build(Story)

        fs = FileSystemStorage("planillavisitas/")
        with fs.open(fileName) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=' + fileName
            return response
        
        return response

        # Fin de código
