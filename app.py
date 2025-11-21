import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
from branca.element import Element

# ===================== CONFIG GLOBAL =====================
st.set_page_config(
    page_title="Polígono Vivo · Planificación de Reforestación",
    page_icon="🌱",
    layout="wide",
)

# ===================== ESTILOS CUSTOM =====================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100..900;1,100..900&display=swap');
    
    html, body, .stApp, .stApp * {
        font-family: 'Roboto', sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at top left, #e8f5e9 0, #f1f8e9 40%, #f9fbe7 100%);
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1b5e20;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        font-size: 1.0rem;
        color: #33691e;
        opacity: 0.9;
        margin-bottom: 1.2rem;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1b5e20 !important;
    }
    .kpi-card {
        background-color: #ffffffdd;
        padding: 0.8rem 1.2rem;
        border-radius: 0.9rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        border-left: 5px solid #66bb6a;
    }
    .kpi-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #558b2f;
    }
    .kpi-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2e7d32;
    }
    .kpi-caption {
        font-size: 0.75rem;
        color: #6d6d6d;
    }
    .stButton>button {
        background: linear-gradient(90deg, #388e3c, #66bb6a);
        border-radius: 999px;
        color: white;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2e7d32, #43a047);
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(56,142,60,0.35);
    }
    button[data-baseweb="tab"] {
        font-weight: 600;
        color: #33691e !important;
    }
    button[aria-selected="true"] {
        border-bottom: 3px solid #43a047 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================== DATOS SIMULADOS BASE =====================
species = [
    "AG_LEC", "AG_SAL", "AG_SCB", "AG_STR",
    "OP_CAN", "OP_ENG", "OP_ROB", "OP_STR",
    "PR_LAE", "YU_FIL"
]

# Mezcla de referencia (promedio de la zona)
expected_mix = {
    "AG_LEC": 0.0638,
    "AG_SAL": 0.2979,
    "AG_SCB": 0.0638,
    "AG_STR": 0.0638,
    "OP_CAN": 0.0745,
    "OP_ENG": 0.0578,
    "OP_ROB": 0.1109,
    "OP_STR": 0.0973,
    "PR_LAE": 0.1307,
    "YU_FIL": 0.0395,
}

# ===================== SIDEBAR =====================
with st.sidebar:
    # LOGO
    if os.path.exists("assets/logo_refo.png"):
        st.image("assets/logo_refo.png", use_container_width=True)
    st.markdown("### 🌱 Polígono Vivo")
    st.caption("Herramienta de apoyo para planear reforestación por polígono.")

    polygon = st.selectbox(
        "Selecciona polígono",
        ["Dominica–Charcas · P1", "Dominica–Charcas · P2", "Escenario ejemplo"],
    )

    nodes = st.slider(
        "Puntos de plantación (nodos)",
        min_value=100,
        max_value=700,
        value=625,
        step=25,
    )

    survival = st.slider(
        "Porcentaje de éxito esperado en la plantación",
        min_value=0.40,
        max_value=0.95,
        value=0.75,
        step=0.01,
    )

    st.markdown("---")
    st.markdown("#### Escenario de compra")
    costo_promedio = st.slider("Costo promedio por planta (MXN)", 10.0, 80.0, 35.0)

    st.markdown("---")
    lanzar = st.button("🔍 Generar plan de plantación")

# ===================== HEADER =====================
st.markdown(
    "<div class='main-title'>Polígono Vivo · Planificación de la reforestación</div>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class='subtitle'>
    Plataforma para apoyar decisiones de dónde y qué plantar, estimando mezclas de especies,
    número de plantas y costos aproximados por polígono.
    </div>
    """,
    unsafe_allow_html=True,
)

if lanzar:
    st.success(f"Plan de plantación generado para **{polygon}** con {nodes} puntos de plantación. 👇")

# ===================== KPIs =====================
total_plantas_esperadas = int(nodes * survival)
costo_total = total_plantas_esperadas * costo_promedio

col_k1, col_k2, col_k3, col_k4 = st.columns(4)

with col_k1:
    st.markdown(
        """
        <div class='kpi-card'>
            <div class='kpi-label'>Superficie de referencia</div>
            <div class='kpi-value'>75 ha</div>
            <div class='kpi-caption'>Línea Dominica–Charcas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_k2:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Puntos de plantación</div>
            <div class='kpi-value'>{nodes}</div>
            <div class='kpi-caption'>Nodos disponibles para plantar</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_k3:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Éxito esperado</div>
            <div class='kpi-value'>{int(survival*100)}%</div>
            <div class='kpi-caption'>Porcentaje de plantas que se espera sobrevivan</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_k4:
    st.markdown(
        f"""
        <div class='kpi-card'>
            <div class='kpi-label'>Costo estimado</div>
            <div class='kpi-value'>${costo_total:,.0f} MXN</div>
            <div class='kpi-caption'>≈ {total_plantas_esperadas} plantas nuevas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

# ===================== TABS PRINCIPALES =====================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🗺 Mapa & mezcla", "🌿 Especies", "📊 Escenarios", "🚚 Resumen logístico"]
)

# ---------- TAB 1: MAPA & MEZCLA ----------
with tab1:
    left, right = st.columns((1.3, 1.0))

    with left:
        st.subheader("Mapa del polígono y puntos de plantación")

        # Asignación simulada de especies a nodos según mezcla de referencia
        np.random.seed(42)
        species_assign = np.random.choice(
            species,
            size=nodes,
            p=np.array(list(expected_mix.values()))
        )

        # Centro de ejemplo (zona verde del país)
        center_lat, center_lon = 16.1, -90.8

        lats = center_lat + np.random.uniform(-0.02, 0.02, size=nodes)
        lons = center_lon + np.random.uniform(-0.02, 0.02, size=nodes)

        df_grid = pd.DataFrame({
            "lat": lats,
            "lon": lons,
            "Especie": species_assign,
        })

        species_colors = {
            "AG_LEC": "#1b5e20",
            "AG_SAL": "#66bb6a",
            "AG_SCB": "#2e7d32",
            "AG_STR": "#81c784",
            "OP_CAN": "#558b2f",
            "OP_ENG": "#9ccc65",
            "OP_ROB": "#33691e",
            "OP_STR": "#aed581",
            "PR_LAE": "#4caf50",
            "YU_FIL": "#8bc34a",
        }

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12,
        )

        # Añadir puntos al mapa
        for _, row in df_grid.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=3,
                color=species_colors.get(row["Especie"], "#2e7d32"),
                fill=True,
                fill_color=species_colors.get(row["Especie"], "#2e7d32"),
                fill_opacity=0.9,
                weight=0,
            ).add_to(m)

        # Leyenda de especies
        legend_items = ""
        for sp, color in species_colors.items():
            legend_items += f"""
            <div style="display:flex; align-items:center; margin-bottom:2px;">
                <span style="
                    display:inline-block;
                    width:12px;
                    height:12px;
                    border-radius:50%;
                    background:{color};
                    margin-right:6px;
                "></span>
                <span>{sp}</span>
            </div>
            """

        legend_html = f"""
        <div style="
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 9999;
            background-color: white;
            padding: 8px 12px;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0,0,0,0.3);
            font-size: 12px;
        ">
            <b>Especies</b>
            <br>
            {legend_items}
        </div>
        """

        m.get_root().html.add_child(Element(legend_html))

        st_folium(m, width="100%", height=450)

    with right:
        st.subheader("Composición por especie")

        comp = (
            df_grid["Especie"]
            .value_counts(normalize=True)
            .rename("Propuesta")
            .reset_index()
            .rename(columns={"index": "Especie"})
        )
        comp["Referencia zona"] = comp["Especie"].map(expected_mix)
        comp = comp.sort_values("Especie")

        fig_bar = px.bar(
            comp.melt(id_vars="Especie", value_vars=["Referencia zona", "Propuesta"]),
            x="Especie",
            y="value",
            color="variable",
            barmode="group",
            labels={"value": "Proporción", "variable": "Escenario"},
            height=450,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.caption(
            "La mezcla de referencia proviene de datos históricos de la zona. "
            "La mezcla propuesta es un ejemplo generado con los parámetros seleccionados."
        )

# ---------- TAB 2: ESPECIES ----------
with tab2:
    st.subheader("Especies y recomendaciones de uso")
    st.write(
        "Cada especie tiene un rol ecológico distinto. A continuación se muestran ejemplos "
        "de cómo pueden combinarse para mejorar sombra, captura de agua y diversidad."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Agaves & Yucca")

        if os.path.exists("assets/ag_salmiana.jpeg"):
            with st.expander("AG_SAL · Agave salmiana"):
                st.image("assets/ag_salmiana.jpeg", caption="Agave salmiana", use_container_width=True)
                st.markdown(
                    "- Alta capacidad de captación de agua.\n"
                    "- Conviene limitar su porcentaje para evitar competencia excesiva.\n"
                    "- Recomendable como base de la mezcla en zonas abiertas."
                )

        if os.path.exists("assets/ag_lechuguilla.jpg"):
            with st.expander("AG_LEC · Agave lechuguilla"):
                st.image("assets/ag_lechuguilla.jpg", use_container_width=True)
                st.markdown(
                    "- Planta más pequeña, ayuda a diversificar el paisaje.\n"
                    "- Buena opción para bordes y zonas con suelo delgado."
                )

        if os.path.exists("assets/yucca_filifera.jpg"):
            with st.expander("YU_FIL · Yucca filifera"):
                st.image("assets/yucca_filifera.jpg", use_container_width=True)
                st.markdown(
                    "- Estructura alta que genera sombra.\n"
                    "- Puede funcionar como planta nodriza para agaves y nopales."
                )

    with col_b:
        st.markdown("#### Opuntias & Prosopis")

        if os.path.exists("assets/op_robusta.jpeg"):
            with st.expander("OP_ROB · Opuntia robusta"):
                st.image("assets/op_robusta.jpeg", use_container_width=True)
                st.markdown(
                    "- Nopal robusto, útil como barrera viva.\n"
                    "- Aporta alimento y refugio para fauna."
                )

        if os.path.exists("assets/op_streptacantha.jpeg"):
            with st.expander("OP_STR · Opuntia streptacantha"):
                st.image("assets/op_streptacantha.jpeg", use_container_width=True)
                st.markdown(
                    "- Forma arborescente que agrega altura al sistema.\n"
                    "- Recomendable mezclarla con agaves y mezquites."
                )

        if os.path.exists("assets/prosopis_lae.jpg"):
            with st.expander("PR_LAE · Prosopis laevigata"):
                st.image("assets/prosopis_lae.jpg", use_container_width=True)
                st.markdown(
                    "- Árbol clave para generar sombra y mejorar suelo.\n"
                    "- Recomendable como estructura principal del polígono."
                )

# ---------- TAB 3: ESCENARIOS ----------
with tab3:
    st.subheader("Escenarios de plantas existentes por polígono")

    n_runs = st.slider("Número de escenarios a simular", 100, 5000, 1000, step=100)
    st.caption(
        "El sistema genera diferentes escenarios para reflejar la variación natural entre polígonos. "
        "En la versión completa, estos valores se alimentan de datos reales."
    )

    # Simulación simple para el demo
    total_plants = np.random.normal(loc=658, scale=40, size=n_runs).astype(int)
    total_plants = np.clip(total_plants, 450, 800)

    fig_hist = px.histogram(
        total_plants,
        nbins=30,
        labels={"value": "Plantas por polígono"},
        title="Distribución simulada de plantas existentes",
        height=400,
    )
    fig_hist.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown(
        f"**Promedio de plantas por polígono (simulado):** {np.mean(total_plants):.1f} · "
        f"**Desviación estándar aproximada:** {np.std(total_plants):.1f}"
    )

    st.info(
        "Estos resultados pueden utilizarse como referencia para mantenimiento y monitoreo, "
        "por ejemplo para definir metas de reposición de plantas en cada visita de campo."
    )

# ---------- TAB 4: LOGÍSTICA DE COMPRA ----------
with tab4:
    st.subheader("Resumen de plantas a comprar por especie")

    compras = []
    for sp in species:
        esperado = expected_mix[sp] * total_plantas_esperadas
        compras.append(
            {
                "Especie": sp,
                "Plantas estimadas a comprar": int(np.ceil(esperado)),
                "Costo estimado (MXN)": int(np.ceil(esperado) * costo_promedio),
            }
        )
    df_compras = pd.DataFrame(compras)

    st.dataframe(df_compras, use_container_width=True)

    st.markdown(
        f"**Total de plantas estimadas:** "
        f"{df_compras['Plantas estimadas a comprar'].sum():,} · "
        f"**Costo total aproximado:** "
        f"${df_compras['Costo estimado (MXN)'].sum():,} MXN"
    )

    st.caption(
        "Este cálculo sirve como apoyo para presupuestos y licitaciones. "
  
    )
