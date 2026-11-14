
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import calculos as cal

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


# =====================================================
# GENERADOR DE INFORME PDF
# =====================================================

def generar_pdf(datos):

    memoria = BytesIO()

    documento = SimpleDocTemplate(
        memoria,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloJR",
        parent=estilos["Title"],
        fontSize=21,
        textColor=colors.HexColor("#123456"),
        alignment=TA_CENTER,
        spaceAfter=10
    )

    subtitulo = ParagraphStyle(
        "SubtituloJR",
        parent=estilos["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2878B5"),
        fontSize=10,
        spaceAfter=15
    )

    seccion = ParagraphStyle(
        "SeccionJR",
        parent=estilos["Heading2"],
        textColor=colors.HexColor("#176B9B"),
        fontSize=12,
        spaceBefore=14,
        spaceAfter=8
    )

    contenido = []

    contenido.append(
        Paragraph("HEAT EXCHANGERS JR", titulo)
    )

    contenido.append(
        Paragraph(
            "INFORME TECNICO DE INTERCAMBIADOR DE DOBLE TUBO",
            subtitulo
        )
    )

    contenido.append(
        Paragraph(
            "Fecha de generacion: "
            + datetime.now().strftime("%d/%m/%Y %H:%M"),
            estilos["Normal"]
        )
    )

    contenido.append(Spacer(1, 15))

    def agregar_tabla(nombre, filas):

        contenido.append(Paragraph(nombre, seccion))

        tabla = Table(
            filas,
            colWidths=[8*cm, 7*cm],
            repeatRows=1
        )

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#123456")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, -1),
             colors.HexColor("#EAF2F8")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))

        contenido.append(tabla)
        contenido.append(Spacer(1, 10))

    agregar_tabla("1. DATOS DE OPERACION", [
        ["Parametro", "Valor"],
        ["Caudal caliente", f"{datos['mh']:.3f} kg/s"],
        ["Caudal frio", f"{datos['mc']:.3f} kg/s"],
        ["Temperatura entrada caliente", f"{datos['Thi']:.2f} °C"],
        ["Temperatura salida caliente", f"{datos['Tho']:.2f} °C"],
        ["Temperatura entrada fria", f"{datos['Tci']:.2f} °C"],
        ["Temperatura salida fria", f"{datos['Tco']:.2f} °C"],
        ["Fluido caliente seleccionado", datos["fluido_caliente"]],
        ["Fluido frio seleccionado", datos["fluido_frio"]],
        ["Material del tubo interior", datos["material"]],
        ["Conductividad de pared", f"{datos['kw']:.2f} W/m K"],
        ["Diametro interior", f"{datos['Di']:.4f} m"],
        ["Diametro exterior tubo interno", f"{datos['Do']:.4f} m"],
        ["Diametro tubo exterior", f"{datos['D2']:.4f} m"],
    ])

    agregar_tabla("2. BALANCE ENERGETICO", [
        ["Parametro", "Resultado"],
        ["Carga termica", f"{datos['Q']/1000:.3f} kW"],
        ["Diferencia media logaritmica", f"{datos['LMTD']:.3f} K"],
    ])

    agregar_tabla("3. ANALISIS HIDRAULICO", [
        ["Parametro", "Resultado"],
        ["Velocidad caliente", f"{datos['vh']:.4f} m/s"],
        ["Velocidad fria", f"{datos['vc']:.4f} m/s"],
        ["Reynolds caliente", f"{datos['Reh']:.0f}"],
        ["Reynolds frio", f"{datos['Rec']:.0f}"],
        ["Prandtl caliente", f"{datos['Prh']:.3f}"],
        ["Prandtl frio", f"{datos['Prc']:.3f}"],
    ])

    agregar_tabla("4. TRANSFERENCIA DE CALOR", [
        ["Parametro", "Resultado"],
        ["Nusselt caliente", f"{datos['Nuh']:.2f}"],
        ["Nusselt frio", f"{datos['Nuc']:.2f}"],
        ["Coeficiente convectivo caliente",
         f"{datos['hi']:.2f} W/m2 K"],
        ["Coeficiente convectivo frio",
         f"{datos['ho']:.2f} W/m2 K"],
        ["Coeficiente global U",
         f"{datos['U']:.2f} W/m2 K"],
        ["Area requerida", f"{datos['A']:.4f} m2"],
        ["Longitud estimada", f"{datos['L']:.3f} m"],
    ])

    agregar_tabla("5. CAIDA DE PRESION Y BOMBEO", [
        ["Parametro", "Resultado"],
        ["Factor de friccion caliente", f"{datos['fh']:.5f}"],
        ["Factor de friccion frio", f"{datos['fc']:.5f}"],
        ["Caida de presion caliente",
         f"{datos['deltaP_h']/1000:.3f} kPa"],
        ["Caida de presion fria",
         f"{datos['deltaP_c']/1000:.3f} kPa"],
        ["Potencia hidraulica caliente",
         f"{datos['potencia_h']:.3f} W"],
        ["Potencia hidraulica fria",
         f"{datos['potencia_c']:.3f} W"],
        ["Potencia hidraulica total",
         f"{datos['potencia_h'] + datos['potencia_c']:.3f} W"],
    ])

    contenido.append(
        Paragraph("6. OBSERVACIONES TECNICAS", seccion)
    )

    contenido.append(
        Paragraph(
            "Este informe presenta un dimensionamiento preliminar "
            "de un intercambiador de calor de doble tubo en "
            "contracorriente. Se consideran propiedades constantes "
            "y correlaciones aproximadas de transferencia de calor "
            "y friccion. Las perdidas localizadas y la eficiencia "
            "real de bombeo no estan incluidas. Se recomienda "
            "validar las correlaciones utilizadas para el espacio "
            "anular antes de adoptar un diseno definitivo.",
            estilos["BodyText"]
        )
    )

    contenido.append(Spacer(1, 20))

    contenido.append(
        Paragraph(
            "HEAT EXCHANGERS JR | SIMULADOR DE INGENIERIA",
            subtitulo
        )
    )

    documento.build(contenido)

    memoria.seek(0)

    return memoria.getvalue()

# =====================================================
# CONFIGURACION
# =====================================================

st.set_page_config(
    page_title="HEAT EXCHANGERS JR",
    page_icon="🌡️",
    layout="wide"
)


# =====================================================
# ESTILO VISUAL
# =====================================================

st.markdown("""
<style>
.stApp {
    background: #08111f;
    color: #edf4ff;
}
[data-testid="stSidebar"] {
    background: #101d30;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #eaf4ff !important;
}
.metric-card {
    background: linear-gradient(135deg,#142944,#0d1b2d);
    border: 1px solid #23476b;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 10px;
}
.metric-label {
    color: #91a9c4;
    font-size: 13px;
}
.metric-value {
    color: #35b9ff;
    font-size: 27px;
    font-weight: bold;
}
.metric-unit {
    color: #c5d5e8;
    font-size: 12px;
}
.length-card {
    background: linear-gradient(135deg,#123d5c,#10243a);
    border: 2px solid #35b9ff;
    border-radius: 12px;
    padding: 12px 16px;
    text-align: center;
    min-height: 92px;
}
.length-label {
    color: #b7d9f2;
    font-size: 13px;
}
.length-value {
    color: #35b9ff;
    font-size: 30px;
    font-weight: 800;
}
.length-unit {
    color: #d5e7f7;
    font-size: 12px;
}
.section {
    color: #35b9ff;
    font-weight: bold;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# ENCABEZADO
# =====================================================

st.markdown("""
# 🌡️ HEAT EXCHANGERS <span style='color:#35b9ff'>JR</span>
### DOUBLE PIPE HEAT EXCHANGER · ENGINEERING SIMULATOR
""", unsafe_allow_html=True)

st.caption(
    "THERMAL DESIGN | HYDRAULIC ANALYSIS | PERFORMANCE"
)

st.caption(
    f"Fluido caliente: {st.session_state.get('fluido_caliente', 'Agua')}  ·  "
    f"Fluido frío: {st.session_state.get('fluido_frio', 'Agua')}  ·  "
    f"Material: {st.session_state.get('material_pared', 'Acero inoxidable')}"
)


# =====================================================
# ENTRADAS
# =====================================================

st.sidebar.title("⚙️ Datos de operación")

# Valores iniciales para los controles. Las propiedades se pueden editar.
st.session_state.setdefault("fluido_caliente", "Agua")
st.session_state.setdefault("fluido_frio", "Agua")
st.session_state.setdefault("material_pared", "Acero inoxidable")

for clave, valor in {
    "mh": 0.50, "Thi": 90.0, "Tho": 60.0, "cp_h": 4180.0,
    "mc": 0.60, "Tci": 20.0, "cp_c": 4180.0,
    "Di": 0.020, "Do": 0.025, "D2": 0.050, "kw": 16.0,
    "rho_h": 995.0, "rho_c": 995.0,
    "mu_h": 0.0008, "mu_c": 0.0008,
    "k_h": 0.62, "k_c": 0.62
}.items():
    st.session_state.setdefault(clave, valor)


def actualizar_propiedades_fluido(lado):
    """Carga las propiedades de referencia del fluido elegido."""
    nombre_widget = "fluido_caliente" if lado == "h" else "fluido_frio"
    propiedades = cal.obtener_propiedades_fluido(
        st.session_state[nombre_widget]
    )
    st.session_state[f"cp_{lado}"] = float(propiedades["cp"])
    st.session_state[f"rho_{lado}"] = float(propiedades["rho"])
    st.session_state[f"mu_{lado}"] = float(propiedades["mu"])
    st.session_state[f"k_{lado}"] = float(propiedades["k"])


def actualizar_material():
    """Actualiza la conductividad de pared según el material elegido."""
    st.session_state["kw"] = float(
        cal.obtener_conductividad_material(
            st.session_state["material_pared"]
        )
    )


st.sidebar.subheader("Fluido caliente")

st.sidebar.selectbox(
    "Tipo de fluido caliente",
    options=list(cal.FLUIDOS.keys()),
    key="fluido_caliente",
    on_change=actualizar_propiedades_fluido,
    args=("h",),
    help="Selecciona el fluido que circula por el tubo interior."
)

mh = st.sidebar.number_input(
    "Caudal caliente (kg/s)", min_value=0.01, key="mh",
    help="Masa de fluido caliente que circula por segundo."
)
Thi = st.sidebar.number_input(
    "Temperatura entrada caliente (°C)", key="Thi",
    help="Temperatura del fluido caliente al entrar al intercambiador."
)
Tho = st.sidebar.number_input(
    "Temperatura salida caliente (°C)", key="Tho",
    help="Temperatura deseada o medida del fluido caliente a la salida."
)
Cph = st.sidebar.number_input(
    "Calor específico caliente (J/kg·K)", key="cp_h",
    help="Energía necesaria para elevar 1 K la temperatura de 1 kg de fluido."
)

st.sidebar.divider()
st.sidebar.subheader("Fluido frío")

st.sidebar.selectbox(
    "Tipo de fluido frío",
    options=list(cal.FLUIDOS.keys()),
    key="fluido_frio",
    on_change=actualizar_propiedades_fluido,
    args=("c",),
    help="Selecciona el fluido que circula por el espacio anular."
)

mc = st.sidebar.number_input(
    "Caudal frío (kg/s)", min_value=0.01, key="mc",
    help="Masa de fluido frío que circula por segundo."
)
Tci = st.sidebar.number_input(
    "Temperatura entrada fría (°C)", key="Tci",
    help="Temperatura del fluido frío antes de recibir calor."
)
Cpc = st.sidebar.number_input(
    "Calor específico frío (J/kg·K)", key="cp_c",
    help="Energía necesaria para elevar 1 K la temperatura de 1 kg de fluido."
)

st.sidebar.divider()
st.sidebar.subheader("Geometría")

Di = st.sidebar.number_input(
    "Diámetro interior (m)", key="Di", format="%.4f",
    help="Diámetro interno del tubo por donde circula el fluido caliente."
)
Do = st.sidebar.number_input(
    "Diámetro exterior tubo interno (m)", key="Do", format="%.4f",
    help="Diámetro externo del tubo interior; define el área de transferencia."
)
D2 = st.sidebar.number_input(
    "Diámetro interior tubo exterior (m)", key="D2", format="%.4f",
    help="Diámetro interno del tubo exterior que contiene el espacio anular."
)

st.sidebar.divider()
st.sidebar.subheader("Material de la pared")

st.sidebar.selectbox(
    "Material del tubo interior",
    options=list(cal.MATERIALES.keys()),
    key="material_pared",
    on_change=actualizar_material,
    help="El material seleccionado determina la conductividad térmica de la pared."
)
kw = st.sidebar.number_input(
    "Conductividad de pared (W/m·K)", key="kw",
    help="Conductividad térmica del material. Se actualiza con el material, pero puedes editarla."
)

st.sidebar.divider()
st.sidebar.subheader("Propiedades de los fluidos")
st.sidebar.caption(
    "Valores de referencia aproximados. Verifica la temperatura y composición; "
    "puedes ajustar cada propiedad manualmente."
)

rho_h = st.sidebar.number_input(
    "Densidad caliente (kg/m³)", key="rho_h",
    help="Masa por unidad de volumen del fluido caliente."
)
rho_c = st.sidebar.number_input(
    "Densidad fría (kg/m³)", key="rho_c",
    help="Masa por unidad de volumen del fluido frío."
)
mu_h = st.sidebar.number_input(
    "Viscosidad caliente (Pa·s)", key="mu_h", format="%.6f",
    help="Resistencia del fluido caliente a fluir."
)
mu_c = st.sidebar.number_input(
    "Viscosidad fría (Pa·s)", key="mu_c", format="%.6f",
    help="Resistencia del fluido frío a fluir."
)
k_h = st.sidebar.number_input(
    "Conductividad caliente (W/m·K)", key="k_h",
    help="Capacidad del fluido caliente para conducir energía térmica."
)
k_c = st.sidebar.number_input(
    "Conductividad fría (W/m·K)", key="k_c",
    help="Capacidad del fluido frío para conducir energía térmica."
)

# =====================================================
# CALCULOS
# =====================================================

try:

    if Thi <= Tho:
        raise ValueError(
            "La entrada caliente debe superar la salida caliente."
        )

    balance = cal.balance_energetico(
        mh, Cph, Thi, Tho, mc, Cpc, Tci
    )

    Q = balance["Q"]
    Tco = balance["Tco"]

    LMTD = cal.diferencia_media_logaritmica(
        Thi, Tho, Tci, Tco
    )

    geo = cal.geometria_doble_tubo(
        Di, Do, D2
    )

    Ai = geo["area_interior"]
    Aa = geo["area_anular"]
    Dh = geo["diametro_hidraulico"]

    vh = cal.velocidad_fluido(
        mh, rho_h, Ai
    )

    vc = cal.velocidad_fluido(
        mc, rho_c, Aa
    )

    Reh = cal.numero_reynolds(
        rho_h, vh, Di, mu_h
    )

    Rec = cal.numero_reynolds(
        rho_c, vc, Dh, mu_c
    )

    Prh = cal.numero_prandtl(
        Cph, mu_h, k_h
    )

    Prc = cal.numero_prandtl(
        Cpc, mu_c, k_c
    )

    Nuh = cal.numero_nusselt(Reh, Prh)

    Nuc = cal.numero_nusselt(Rec, Prc)

    hi = Nuh * k_h / Di
    ho = Nuc * k_c / Dh

    U = cal.coeficiente_global_exterior(
        hi, ho, Di, Do, kw
    )

    A = cal.area_transferencia(
        Q, U, LMTD
    )

    L = cal.longitud_intercambiador(
        A, Do
    )

    # CAIDA DE PRESION

    fh = cal.factor_friccion_blasius(Reh)
    fc = cal.factor_friccion_blasius(Rec)

    deltaP_h = cal.caida_presion(
        fh, L, Di, rho_h, vh
    )

    deltaP_c = cal.caida_presion(
        fc, L, Dh, rho_c, vc
    )

    potencia_h = cal.potencia_hidraulica(
        deltaP_h, mh, rho_h
    )

    potencia_c = cal.potencia_hidraulica(
        deltaP_c, mc, rho_c
    )

except Exception as error:

    st.error(f"Error en los cálculos: {error}")
    st.stop()


# =====================================================
# RESULTADOS PRINCIPALES
# =====================================================

st.markdown(
    '<p class="section">01 / THERMAL PERFORMANCE</p>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

metricas = [
    (c1, "HEAT DUTY", f"{Q/1000:.2f}", "kW · Carga térmica"),
    (c2, "COLD OUTLET", f"{Tco:.2f}", "°C · Salida fluido frío"),
    (c3, "LMTD", f"{LMTD:.2f}", "K · Contracorriente"),
    (c4, "GLOBAL U", f"{U:.1f}", "W/m²·K · Coeficiente global")
]

for col, label, value, unit in metricas:

    with col:

        st.markdown(f"""
        <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# DIAGRAMA Y GRAFICA
# =====================================================

st.divider()

st.markdown(
    '<p class="section">02 / HEAT EXCHANGER CONFIGURATION</p>',
    unsafe_allow_html=True
)

left, right = st.columns([1.15, 1])

with left:

    st.subheader("Esquema de operación")

    st.markdown(f"""
    <div style="background:#101d30;padding:22px;border-radius:14px;border:1px solid #23476b;">
    <div style="color:#ff765f;font-weight:bold;">HOT FLUID →</div>
    <div style="color:white;">Entrada: {Thi:.1f} °C</div>
    <div style="height:8px;background:#ff765f;border-radius:8px;margin:8px 0;"></div>
    <div style="text-align:center;color:#b9cce2;">TUBO INTERIOR</div>
    <div style="text-align:right;color:#ff765f;">Salida: {Tho:.1f} °C</div>
    <br>
    <div style="color:#35b9ff;font-weight:bold;text-align:right;">← COLD FLUID</div>
    <div style="text-align:right;color:white;">Entrada: {Tci:.1f} °C</div>
    <div style="height:8px;background:#35b9ff;border-radius:8px;margin:8px 0;"></div>
    <div style="text-align:center;color:#b9cce2;">ESPACIO ANULAR</div>
    <div style="color:#35b9ff;">Salida: {Tco:.1f} °C</div>
    <div style="text-align:center;color:#9db2ca;margin-top:15px;">CONTRACORRIENTE</div>
    </div>
    """, unsafe_allow_html=True)

with right:

    st.subheader("Perfil de temperaturas")

    x = np.linspace(0, 1, 50)

    hot = Thi - x * (Thi - Tho)
    cold = Tco - x * (Tco - Tci)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=hot,
        name="Fluido caliente",
        line=dict(color="#ff765f", width=4)
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=cold,
        name="Fluido frío",
        line=dict(color="#35b9ff", width=4)
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#101d30",
        plot_bgcolor="#101d30",
        xaxis_title="Longitud relativa",
        yaxis_title="Temperatura (°C)",
        height=340,
        margin=dict(l=20, r=20, t=35, b=20)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =====================================================
# ANALISIS HIDRAULICO
# =====================================================

st.divider()

st.markdown(
    '<p class="section">03 / HYDRAULIC ANALYSIS</p>',
    unsafe_allow_html=True
)

h1, h2 = st.columns(2)

with h1:

    st.subheader("Fluido caliente · Tubo interior")

    st.metric("Velocidad", f"{vh:.4f} m/s")
    st.metric("Reynolds", f"{Reh:,.0f}")
    st.metric("Prandtl", f"{Prh:.3f}")
    st.metric("Nusselt", f"{Nuh:.2f}")
    st.metric("Coeficiente convectivo", f"{hi:.1f} W/m²·K")

with h2:

    st.subheader("Fluido frío · Espacio anular")

    st.metric("Velocidad", f"{vc:.4f} m/s")
    st.metric("Reynolds", f"{Rec:,.0f}")
    st.metric("Prandtl", f"{Prc:.3f}")
    st.metric("Nusselt", f"{Nuc:.2f}")
    st.metric("Coeficiente convectivo", f"{ho:.1f} W/m²·K")


def regimen(Re):

    if Re < 2300:
        return "Laminar"

    elif Re < 4000:
        return "Transicional"

    return "Turbulento"


st.write(f"Régimen caliente: **{regimen(Reh)}**")
st.write(f"Régimen frío: **{regimen(Rec)}**")


# =====================================================
# DIMENSIONAMIENTO
# =====================================================

st.divider()

st.markdown(
    '<p class="section">04 / THERMAL SIZING</p>',
    unsafe_allow_html=True
)

d1, d2, d3 = st.columns(3)

d1.metric("Área requerida", f"{A:.3f} m²")
with d2:
    st.markdown(f"""
    <div class="length-card">
        <div class="length-label">LONGITUD ESTIMADA</div>
        <div class="length-value">{L:.2f}</div>
        <div class="length-unit">metros · longitud preliminar del tubo</div>
    </div>
    """, unsafe_allow_html=True)
d3.metric("Diámetro hidráulico anular", f"{Dh:.4f} m")

st.caption(
    "La longitud estimada se calcula a partir del área exterior requerida "
    "y del diámetro exterior del tubo interior. Es un resultado preliminar."
)

# =====================================================
# PRESION Y BOMBEO
# =====================================================

st.divider()

st.markdown(
    '<p class="section">05 / PRESSURE DROP & PUMPING</p>',
    unsafe_allow_html=True
)

p1, p2 = st.columns(2)

with p1:

    st.subheader("Fluido caliente")

    st.metric("Factor de fricción", f"{fh:.5f}")
    st.metric("Caída de presión", f"{deltaP_h/1000:.2f} kPa")
    st.metric("Potencia hidráulica", f"{potencia_h:.2f} W")

with p2:

    st.subheader("Fluido frío")

    st.metric("Factor de fricción", f"{fc:.5f}")
    st.metric("Caída de presión", f"{deltaP_c/1000:.2f} kPa")
    st.metric("Potencia hidráulica", f"{potencia_c:.2f} W")

st.markdown("### Resumen de bombeo")

st.metric(
    "Potencia hidráulica total",
    f"{potencia_h + potencia_c:.2f} W"
)


# =====================================================
# INFORME TECNICO PDF
# =====================================================

st.divider()

st.markdown(
    '<p class="section">06 / TECHNICAL REPORT</p>',
    unsafe_allow_html=True
)

st.write(
    "Genera un informe técnico con los datos y resultados "
    "actuales del intercambiador."
)

datos_informe = {
    "fluido_caliente": st.session_state["fluido_caliente"],
    "fluido_frio": st.session_state["fluido_frio"],
    "material": st.session_state["material_pared"],
    "kw": kw,
    "mh": mh,
    "mc": mc,
    "Thi": Thi,
    "Tho": Tho,
    "Tci": Tci,
    "Tco": Tco,
    "Di": Di,
    "Do": Do,
    "D2": D2,
    "Q": Q,
    "LMTD": LMTD,
    "vh": vh,
    "vc": vc,
    "Reh": Reh,
    "Rec": Rec,
    "Prh": Prh,
    "Prc": Prc,
    "Nuh": Nuh,
    "Nuc": Nuc,
    "hi": hi,
    "ho": ho,
    "U": U,
    "A": A,
    "L": L,
    "fh": fh,
    "fc": fc,
    "deltaP_h": deltaP_h,
    "deltaP_c": deltaP_c,
    "potencia_h": potencia_h,
    "potencia_c": potencia_c
}

try:

    pdf_bytes = generar_pdf(datos_informe)

    st.download_button(
        label="📄 GENERAR Y DESCARGAR INFORME PDF",
        data=pdf_bytes,
        file_name="Informe_HEAT_EXCHANGERS_JR.pdf",
        mime="application/pdf",
        use_container_width=True
    )

except Exception as error:

    st.error(f"No se pudo generar el PDF: {error}")


# =====================================================
# OBSERVACIONES
# =====================================================

st.info(
    "Dimensionamiento preliminar. Se utilizan propiedades "
    "constantes y la correlación de Dittus-Boelter como "
    "aproximación. Las correlaciones de transferencia de calor "
    "y fricción en el espacio anular deben validarse para "
    "un diseño definitivo. Las pérdidas localizadas no están incluidas."
)

st.caption(
    "HEAT EXCHANGERS JR · Versión 0.5 · "
    "Simulador térmico e hidráulico."
)
