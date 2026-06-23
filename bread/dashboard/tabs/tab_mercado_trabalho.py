import plotly.express as px
import streamlit as st


def render(df_filtered, render_kpi, customize_fig):
    # TAB 3: MERCADO DE TRABALHO
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
        st.plotly_chart(fig_jobs_trend, width='stretch')

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
        st.plotly_chart(fig_jobs_conv, width='stretch')

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
