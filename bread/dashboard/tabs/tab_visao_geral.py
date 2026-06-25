import plotly.express as px
import streamlit as st


def render(df_filtered, selected_years, render_kpi, customize_fig):
    # TAB 1: VISÃO GERAL
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
            # title="Evolução Temporal dos Atendimentos por Área"
        )
        # Relabel legend traces
        fig_area_ts.for_each_trace(lambda t: t.update(name=area_labels_full.get(t.name, t.name)))
        fig_area_ts = customize_fig(fig_area_ts)
        st.plotly_chart(fig_area_ts, width='stretch')

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
            # title="Proporção Acumulada de Atendimentos"
        )
        fig_pie = customize_fig(fig_pie, hovermode=None)
        st.plotly_chart(fig_pie, width='stretch')

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
        # title=f"Distribuição de Atendimentos em {area_labels_full[selected_area]}",
        color_discrete_sequence=["#006fa1"]
    )
    fig_cat = customize_fig(fig_cat, hovermode="y unified")
    st.plotly_chart(fig_cat, width='stretch')
