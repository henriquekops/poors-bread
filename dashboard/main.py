from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Dashboard Pão dos Pobres",
    page_icon="🍞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Styling & CSS injection for premium look (using logo palette #0f516e and #006fa1)
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

# Helper function to render KPI
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
output_path = f"{Path(__file__).parent.parent}/data/output"
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
logo_path = Path(__file__).parent.parent / "assets" / "dashboard_logo.png"
if logo_path.exists():
    st.sidebar.image(str(logo_path), use_container_width=True)

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

# 5. Header Title
st.markdown('<div class="main-title">Fundação Pão dos Pobres</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Análise de Métricas Operacionais e Indicadores de Impacto Social</div>', unsafe_allow_html=True)

# 6. Tab layout
tab1, tab2, tab3, tab4 = st.tabs([
    "Visão Geral", 
    "Curso Profissionalizante", 
    "Mercado de Trabalho", 
    "Fluxo de Entrada/Saída"
])

# ==========================================
# TAB 1: VISÃO GERAL
# ==========================================
with tab1:
    st.markdown("### Análise Descritiva Geral")
    
    # Overview metrics
    total_val = df_filtered["valor"].sum()
    unique_types = df_filtered["tipo"].nunique()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi("Volume Total de Atendimentos", f"{total_val:,.0f}", f"Anos: {selected_years[0]}-{selected_years[1]}", "neutral")
    with col2:
        # Find area with most service count
        top_area = df_filtered.groupby("area")["valor"].sum().idxmax()
        area_labels_full = {
            "desdobramentos tecnicos": "Desdobramentos Técnicos",
            "educacao": "Educação",
            "profissionalizacao": "Profissionalização",
            "saude": "Saúde"
        }
        render_kpi("Área com Maior Demanda", area_labels_full.get(top_area, top_area), "Volume total acumulado", "up")
    with col3:
        render_kpi("Categorias Operacionais Monitoradas", f"{unique_types}", "Indicadores distintos", "neutral")
        
    st.markdown("---")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        df_area_ts = df_filtered.groupby(["data", "area"])["valor"].sum().reset_index()
        fig_area_ts = px.line(
            df_area_ts,
            x="data",
            y="valor",
            color="area",
            color_discrete_map={
                "desdobramentos tecnicos": "#0f516e",
                "educacao": "#006fa1",
                "profissionalizacao": "#3fa3d1",
                "saude": "#82c3e2"
            },
            labels={"data": "Data", "valor": "Total de Atendimentos", "area": "Área"},
            title="Evolução Temporal dos Atendimentos por Área"
        )
        # Relabel legend traces
        fig_area_ts.for_each_trace(lambda t: t.update(name=area_labels_full.get(t.name, t.name)))
        fig_area_ts = customize_fig(fig_area_ts)
        st.plotly_chart(fig_area_ts, use_container_width=True)
        
    with c2:
        df_area_pie = df_filtered.groupby("area")["valor"].sum().reset_index()
        df_area_pie["Area Label"] = df_area_pie["area"].map(area_labels_full)
        fig_pie = px.pie(
            df_area_pie,
            values="valor",
            names="Area Label",
            color="Area Label",
            color_discrete_map={
                "Desdobramentos Técnicos": "#0f516e",
                "Educação": "#006fa1",
                "Profissionalização": "#3fa3d1",
                "Saúde": "#82c3e2"
            },
            hole=0.4,
            title="Proporção Acumulada de Atendimentos"
        )
        fig_pie = customize_fig(fig_pie, hovermode=None)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    
    # Detailing section
    st.markdown("### Detalhamento por Área")
    selected_area = st.selectbox(
        "Selecione uma Área de Atendimento para detalhar categorias:",
        options=["desdobramentos tecnicos", "educacao", "profissionalizacao", "saude"],
        format_func=lambda x: area_labels_full.get(x, x)
    )
    
    df_detail = df_filtered[df_filtered["area"] == selected_area].copy()
    
    df_cat = df_detail.groupby(["tipo", "status"])["valor"].sum().reset_index()
    df_cat["Categoria"] = df_cat.apply(
        lambda r: f"{r['tipo']} ({r['status']})" if r["status"] != "none" else r["tipo"],
        axis=1
    )
    df_cat = df_cat.sort_values("valor", ascending=True)
    
    fig_cat = px.bar(
        df_cat,
        x="valor",
        y="Categoria",
        orientation="h",
        labels={"valor": "Total de Atendimentos", "Categoria": "Categoria / Status"},
        title=f"Distribuição de Atendimentos em {area_labels_full[selected_area]}",
        color_discrete_sequence=["#006fa1"]
    )
    fig_cat = customize_fig(fig_cat, hovermode="y unified")
    st.plotly_chart(fig_cat, use_container_width=True)


# ==========================================
# TAB 2: CURSO PROFISSIONALIZANTE
# ==========================================
with tab2:
    st.markdown("### Pergunta 1: Taxa de conversão nos cursos profissionalizantes?")
    st.markdown("*Dentre os adolescentes encaminhados para cursos profissionalizantes, quantos foram efetivamente inseridos?*")
    
    df_course = df_filtered[
        (df_filtered["area"] == "profissionalizacao") & 
        (df_filtered["tipo"].str.contains("curso profissionalizante", case=False))
    ].copy()
    
    df_course_pivot = df_course.pivot_table(
        index="data",
        columns="tipo",
        values="valor",
        aggfunc="sum"
    ).reset_index()
    
    col_enc = "ENCAMINHADOS para curso profissionalizante"
    col_ins = "INSERIDOS em curso profissionalizante"
    
    # Check column presence
    if col_enc not in df_course_pivot.columns:
        df_course_pivot[col_enc] = 0.0
    if col_ins not in df_course_pivot.columns:
        df_course_pivot[col_ins] = 0.0
        
    df_course_pivot = df_course_pivot.fillna(0.0)
    
    total_enc = df_course_pivot[col_enc].sum()
    total_ins = df_course_pivot[col_ins].sum()
    conv_rate = (total_ins / total_enc * 100) if total_enc > 0 else 0.0
    
    # Render Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        render_kpi("Encaminhados para Cursos", f"{total_enc:,.0f}", "Jovens indicados", "neutral")
    with m2:
        render_kpi("Efetivamente Inseridos", f"{total_ins:,.0f}", "Jovens matriculados", "up")
    with m3:
        render_kpi("Taxa de Conversão Média", f"{conv_rate:.1f}%", "Inserções / Encaminhamentos", "up" if conv_rate >= 50 else "neutral")
        
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_course_trend = px.line(
            df_course_pivot,
            x="data",
            y=[col_enc, col_ins],
            labels={"data": "Data", "value": "Quantidade", "variable": "Indicador"},
            title="Evolução de Encaminhamentos vs. Inserções em Cursos",
            color_discrete_map={
                col_enc: "#0f516e",
                col_ins: "#006fa1"
            }
        )
        new_names = {col_enc: "Encaminhados", col_ins: "Inseridos"}
        fig_course_trend.for_each_trace(lambda t: t.update(name=new_names.get(t.name, t.name)))
        fig_course_trend = customize_fig(fig_course_trend)
        st.plotly_chart(fig_course_trend, use_container_width=True)
        
    with c2:
        df_course_pivot["Taxa de Conversão (%)"] = (df_course_pivot[col_ins] / df_course_pivot[col_enc] * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        fig_course_conv = px.bar(
            df_course_pivot,
            x="data",
            y="Taxa de Conversão (%)",
            title="Taxa de Conversão Mensal (%)",
            color_discrete_sequence=["#006fa1"]
        )
        fig_course_conv = customize_fig(fig_course_conv)
        st.plotly_chart(fig_course_conv, use_container_width=True)
        
    st.markdown(
        """
        <div class="info-box">
            <div class="info-box-title"> Contextualização Técnica e Análise do Efeito Latência</div>
            <div class="info-box-content">
                A taxa de conversão em alguns períodos mensais pode demonstrar valores atípicos ou superiores a 100%. 
                Este comportamento deve-se ao <strong>efeito de latência temporal</strong>: a indicação de um jovem a um curso profissionalizante (encaminhamento) 
                pode ser registrada em um determinado mês, enquanto a sua matrícula efetiva e início no curso (inserção) se conclui apenas nos meses subsequentes. 
                Portanto, para análises gerenciais, recomenda-se a visualização do acumulado anual ou de intervalos de tempo maiores, onde essa defasagem temporal é diluída.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# TAB 3: MERCADO DE TRABALHO
# ==========================================
with tab3:
    st.markdown("### Pergunta 2: Taxa de conversão no mercado de trabalho?")
    st.markdown("*Dentre os adolescentes encaminhados para o mercado de trabalho, quantos foram efetivamente inseridos?*")
    
    df_jobs = df_filtered[
        (df_filtered["area"] == "profissionalizacao") & 
        (df_filtered["tipo"].str.contains("mercado de trabalho", case=False))
    ].copy()
    
    df_jobs_pivot = df_jobs.pivot_table(
        index="data",
        columns="tipo",
        values="valor",
        aggfunc="sum"
    ).reset_index()
    
    col_enc_job = "ENCAMINHADO para mercado de trabalho"
    col_ins_job = "INSERIDO no mercado de trabalho"
    
    # Check column presence
    if col_enc_job not in df_jobs_pivot.columns:
        df_jobs_pivot[col_enc_job] = 0.0
    if col_ins_job not in df_jobs_pivot.columns:
        df_jobs_pivot[col_ins_job] = 0.0
        
    df_jobs_pivot = df_jobs_pivot.fillna(0.0)
    
    total_enc_job = df_jobs_pivot[col_enc_job].sum()
    total_ins_job = df_jobs_pivot[col_ins_job].sum()
    conv_rate_job = (total_ins_job / total_enc_job * 100) if total_enc_job > 0 else 0.0
    
    # Render Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        render_kpi("Encaminhados para Vagas", f"{total_enc_job:,.0f}", "Jovens preparados", "neutral")
    with m2:
        render_kpi("Efetivamente Contratados", f"{total_ins_job:,.0f}", "Jovens empregados", "up")
    with m3:
        render_kpi("Taxa de Empregabilidade (Conversão)", f"{conv_rate_job:.1f}%", "Contratações / Encaminhamentos", "up" if conv_rate_job >= 50 else "neutral")
        
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_jobs_trend = px.line(
            df_jobs_pivot,
            x="data",
            y=[col_enc_job, col_ins_job],
            labels={"data": "Data", "value": "Quantidade", "variable": "Indicador"},
            title="Evolução de Encaminhamentos vs. Contratações",
            color_discrete_map={
                col_enc_job: "#0f516e",
                col_ins_job: "#006fa1"
            }
        )
        new_names_job = {col_enc_job: "Encaminhados", col_ins_job: "Inseridos (Contratados)"}
        fig_jobs_trend.for_each_trace(lambda t: t.update(name=new_names_job.get(t.name, t.name)))
        fig_jobs_trend = customize_fig(fig_jobs_trend)
        st.plotly_chart(fig_jobs_trend, use_container_width=True)
        
    with c2:
        df_jobs_pivot["Taxa de Conversão (%)"] = (df_jobs_pivot[col_ins_job] / df_jobs_pivot[col_enc_job] * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        fig_jobs_conv = px.bar(
            df_jobs_pivot,
            x="data",
            y="Taxa de Conversão (%)",
            title="Taxa de Empregabilidade Mensal (%)",
            color_discrete_sequence=["#006fa1"]
        )
        fig_jobs_conv = customize_fig(fig_jobs_conv)
        st.plotly_chart(fig_jobs_conv, use_container_width=True)
        
    st.markdown(
        """
        <div class="info-box">
            <div class="info-box-title"> Insight de Empregabilidade e Relação com o Mercado</div>
            <div class="info-box-content">
                A taxa de conversão no mercado de trabalho indica o sucesso da transição escola-trabalho propiciada pela Fundação. 
                Flutuações bruscas nesta métrica refletem fatores macroeconômicos (como abertura de vagas de Jovem Aprendiz por empresas parceiras 
                em períodos específicos do ano) e o alinhamento da qualificação técnica do jovem com as exigências de mercado. 
                Períodos de encaminhamento elevado sem contratação proporcional podem indicar gargalos que exigem capacitação complementar ou mediação mais próxima.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# TAB 4: FLUXO DE ENTRADA E SAÍDA
# ==========================================
with tab4:
    st.markdown("### Pergunta 3: Como é o fluxo de entrada e saída ao longo do tempo?")
    st.markdown("*Monitoramento do volume de novas admissões (entradas) em contrapartida aos desligamentos (saídas) dos programas.*")
    
    df_flow = df_filtered[
        (df_filtered["area"] == "educacao") & 
        (df_filtered["tipo"].isin(["Novos ingressos", "Desligamentos"]))
    ].copy()
    
    df_flow_pivot = df_flow.pivot_table(
        index="data",
        columns="tipo",
        values="valor",
        aggfunc="sum"
    ).reset_index()
    
    col_in = "Novos ingressos"
    col_out = "Desligamentos"
    
    # Check column presence
    if col_in not in df_flow_pivot.columns:
        df_flow_pivot[col_in] = 0.0
    if col_out not in df_flow_pivot.columns:
        df_flow_pivot[col_out] = 0.0
        
    df_flow_pivot = df_flow_pivot.fillna(0.0)
    
    total_in = df_flow_pivot[col_in].sum()
    total_out = df_flow_pivot[col_out].sum()
    net_flow = total_in - total_out
    
    # Render Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        render_kpi("Novos Ingressos (Entradas)", f"{total_in:,.0f}", "Total de novos atendidos", "up")
    with m2:
        render_kpi("Desligamentos (Saídas)", f"{total_out:,.0f}", "Total de desligados", "down")
    with m3:
        trend_direction = "up" if net_flow >= 0 else "down"
        trend_label = f"{'Saldo Positivo' if net_flow >= 0 else 'Saldo Negativo'}"
        render_kpi("Fluxo Líquido de Atendidos", f"{net_flow:+,.0f}", trend_label, trend_direction)
        
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_flow_trend = px.line(
            df_flow_pivot,
            x="data",
            y=[col_in, col_out],
            labels={"data": "Data", "value": "Quantidade", "variable": "Fluxo"},
            title="Fluxo Temporal: Novos Ingressos vs. Desligamentos",
            color_discrete_map={
                col_in: "#0f516e",
                col_out: "#006fa1"
            }
        )
        new_names_flow = {col_in: "Novos Ingressos (Entradas)", col_out: "Desligamentos (Saídas)"}
        fig_flow_trend.for_each_trace(lambda t: t.update(name=new_names_flow.get(t.name, t.name)))
        fig_flow_trend = customize_fig(fig_flow_trend)
        st.plotly_chart(fig_flow_trend, use_container_width=True)
        
    with c2:
        df_flow_pivot["Saldo Líquido"] = df_flow_pivot[col_in] - df_flow_pivot[col_out]
        df_flow_pivot["Tipo de Saldo"] = df_flow_pivot["Saldo Líquido"].apply(lambda x: "Positivo" if x >= 0 else "Negativo")
        fig_net_flow = px.bar(
            df_flow_pivot,
            x="data",
            y="Saldo Líquido",
            color="Tipo de Saldo",
            color_discrete_map={"Positivo": "#006fa1", "Negativo": "#0f516e"},
            title="Saldo Líquido Mensal (Ingressos - Desligamentos)",
            labels={"Saldo Líquido": "Saldo de Atendidos"}
        )
        fig_net_flow = customize_fig(fig_net_flow)
        st.plotly_chart(fig_net_flow, use_container_width=True)
        
    st.markdown("---")
    
    # Seasonality Analysis
    st.markdown("### Análise de Sazonalidade Histórica")
    st.markdown("*Média histórica de ingressos e saídas por mês do ano. Auxilia na alocação de infraestrutura e equipe.*")
    
    df_flow["mes_idx"] = df_flow["mes"].map({m: i for i, m in enumerate(month_order)})
    df_season = df_flow.groupby(["mes_idx", "mes", "tipo"])["valor"].mean().reset_index()
    df_season = df_season.sort_values("mes_idx")
    
    fig_season = px.bar(
        df_season,
        x="mes",
        y="valor",
        color="tipo",
        barmode="group",
        color_discrete_map={
            col_in: "#0f516e",
            col_out: "#006fa1"
        },
        labels={"valor": "Média Histórica", "mes": "Mês do Ano", "tipo": "Categoria"},
        title="Sazonalidade: Média de Entradas e Saídas por Mês",
        category_orders={"mes": month_order}
    )
    # Customize names
    fig_season.for_each_trace(lambda t: t.update(name="Novos Ingressos (Entradas)" if t.name == col_in else "Desligamentos (Saídas)"))
    fig_season = customize_fig(fig_season, hovermode="x unified")
    st.plotly_chart(fig_season, use_container_width=True)
    
    st.markdown(
        """
        <div class="info-box">
            <div class="info-box-title"> Aplicação Prática no Planejamento de Vagas e Infraestrutura</div>
            <div class="info-box-content">
                A análise de sazonalidade revela os momentos críticos de rotatividade do público atendido. 
                Meses com alto volume de novos ingressos exigem reforço nas equipes de triagem técnica e assistencial. 
                Paralelamente, picos de desligamento (comumente associados ao encerramento de ciclos letivos ou de capacitação no final e meio do ano) 
                indicam oportunidades para a reabertura imediata de vagas e reestruturação física de salas de aula e dormitórios. 
                Manter um saldo líquido previsível ajuda a evitar a sobrecarga de atendimentos ou a ociosidade de instalações.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
