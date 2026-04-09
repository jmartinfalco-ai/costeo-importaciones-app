import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

st.set_page_config(
    page_title="Aramis Coding Company",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================
# 🎨 FIX COLORES FINAL
# =========================
st.markdown("""
<style>

/* =========================
   BOTONES - HOVER FIX
========================= */

/* Botones normales */
button {
    background-color: #ffffff !important;
    color: black !important;
    border-radius: 8px !important;
    border: none !important;
    transition: 0.2s;
}

/* Hover (cuando pasás el mouse) */
button:hover {
    background-color: #00ff9f !important;
    color: black !important;
}

/* Botón activo (click) */
button:active {
    background-color: #00cc7a !important;
    color: black !important;
}

/* Fondo general */
body, .stApp {
    background-color: #0e1117;
}

/* TODO el texto */
* {
    color: white !important;
}

/* Labels */
label {
    color: white !important;
}

/* Inputs */
input, textarea {
    color: black !important;
}

/* Placeholder */
::placeholder {
    color: #999 !important;
}

/* Botones */
button {
    color: black !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    color: white !important;
}

/* Texto uploader */
[data-testid="stFileUploader"] span {
    color: white !important;
}

/* Para asegurar hover también */
button:hover span {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)


# 🌍 IDIOMA
idioma = st.radio(
    "🌐 Language / Idioma",
    ["ES", "EN", "中文"],
    horizontal=True
)

version = st.radio(
    "📄 Versión de Reporte",
    ["Eyecandy", "Simple"],
    horizontal=True
)

if idioma == "ES":
    st.success("🇦🇷 Idioma Español seleccionado")
elif idioma == "EN":
    st.success("🇺🇸 English language selected")
elif idioma == "中文":
    st.success("🇨🇳 已选择中文 (Mandarín)")

textos = {
    "ES": {
        "titulo": "Reporte de Costos de Importación",
        "detalle": "Detalle de Productos",
        "observaciones": "Observaciones",
        "fob": "FOB",
        "flete": "Flete",
        "seguro": "Seguro",
        "cif": "CIF",
        "costo_unitario": "Costo Unitario",
        "porcentaje": "% sobre FOB",
        "contrato": "Nro. de Contrato",
        "fecha": "Fecha",
    },
    "EN": {
        "titulo": "Import Cost Report",
        "detalle": "Product Details",
        "observaciones": "Observations",
        "fob": "FOB",
        "flete": "Freight",
        "seguro": "Insurance",
        "cif": "CIF",
        "costo_unitario": "Unit Cost",
        "porcentaje": "% of FOB",
        "contrato": "Contract No.",
        "fecha": "Date",
    },
    "中文": {
        "titulo": "进口成本报告",
        "detalle": "产品明细",
        "observaciones": "备注",
        "fob": "离岸价 (FOB)",
        "flete": "运费",
        "seguro": "保险",
        "cif": "到岸价 (CIF)",
        "costo_unitario": "单位成本",
        "porcentaje": "占FOB比例",
        "contrato": "合同编号",
        "fecha": "日期",
    }
}

t = textos[idioma]

col_btn, col_msg = st.columns([1,2])

with col_btn:
    generar_pdf = st.button("📄 Generar Reporte PDF", key="btn_pdf")

with col_msg:
    if generar_pdf:
        st.success("✅ Generado con éxito!")
        st.toast("PDF generado ✔")

# CUADROS DE TEXTO
st.markdown("### 🧾 Datos del Reporte")

colA, colB = st.columns(2)

with colA:
    contrato = st.text_input(
        "📄 Número de Contrato",
        placeholder="Ej: NUCARG-2-26-0001 / NUC1Y123456B00"
    )

with colB:
    fecha = st.text_input(
        "📅 Fecha de importación",
        placeholder="DD/MM/AAAA"
    )

observaciones = st.text_area(
    "📝 Observaciones",
    placeholder="Escribí cualquier comentario para el informe...",
    height=120
)

# 🎨 ESTILO
st.markdown("""
<style>
.stApp {background-color:#000;color:white;}
.stApp {
    color: white;
}
h1 {color:#00ff88 !important;font-size:32px;}
h2 {font-size:18px;}
.stFileUploader {
    background-color: rgba(0,255,136,0.08);
    border:1px solid #00ff88;
    border-radius:10px;
    padding:15px;
}
[data-testid="stFileUploaderDropzone"] {
    background-color: rgba(0,255,136,0.08);
    border:1px dashed #00ff88;
}
img {filter: drop-shadow(0px 0px 10px rgba(0,255,136,0.3));}
</style>
""", unsafe_allow_html=True)

# 🐈 HEADER
col1, col2 = st.columns([1,3])
with col1:
    st.image("assets/aramis.png", width=400)
with col2:
    st.markdown("<h1>Sistema de Costeo de Importaciones</h1>", unsafe_allow_html=True)
    st.markdown("<h2>Aramis Coding Company</h2>", unsafe_allow_html=True)

st.markdown("---")

# 📥 Upload
uploaded_file = st.file_uploader("📂 Subí tu archivo Excel", type=["xlsx"])

# 🧠 FUNCION PRINCIPAL
def extraer_data(df):

    # 🔹 BLOQUE FIJO
    fob = float(df.iloc[0,1])
    flete = float(df.iloc[1,1])
    seguro = float(df.iloc[2,1])

    # 🔹 AJUSTES DINAMICOS
    ajustes = 0
    for i in range(7,20):
        texto = str(df.iloc[i,0]).lower()
        if "ajuste" in texto:
            try:
                ajustes += float(df.iloc[i,1])
            except:
                pass

    cif = fob + flete + seguro + ajustes

    # 🔹 GASTOS
    try:
        despachante = float(df.iloc[15,4])
    except:
        despachante = 0

    try:
        forwarder = float(df.iloc[15,7])
    except:
        forwarder = 0

    gastos_total = despachante + forwarder

    # 🔹 PRODUCTOS
    productos = []
    start = None

    for i in range(len(df)):
        if "codigo" in str(df.iloc[i,0]).lower():
            start = i + 1
            break

    if start:
        i = start
        while True:
            codigo = df.iloc[i,0]

            if pd.isna(codigo) or "TOTAL" in str(codigo):
                break

            producto = {
                "codigo": codigo,
                "nombre": df.iloc[i,1],
                "uni": df.iloc[i,2],  # 🔥 AGREGAR ESTA LÍNEA
                "fob_total": df.iloc[i,4],
                "flete": float(df.iloc[i,6]) if pd.notna(df.iloc[i,6]) else 0,
                "seguro": float(df.iloc[i,7]) if pd.notna(df.iloc[i,7]) else 0,
                "gastos": float(df.iloc[i,8]) if pd.notna(df.iloc[i,8]) else 0,
                "costo_unitario": df.iloc[i,18],
                "porcentaje": df.iloc[i,19]
            }

            productos.append(producto)
            i += 1

    return fob, flete, seguro, ajustes, cif, gastos_total, productos


# 🚀 EJECUCION
if uploaded_file:

    df = pd.read_excel(uploaded_file, header=None)

    fob, flete, seguro, ajustes, cif, gastos, productos = extraer_data(df)

    cantidad_items = len(productos)

    # 🎯 CARDS PRINCIPALES
    st.markdown("### 📊 Resumen General")

    col1, col2, col3, col4 = st.columns(4)

    def card(titulo, valor):
        return f"""
        <div style='background-color:#111;
                    padding:20px;
                    border-radius:10px;
                    border:1px solid #00ff88;
                    min-height:140px;
                    height:auto;
                    display:flex;
                    flex-direction:column;
                    justify-content:center'>
            <h4 style="margin:0;font-size:16px;">{titulo}</h4>
            <h2 style="margin:5px 0 0 0;font-size:22px;word-break:keep-all;">{valor}</h2>
        </div>
        """

    col1.markdown(card("💰 FOB", f"{fob:,.2f} USD"), unsafe_allow_html=True)
    col2.markdown(card("🚛 Flete", f"{flete:,.2f} USD"), unsafe_allow_html=True)
    col3.markdown(card("🛡 Seguro", f"{seguro:,.2f} USD"), unsafe_allow_html=True)
    col4.markdown(card("📦 CIF", f"{cif:,.2f} USD"), unsafe_allow_html=True)

    # 🎯 SEGUNDO BLOQUE
    st.markdown("### 📊 Resumen")

    col1, col2, col3, col4 = st.columns(4)

    # 1️⃣ GASTOS LOCALES (B6)
    gastos_locales = float(df.iloc[5,1])

    # 3️⃣ IMPUESTOS (sumar columnas K a P)
    impuestos_total = 0

    for i in range(len(df)):
        texto = str(df.iloc[i,0]).lower()

        if "total" in texto:
            try:
                fila = df.iloc[i]

                impuestos_total = sum([
                    float(fila[10]) if pd.notna(fila[10]) else 0,
                    float(fila[11]) if pd.notna(fila[11]) else 0,
                    float(fila[12]) if pd.notna(fila[12]) else 0,
                    float(fila[13]) if pd.notna(fila[13]) else 0,
                    float(fila[14]) if pd.notna(fila[14]) else 0,
                    float(fila[15]) if pd.notna(fila[15]) else 0,
                    float(fila[16]) if pd.notna(fila[16]) else 0
                ])

            except:
                pass

    # 2️⃣ GASTOS EN ADUANA (buscar última fila en columna L = index 11)
    gastos_aduana = impuestos_total + 10

    productos = []

    for i in range(len(df)):

        codigo = str(df.iloc[i,0])

        # 🔥 detectar códigos reales
        if codigo.startswith("1405") or codigo.startswith("REP"):

            producto = {
                "codigo": codigo,
                "nombre": df.iloc[i,1],
                "uni": df.iloc[i,2] if pd.notna(df.iloc[i,2]) else 1,
                "fob_total": df.iloc[i,4],
                "flete": float(df.iloc[i,6]) if pd.notna(df.iloc[i,6]) else 0,
                "seguro": float(df.iloc[i,7]) if pd.notna(df.iloc[i,7]) else 0,
                "gastos": float(df.iloc[i,8]) if pd.notna(df.iloc[i,8]) else 0,
                "costo_unitario": df.iloc[i,18],
                "porcentaje": df.iloc[i,19]
            }

            productos.append(producto)

    productos_texto = ""

    for p in productos:
        try:
            nombre = str(p["nombre"]).strip()
            cantidad = int(float(p["uni"]))
        except:
            cantidad = 1

        productos_texto += f"• {nombre} ({cantidad} unidad)<br>"

    # 🎯 CARDS
    col1.markdown(card("🏭 Gastos Locales", f"{gastos_locales:,.2f} USD"), unsafe_allow_html=True)
    col2.markdown(card("🛃 Gastos en Aduana", f"{gastos_aduana:,.2f} USD"), unsafe_allow_html=True)
    col3.markdown(card("💸 Impuestos Totales", f"{impuestos_total:,.2f} USD"), unsafe_allow_html=True)
    col4.markdown(card("<div style='margin-top:8px; display:flex; align-items:center;'>📦 Productos</div>", productos_texto), unsafe_allow_html=True)

    # 📦 PRODUCTOS
    st.markdown("### 📦 Detalle por Producto")

    for p in productos:
        html = f"""
        <div style='background-color:#111;
        padding:20px;
        border-radius:12px;
        border:1px solid #00ff88;
        margin-bottom:15px'>

        <h3 style="margin-bottom:10px;">
        {p['codigo']} - {p['nombre']}
        </h3>

        <div style="display:grid;
        grid-template-columns: repeat(3, 1fr);
        gap:10px;
        font-size:18px;">

        <div><b>FOB:</b><br>{p['fob_total']:,.2f} USD</div>
        <div><b>Flete:</b><br>{p['flete']:,.2f} USD</div>
        <div><b>Seguro:</b><br>{p['seguro']:,.2f} USD</div>

        <div><b>Gastos:</b><br>{p['gastos']:,.2f} USD</div>
        <div><b>Costo Unitario:</b><br>{p['costo_unitario']:,.2f}</div>
        <div><b>% sobre FOB:</b><br>{p['porcentaje']:,.2f}%</div>

        </div>
        </div>
        """

        st.markdown(html, unsafe_allow_html=True)



    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader

    # =========================
    # 🧠 LIMPIAR NOMBRE CONTRATO
    # =========================

    contrato_limpio = contrato.split("/")[0].strip()

    # limpiar fecha
    fecha_archivo = fecha.replace("/", "-")

    # idioma texto
    if idioma == "ES":
        idioma_txt = "Español"
    elif idioma == "EN":
        idioma_txt = "English"
    else:
        idioma_txt = "中文"

    if version == "Eyecandy":
        tipo = "Full"
    else:
        tipo = "Simple"

    nombre_pdf = f"Reporte {contrato_limpio} - {idioma_txt} - {fecha_archivo} ({tipo}).pdf"

    if generar_pdf:

        c = canvas.Canvas(nombre_pdf, pagesize=letter)
        width, height = letter

        # =========================
        # 🎯 CONFIGURAR FUENTE
        # =========================
        if idioma == "中文":
            pdfmetrics.registerFont(TTFont("NotoChinese", "NotoSansSC-Regular.ttf"))
            fuente = "NotoChinese"
        else:
            fuente = "Helvetica"

        # 🖼️ FONDO
        if version == "Eyecandy":
            fondo = ImageReader("assets/fondo.png")
        else:
            fondo = ImageReader("assets/fondo_simple.png")

        c.drawImage(fondo, 0, 0, width=width, height=height)

        # =========================
        # 🔝 HEADER (ZONA AZUL)
        # =========================

        # 📄 DATOS
        c.setFont(fuente, 11)
        c.drawCentredString(width/2 + 5, 620, f"{t.get('contrato','Nro. de Contrato')}: {contrato}")
        c.drawCentredString(width/2, 595, f"{t.get('fecha','Fecha')}: {fecha}")

        # 💰 RESUMEN EN 2 COLUMNAS
        # 📊 RESUMEN EN 2 COLUMNAS (como Canva)

        # Columna izquierda
        c.drawString(120, 565, f"{t['fob']}: {fob:,.2f} USD")
        c.drawString(115, 545, f"{t['seguro']}: {seguro:,.2f} USD")

        # Columna derecha
        c.drawString(350, 565, f"{t['flete']}: {flete:,.2f} USD")
        c.drawString(350, 545, f"{t['cif']}: {cif:,.2f} USD")

        # =========================
        # 📦 CUERPO (ZONA BLANCA)
        # =========================

        y = 480  # 🔥 BAJAMOS TODO

        c.setFont(fuente, 13)
        c.drawString(50, y, t["detalle"])
        y -= 25

        # =========================
        # 📊 GRÁFICO FOB POR PRODUCTO
        # =========================
        # =========================
        # 📊 DATOS
        # =========================
        labels = [p["nombre"] for p in productos]
        values = [p["fob_total"] for p in productos]

        total = sum(values)
        porcentajes = [(v / total) * 100 for v in values]

        plt.figure(figsize=(10,6))

        bars = plt.barh(labels, values)

        # 🔥 TAMAÑOS DE TEXTO
        plt.yticks(fontsize=10, fontweight='bold')
        plt.xticks(fontsize=9)
        plt.xlabel("USD", fontsize=10, fontweight='bold')

        # 🔥 etiquetas sobre barras (CLAVE)
        for i, v in enumerate(values):
            plt.text(
                v,
                i,
                f" {v:,.0f} USD ({porcentajes[i]:.1f}%)",
                va='center',
                fontsize=10,
                fontweight='bold'  # 🔥 CLAVE
            )

        plt.tight_layout()

        # guardar imagen
        plt.savefig("grafico.png", dpi=300)
        plt.close()


        # 📍 POSICIÓN EN PDF
        if version == "Eyecandy":
            c.drawImage("grafico.png", 280, 320, width=323, height=185)

        # =========================
        # 📊 % PARTICIPACIÓN SOBRE FOB
        # =========================

        y_grafico = 270
        c.setFont(fuente, 11)
        c.drawString(280, y_grafico, t["porcentaje"] + ":")

        y_grafico -= 15

        for p in productos:
            c.setFont(fuente, 10)
            porcentaje = (p["fob_total"] / fob) * 100
            texto = f"• {p['nombre']}: {porcentaje:.1f}%"
    
            c.drawString(280, y_grafico, texto)
            y_grafico -= 12

        for p in productos:
            # Título producto
            c.setFont(fuente, 11)
            c.drawString(80, y, f"{p['codigo']} - {p['nombre']} ({p['uni']} unidad)")
            y -= 15

            # Datos producto
            c.setFont(fuente, 10)
            c.drawString(100, y, f"{t['fob']}: {p['fob_total']:,.2f} USD")
            y -= 13
            c.drawString(100, y, f"{t['flete']}: {p['flete']:,.2f} USD")
            y -= 13
            c.drawString(100, y, f"{t['seguro']}: {p['seguro']:,.2f} USD")
            y -= 13
            c.drawString(100, y, f"{t['costo_unitario']}: {p['costo_unitario']:,.2f} USD")

            # Espacio entre productos (MUY IMPORTANTE)
            y -= 22

        # =========================
        # 🥧 GRÁFICO RADIAL (% FOB)
        # =========================
        valores = [p["fob_total"] for p in productos]

        plt.figure(figsize=(3,3))

        plt.pie(
            valores,
            autopct='%1.1f%%',
            textprops={
                'fontsize':9,
                'fontweight':'bold'  # 🔥 CLAVE
            }
        )

        plt.title(
            f"FOB TOTAL\n{fob:,.0f} USD",
            fontsize=10,
            fontweight='bold'
        )

        plt.tight_layout()
        plt.savefig("pie.png", dpi=300)
        plt.close()

        if version == "Eyecandy":
            c.drawImage("pie.png", 458, 185, width=100, height=100)

        # =========================
        # 📝 OBSERVACIONES
        # =========================

        y_obs = 130  # 🔥 posición fija (ajustable fino)
        c.setFont(fuente, 11)
        c.drawString(80, y_obs, t["observaciones"] + ":")
        c.setFont(fuente, 10)
        c.drawString(80, y_obs - 15, observaciones)

        # =========================

        # 👉 SOLO UN SAVE
        c.save()

        st.success("✅ PDF generado correctamente")
