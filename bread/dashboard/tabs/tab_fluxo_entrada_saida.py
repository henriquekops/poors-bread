import plotly.express as px
import streamlit as st


def render(df_filtered, month_order, render_kpi, customize_fig):
    # TAB 4: FLUXO DE ENTRADA E SAÍDA
    st.markdown("### Fluxo de entrada e saída")
    st.markdown("*Monitoramento do volume de novas admissões (entradas) em contrapartida aos desligamentos (saídas) dos programas.*")

    df_flow = df_filtered[
        (df_filtered["area"] == "desdobramentos tecnicos") &
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
            # title="Fluxo Temporal: Novos Ingressos vs. Desligamentos",
            color_discrete_map={
                col_in: "#0f516e",
                col_out: "#006fa1"
            }
        )
        new_names_flow = {col_in: "Novos Ingressos (Entradas)", col_out: "Desligamentos (Saídas)"}
        fig_flow_trend.for_each_trace(lambda t: t.update(name=new_names_flow.get(t.name, t.name)))
        fig_flow_trend = customize_fig(fig_flow_trend)
        st.plotly_chart(fig_flow_trend, width='stretch')

    with c2:
        df_flow_pivot["Saldo Líquido"] = df_flow_pivot[col_in] - df_flow_pivot[col_out]
        df_flow_pivot["Tipo de Saldo"] = df_flow_pivot["Saldo Líquido"].apply(lambda x: "Positivo" if x >= 0 else "Negativo")
        fig_net_flow = px.bar(
            df_flow_pivot,
            x="data",
            y="Saldo Líquido",
            color="Tipo de Saldo",
            color_discrete_map={"Positivo": "#006fa1", "Negativo": "#0f516e"},
            # title="Saldo Líquido Mensal (Ingressos - Desligamentos)",
            labels={"Saldo Líquido": "Saldo de Atendidos"}
        )
        fig_net_flow = customize_fig(fig_net_flow)
        st.plotly_chart(fig_net_flow, width='stretch')

    # st.markdown("---")

    # # Seasonality Analysis
    # st.markdown("### Análise de Sazonalidade Histórica")
    # st.markdown("*Média histórica de ingressos e saídas por mês do ano. Auxilia na alocação de infraestrutura e equipe.*")

    # df_flow["mes_idx"] = df_flow["mes"].map({m: i for i, m in enumerate(month_order)})
    # df_season = df_flow.groupby(["mes_idx", "mes", "tipo"])["valor"].mean().reset_index()
    # df_season = df_season.sort_values("mes_idx")

    # fig_season = px.bar(
    #     df_season,
    #     x="mes",
    #     y="valor",
    #     color="tipo",
    #     barmode="group",
    #     color_discrete_map={
    #         col_in: "#0f516e",
    #         col_out: "#006fa1"
    #     },
    #     labels={"valor": "Média Histórica", "mes": "Mês do Ano", "tipo": "Categoria"},
    #     # title="Sazonalidade: Média de Entradas e Saídas por Mês",
    #     category_orders={"mes": month_order}
    # )
    # # Customize names
    # fig_season.for_each_trace(lambda t: t.update(name="Novos Ingressos (Entradas)" if t.name == col_in else "Desligamentos (Saídas)"))
    # fig_season = customize_fig(fig_season, hovermode="x unified")
    # st.plotly_chart(fig_season, width='stretch')

    # st.markdown(
    #     """
    #     <div class="info-box">
    #         <div class="info-box-title"> Aplicação Prática no Planejamento de Vagas e Infraestrutura</div>
    #         <div class="info-box-content", style="color: black;">
    #             Texto descritivo
    #         </div>
    #     </div>
    #     """,
    #     unsafe_allow_html=True
    # )
