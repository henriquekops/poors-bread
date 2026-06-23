from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from tabs import tab_visao_geral, tab_curso_profissionalizante, tab_mercado_trabalho, tab_fluxo_entrada_saida

# 1. Page Configuration
st.set_page_config(
    page_title="Dashboard Pão dos Pobres",
    page_icon="🍞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styling & CSS injection for premium look
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0f516e, #006fa1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        font-size: 1rem;
        color: #88888b;
        margin-bottom: 1.5rem;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 15px;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        border-color: rgba(0, 111, 161, 0.4);
    }
    
    .kpi-title {
        font-size: 0.9rem;
        color: #88888b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 5px 0;
    }
    
    .kpi-trend {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 5px;
    }
    
    .trend-up {
        color: #006fa1;
    }
    
    .trend-down {
        color: #0f516e;
    }
    
    .trend-neutral {
        color: #88888b;
    }
    
    /* Custom info box */
    .info-box {
        background: rgba(15, 81, 110, 0.05);
        border-left: 4px solid #0f516e;
        border-radius: 4px;
        padding: 15px;
        margin: 20px 0;
    }
    
    .info-box-title {
        font-weight: 600;
        color: #0f516e;
        margin-bottom: 5px;
    }
    
    .info-box-content {
        font-size: 0.9rem;
        color: #555555;
    }
    
    /* Support dark mode color for info box text in Streamlit */
    @media (prefers-color-scheme: dark) {
        .info-box-content {
            color: #dddddd;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Render KPI
def render_kpi(title, value, trend=None, trend_direction="up"):
    trend_html = ""
    if trend is not None:
        if trend_direction == "up":
            trend_class = "trend-up"
            arrow = "▲"
        elif trend_direction == "down":
            trend_class = "trend-down"
            arrow = "▼"
        else:
            trend_class = "trend-neutral"
            arrow = "•"
        trend_html = f'<div class="kpi-trend {trend_class}">{arrow} {trend}</div>'
    
    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {trend_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# Helper function to customize Plotly Layout
def customize_fig(fig, hovermode="x unified"):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Outfit",
        hovermode=hovermode,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, b=40, l=40, r=40),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.15)",
        linecolor="rgba(128, 128, 128, 0.2)"
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.15)",
        linecolor="rgba(128, 128, 128, 0.2)"
    )
    return fig

# 3. Data Loading
output_path = f"{Path(__file__).parent.parent.parent}/data/output"
df = pd.read_csv(f"{output_path}/processed.csv")

# Standard month ordering
month_order = [
    "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
    "JUL", "AGO", "SET", "OUT", "NOV", "DEZ",
]
month_num = {
    "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06",
    "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
}

df["mes_num"] = df["mes"].map(month_num)
df["data"] = pd.to_datetime(df["ano"].astype(str) + "-" + df["mes_num"] + "-01")
df = df.sort_values("data")

# 4. Sidebar Configuration
logo_path = Path(__file__).parent / "assets" / "dashboard_logo.png"
if logo_path.exists():
    st.sidebar.image(str(logo_path), width='stretch')

st.sidebar.markdown("### Filtros Globais")

years = sorted(df["ano"].unique())
selected_years = st.sidebar.slider(
    "Intervalo de Anos",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years))),
    step=1
)

# Apply global filter
df_filtered = df[(df["ano"] >= selected_years[0]) & (df["ano"] <= selected_years[1])].copy()

# Sidebar Info
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Fundação Pão dos Pobres**  
    LEM (Levantamento Estatístico Mensal)      
    """
)

# 6. Tab layout
def page_visao_geral():
    tab_visao_geral.render(df_filtered, selected_years, render_kpi, customize_fig)

def page_curso_profissionalizante():
    tab_curso_profissionalizante.render(df_filtered, render_kpi, customize_fig)

def page_mercado_trabalho():
    tab_mercado_trabalho.render(df_filtered, render_kpi, customize_fig)

def page_fluxo_entrada_saida():
    tab_fluxo_entrada_saida.render(df_filtered, month_order, render_kpi, customize_fig)

pg = st.navigation([
    st.Page(page_visao_geral, title="Visão Geral"),
    st.Page(page_curso_profissionalizante, title="Curso Profissionalizante"),
    st.Page(page_mercado_trabalho, title="Mercado de Trabalho"),
    st.Page(page_fluxo_entrada_saida, title="Fluxo de Entrada/Saída")
], position="top")
pg.run()
