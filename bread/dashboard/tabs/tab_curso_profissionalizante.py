import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render(df_filtered, render_kpi, customize_fig):
    # TAB 2: CURSO PROFISSIONALIZANTE
    st.markdown("### Taxa de conversão nos cursos profissionalizantes")
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
        fig_course_trend = go.Figure()
        fig_course_trend.add_trace(go.Scatter(
            x=df_course_pivot["data"],
            y=df_course_pivot[col_ins],
            name="Inseridos",
            mode="lines",
            line=dict(color="#006fa1", width=2),
            fill="none",
        ))
        fig_course_trend.add_trace(go.Scatter(
            x=df_course_pivot["data"],
            y=df_course_pivot[col_enc],
            name="Encaminhados",
            mode="lines",
            line=dict(color="#0f516e", width=2),
            fill="tonexty",
            fillcolor="rgba(15, 81, 110, 0.20)",
        ))
        fig_course_trend.update_layout(
            xaxis_title="Data",
            yaxis_title="Quantidade",
            legend_title="Indicador",
        )
        fig_course_trend = customize_fig(fig_course_trend)
        st.plotly_chart(fig_course_trend, width='stretch')

    with c2:
        df_course_pivot["Taxa de Conversão (%)"] = (df_course_pivot[col_ins] / df_course_pivot[col_enc] * 100).fillna(0).replace([float('inf'), -float('inf')], 0)
        fig_course_conv = px.bar(
            df_course_pivot,
            x="data",
            y="Taxa de Conversão (%)",
            # title="Taxa de Conversão Mensal (%)",
            color_discrete_sequence=["#006fa1"]
        )
        fig_course_conv = customize_fig(fig_course_conv)
        st.plotly_chart(fig_course_conv, width='stretch')

    st.markdown(
        """
        <div class="info-box">
            <div class="info-box-title"> Contextualização Técnica e Análise do Efeito Latência</div>
            <div class="info-box-content", style="color: blue;">
                Descrição detalhada
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
