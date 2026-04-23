import openpyxl
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Cotización Importación"

# Colors
DARK_BLUE = "1F3864"
MEDIUM_BLUE = "2E5FA3"
LIGHT_BLUE = "BDD7EE"
ORANGE = "C55A11"
LIGHT_ORANGE = "FCE4D6"
GRAY = "D9D9D9"
WHITE = "FFFFFF"
YELLOW = "FFD966"

def make_border(style="thin"):
    s = Side(style=style)
    return Border(left=s, right=s, top=s, bottom=s)

def header_style(ws, row, col, value, bg=DARK_BLUE, font_color=WHITE, bold=True, size=11):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(bold=bold, color=font_color, size=size)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = make_border()
    return cell

def data_cell(ws, row, col, value, bg=WHITE, bold=False, align="left", number_format=None):
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = Font(bold=bold, color="000000", size=10)
    cell.fill = PatternFill("solid", fgColor=bg)
    cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)
    cell.border = make_border()
    if number_format:
        cell.number_format = number_format
    return cell

# Column widths
ws.column_dimensions["A"].width = 32
ws.column_dimensions["B"].width = 48
ws.column_dimensions["C"].width = 22
ws.column_dimensions["D"].width = 18

# Row 1: Title
ws.merge_cells("A1:D1")
cell = ws["A1"]
cell.value = "COTIZACIÓN DE IMPORTACIÓN MARÍTIMA"
cell.font = Font(bold=True, color=WHITE, size=14)
cell.fill = PatternFill("solid", fgColor=DARK_BLUE)
cell.alignment = Alignment(horizontal="center", vertical="center")
cell.border = make_border()
ws.row_dimensions[1].height = 30

# Row 2: Subheader route
ws.merge_cells("A2:D2")
cell = ws["A2"]
cell.value = "ORIGEN: NINGBO  →  DESTINO: BUENAVENTURA"
cell.font = Font(bold=True, color=WHITE, size=11)
cell.fill = PatternFill("solid", fgColor=MEDIUM_BLUE)
cell.alignment = Alignment(horizontal="center", vertical="center")
cell.border = make_border()
ws.row_dimensions[2].height = 20

# Row 3: Column headers
headers = ["CONCEPTO", "DESCRIPCIÓN", "TARIFA USD", "VALOR COP"]
for col, h in enumerate(headers, start=1):
    header_style(ws, 3, col, h, bg=MEDIUM_BLUE, size=10)
ws.row_dimensions[3].height = 22

# ── SECTION 1: Flete Internacional Marítimo ──
ROW = 4
ws.merge_cells(f"A{ROW}:D{ROW}")
cell = ws[f"A{ROW}"]
cell.value = "FLETE INTERNACIONAL MARÍTIMO"
cell.font = Font(bold=True, color=WHITE, size=11)
cell.fill = PatternFill("solid", fgColor=ORANGE)
cell.alignment = Alignment(horizontal="center", vertical="center")
cell.border = make_border()
ws.row_dimensions[ROW].height = 18
ROW += 1

flete_rows = [
    ("Flete Internacional Marítimo",
     "Flete marítimo Ningbo – Buenaventura. Tarifa por TON/CBM",
     "USD 208.1", 763102.65),
    ("Handling",
     "Gasto de origen / consolidación puerto origen",
     "USD 90", 330030),
    ("Desconsolidación",
     "Gasto en destino. Tarifa 25 x TON/CBM. Mínima USD 120",
     "USD 120", 440040),
    ("Radicación",
     "Gasto en destino – Radicación sistema DIAN",
     "USD 180", 660060),
    ("Manejo Agente de Carga",
     "Gasto en destino – Manejo de carga",
     "USD 150", 550050),
    ("THC",
     "Gastos en destino naviera",
     "USD 80", 293360),
]

alt = False
for concepto, desc, tarifa, valor in flete_rows:
    bg = LIGHT_BLUE if alt else WHITE
    data_cell(ws, ROW, 1, concepto, bg=bg, bold=True)
    data_cell(ws, ROW, 2, desc, bg=bg)
    data_cell(ws, ROW, 3, tarifa, bg=bg, align="center")
    data_cell(ws, ROW, 4, valor, bg=bg, align="right", number_format='$ #,##0.00')
    ws.row_dimensions[ROW].height = 32
    ROW += 1
    alt = not alt

# Total flete
data_cell(ws, ROW, 1, "TOTAL FLETE INTERNACIONAL + GASTOS EN DESTINO",
          bg=YELLOW, bold=True, align="left")
ws.merge_cells(f"A{ROW}:C{ROW}")
ws.cell(row=ROW, column=1).alignment = Alignment(horizontal="center", vertical="center")
data_cell(ws, ROW, 4, 3036642, bg=YELLOW, bold=True, align="right",
          number_format='$ #,##0.00')
ws.row_dimensions[ROW].height = 20
ROW += 1

# Blank separator
ROW += 1

# ── SECTION 2: Agenciamiento Aduanero ──
ws.merge_cells(f"A{ROW}:D{ROW}")
cell = ws[f"A{ROW}"]
cell.value = "AGENCIAMIENTO ADUANERO – BUENAVENTURA"
cell.font = Font(bold=True, color=WHITE, size=11)
cell.fill = PatternFill("solid", fgColor=ORANGE)
cell.alignment = Alignment(horizontal="center", vertical="center")
cell.border = make_border()
ws.row_dimensions[ROW].height = 18
ROW += 1

ws.merge_cells(f"A{ROW}:D{ROW}")
cell = ws[f"A{ROW}"]
cell.value = "Servicio de Agenciamiento Aduanero de Destino"
cell.font = Font(bold=True, color="000000", size=10, italic=True)
cell.fill = PatternFill("solid", fgColor=LIGHT_ORANGE)
cell.alignment = Alignment(horizontal="center", vertical="center")
cell.border = make_border()
ws.row_dimensions[ROW].height = 16
ROW += 1

agencia_rows = [
    ("Desaduanamiento en Buenaventura",
     "Costo tarifa mínima / advaron del 0.38%",
     "", 1450000),
    ("Gastos Consolidados",
     "Gastos operativos",
     "", 220000),
    ("Elaboración de Declaraciones de Importación y Valor",
     "Elaboración de declaraciones de importación y de valor. $40.000 el juego "
     "(aplica según cantidad de partidas)",
     "", 40000),
    ("Transmisión Siglo XXI",
     "Costo tarifa mínima $780.000 / advaron del 0.38%",
     "", 280000),
    ("Firma Agencia de Aduana",
     "Servicio de firma, presentación y representación ante autoridades en puerto",
     "", 900000),
    ("Liberación de BL",
     "Liberación de BL ante línea naviera – incluye comodato",
     "", 120000),
    ("Impuestos de Aduana",
     "Arancel 5% – IVA 19%  //  Arancel $3.142.000 – IVA $12.538.000",
     "", 15700000),
    ("Inspección DIAN",
     "En caso de aplicar o tener selectividad con inspección (SOLO SI APLICA)",
     "", 600000),
    ("Gastos Portuarios",
     "Bodegajes estimados por 8 días en puerto para la legalización",
     "", 1800000),
    ("Transporte Terrestre Buenaventura – Cali",
     "Transporte terrestre Buenaventura – Cali consolidado",
     "", 400000),
]

alt = False
for concepto, desc, tarifa, valor in agencia_rows:
    bg = LIGHT_ORANGE if alt else WHITE
    data_cell(ws, ROW, 1, concepto, bg=bg, bold=True)
    data_cell(ws, ROW, 2, desc, bg=bg)
    data_cell(ws, ROW, 3, tarifa if tarifa else "–", bg=bg, align="center")
    data_cell(ws, ROW, 4, valor, bg=bg, align="right", number_format='$ #,##0.00')
    ws.row_dimensions[ROW].height = 36
    ROW += 1
    alt = not alt

# Total anticipo
data_cell(ws, ROW, 1, "TOTAL ANTICIPO",
          bg=YELLOW, bold=True, align="left")
ws.merge_cells(f"A{ROW}:C{ROW}")
ws.cell(row=ROW, column=1).alignment = Alignment(horizontal="center", vertical="center")
data_cell(ws, ROW, 4, 21510000, bg=YELLOW, bold=True, align="right",
          number_format='$ #,##0.00')
ws.row_dimensions[ROW].height = 22

output_path = "/home/user/Casa-del-Carburador/cotizacion_importacion.xlsx"
wb.save(output_path)
print(f"Archivo guardado: {output_path}")
