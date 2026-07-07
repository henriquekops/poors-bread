import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ._footer import render_footer

AREA_META = {
    "desdobramentos tecnicos": {
        "label": "Desdobramentos Técnicos",
        "color": "#0f516e",
        "color_rgba": "rgba(15,81,110,0.15)",
        "icon": "",
        "description": "Acompanhamento técnico individualizado, documentação, interfaces institucionais e movimentações dos assistidos.",
    },
    "educacao": {
        "label": "Educação",
        "color": "#006fa1",
        "color_rgba": "rgba(0,111,161,0.15)",
        "icon": "",
        "description": "Matrículas e vagas em aberto no ensino infantil, regular, EJA e SCFV — separadas por status de matrícula.",
    },
    "profissionalizacao": {
        "label": "Profissionalização",
        "color": "#3fa3d1",
        "color_rgba": "rgba(63,163,209,0.15)",
        "icon": "",
        "description": "Encaminhamentos e inserções em cursos profissionalizantes e no mercado de trabalho.",
    },
    "saude": {
        "label": "Saúde",
        "color": "#82c3e2",
        "color_rgba": "rgba(130,195,226,0.15)",
        "icon": "",
        "description": "Atendimentos de saúde clínica, saúde mental e internações registradas no período.",
    },
}

AREA_KEYS = list(AREA_META.keys())

# Graduated blues for charts with many categories
_BLUES = [
    "#08304a", "#0f516e", "#1a6f8f", "#006fa1", "#2389b5",
    "#3fa3d1", "#5ab5df", "#82c3e2", "#aad8ee", "#cce8f4",
    "#ddf0f9", "#edf7fc",
]


def _add_display_label(df_area: "pd.DataFrame", area_key: str) -> "pd.DataFrame":
    """Add a human-readable 'display_label' column combining tipo + status when relevant."""
    df = df_area.copy()
    if area_key == "educacao":
        df["display_label"] = df.apply(
            lambda r: f"{r['tipo']} ({r['status']})" if r["status"] != "none" else r["tipo"],
            axis=1,
        )
    else:
        df["display_label"] = df["tipo"]
    return df



def _render_area_charts(df_area, meta, customize_fig):
    """Render the three uniform charts for the selected area."""
    labels = sorted(df_area["display_label"].unique())
    n = len(labels)
    colors = (_BLUES * ((n // len(_BLUES)) + 1))[:n]
    color_map = dict(zip(labels, colors))

    c1, c2 = st.columns(2)

    with c1:
        df_ts = df_area.groupby(["data", "display_label"])["valor"].sum().reset_index()
        fig_ts = px.line(
            df_ts,
            x="data",
            y="valor",
            color="display_label",
            color_discrete_map=color_map,
            labels={"data": "Data", "valor": "Atendimentos", "display_label": "Categoria"},
        )
        fig_ts.update_traces(line=dict(width=1.5))
        fig_ts = customize_fig(fig_ts)
        st.plotly_chart(fig_ts, width="stretch")

    with c2:
        df_rank = (
            df_area.groupby("display_label")["valor"]
            .sum()
            .reset_index()
            .sort_values("valor", ascending=True)
        )
        fig_rank = px.bar(
            df_rank,
            x="valor",
            y="display_label",
            orientation="h",
            color="display_label",
            color_discrete_map=color_map,
            labels={"valor": "Total Acumulado", "display_label": ""},
        )
        fig_rank.update_layout(showlegend=False)
        fig_rank = customize_fig(fig_rank, hovermode="y unified")
        st.plotly_chart(fig_rank, width="stretch")

    fig_box = px.box(
        df_area,
        x="display_label",
        y="valor",
        color="display_label",
        color_discrete_map=color_map,
        labels={"display_label": "Categoria", "valor": "Valor Mensal"},
        points="outliers",
    )
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-28)
    fig_box = customize_fig(fig_box, hovermode="closest")
    st.plotly_chart(fig_box, width="stretch")




def render(df_filtered, render_kpi, customize_fig):
    st.markdown("### Detalhamento por Área de Atendimento")
    st.markdown(
        "*Selecione uma área para explorar o desempenho detalhado de cada categoria operacional.*"
    )

    selected_area = st.pills(
        "Área de Atendimento",
        options=AREA_KEYS,
        format_func=lambda k: f"{AREA_META[k]['icon']} {AREA_META[k]['label']}",
        default=AREA_KEYS[0],
        key="detail_area",
        label_visibility="collapsed",
    )
    # Guard against deselection (pills allows clicking again to deselect)
    if selected_area is None:
        selected_area = AREA_KEYS[0]

    meta = AREA_META[selected_area]

    st.markdown(
        f"""
        <div style="
            background:{meta['color_rgba']};
            border-left:4px solid {meta['color']};
            border-radius:8px;
            padding:12px 20px;
            margin:14px 0 18px 0;
        ">
            <span style="font-size:1.4rem;">{meta['icon']}</span>
            <strong style="font-size:1.05rem;margin-left:8px;color:{meta['color']};">
                {meta['label']}
            </strong>
            <p style="margin:5px 0 0 0;color:#888;font-size:0.88rem;">{meta['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df_area = df_filtered[df_filtered["area"] == selected_area].copy()
    df_area = _add_display_label(df_area, selected_area)

    if df_area.empty:
        st.info("Nenhum dado disponível para esta área no período selecionado.")
        return

    total = df_area["valor"].sum()
    n_tipos = df_area["display_label"].nunique()
    top_tipo = df_area.groupby("display_label")["valor"].sum().idxmax()
    top_short = top_tipo if len(top_tipo) <= 32 else top_tipo[:30] + "…"

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Total de Atendimentos", f"{total:,.0f}")
    with k2:
        st.metric("Categorias Monitoradas", str(n_tipos))
    with k3:
        st.metric("Categoria Destaque", top_short)

    st.markdown("---")

    _render_area_charts(df_area, meta, customize_fig)

    render_footer()
