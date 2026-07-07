import numpy as np
import plotly.graph_objects as go
import streamlit as st

from ._footer import render_footer

def _horizon_chart(x, y, customize_fig, band_count: int = 3):
    """
    Horizon chart.

    The y-range is divided into `band_count` equal bands.
    Each band is folded back to the [0, band_h] / [-band_h, 0] window and
    drawn with a flat, solid color — no opacity variation between bands.
      - positive bands: #006fa1
      - negative bands: #0f516e
    """
    y = np.array(y, dtype=float)
    max_abs = max(float(np.abs(y).max()), 1.0)
    band_h = max_abs / band_count

    fig = go.Figure()

    pos_color = "rgba(0,111,161,0.85)"    # #006fa1, solid
    neg_color = "rgba(15,81,110,0.85)"    # #0f516e, solid

    for i in range(band_count):
        lo = i * band_h

        # Positive band i: fold values in [lo, lo+band_h] → [0, band_h]
        y_pos = np.where(y > lo, np.minimum(y - lo, band_h), 0.0)

        # Negative band i: fold values in [-lo-band_h, -lo] → [-band_h, 0]
        y_neg = np.where(y < -lo, np.maximum(y + lo, -band_h), 0.0)

        fig.add_trace(go.Scatter(
            x=x,
            y=y_pos,
            mode="lines",
            line=dict(shape="spline", smoothing=1.3, color="rgba(0,0,0,0)", width=0),
            fill="tozeroy",
            fillcolor=pos_color,
            showlegend=(i == 0),
            name="Saldo Positivo",
            legendgroup="pos",
            hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=x,
            y=y_neg,
            mode="lines",
            line=dict(shape="spline", smoothing=1.3, color="rgba(0,0,0,0)", width=0),
            fill="tozeroy",
            fillcolor=neg_color,
            showlegend=(i == 0),
            name="Saldo Negativo",
            legendgroup="neg",
            hoverinfo="skip",
        ))

    # Invisible hover line carrying the actual saldo value
    fig.add_trace(go.Scatter(
        x=x,
        y=np.clip(y, -band_h, band_h),
        mode="lines",
        line=dict(color="rgba(0,0,0,0)", width=0),
        customdata=y,
        hovertemplate="<b>%{x|%b %Y}</b><br>Saldo: %{customdata:+.0f}<extra></extra>",
        showlegend=False,
    ))

    # Zero baseline
    fig.add_hline(y=0, line_color="rgba(128,128,128,0.5)", line_width=1)

    # Fold-line guides at each band boundary
    for i in range(1, band_count):
        boundary = i * band_h
        fig.add_hline(
            y=boundary,
            line_dash="dot",
            line_color="rgba(0,111,161,0.35)",
            line_width=1,
        )
        fig.add_hline(
            y=-boundary,
            line_dash="dot",
            line_color="rgba(15,81,110,0.35)",
            line_width=1,
        )

    fig.update_yaxes(
        range=[-band_h, band_h],
        tickformat="+.0f",
        title_text="Saldo (dobrado)",
    )
    fig.update_xaxes(title_text="Data")

    return customize_fig(fig)


def render(df_filtered, month_order, render_kpi, customize_fig):
    st.markdown("### Fluxo de entrada e saída")
    st.markdown(
        "*Monitoramento do volume de novas admissões (entradas) em contrapartida "
        "aos desligamentos (saídas) dos programas.*"
    )

    df_flow = df_filtered[
        (df_filtered["area"] == "desdobramentos tecnicos") &
        (df_filtered["tipo"].isin(["Novos ingressos", "Desligamentos"]))
    ].copy()

    df_flow_pivot = df_flow.pivot_table(
        index="data",
        columns="tipo",
        values="valor",
        aggfunc="sum",
    ).reset_index()

    col_in = "Novos ingressos"
    col_out = "Desligamentos"

    if col_in not in df_flow_pivot.columns:
        df_flow_pivot[col_in] = 0.0
    if col_out not in df_flow_pivot.columns:
        df_flow_pivot[col_out] = 0.0

    df_flow_pivot = df_flow_pivot.fillna(0.0)

    total_in = df_flow_pivot[col_in].sum()
    total_out = df_flow_pivot[col_out].sum()
    net_flow = total_in - total_out

    m1, m2, m3 = st.columns(3)
    with m1:
        render_kpi("Novos Ingressos (Entradas)", f"{total_in:,.0f}", "Total de novos atendidos", "up")
    with m2:
        render_kpi("Desligamentos (Saídas)", f"{total_out:,.0f}", "Total de desligados", "down")
    with m3:
        trend_direction = "up" if net_flow >= 0 else "down"
        trend_label = "Saldo Positivo" if net_flow >= 0 else "Saldo Negativo"
        render_kpi("Fluxo Líquido de Atendidos", f"{net_flow:+,.0f}", trend_label, trend_direction)

    st.markdown("---")

    st.markdown(
        "<p style='font-size:0.78rem;color:#888;margin:0 0 6px 0;'>"
        "Saldo líquido mensal (Ingressos − Desligamentos). "
        "Bandas dobradas sobre o mesmo eixo: azul claro = saldo positivo, "
        "azul escuro = saldo negativo. Linhas pontilhadas marcam os limiares de dobramento.</em></p>",
        unsafe_allow_html=True,
    )

    df_flow_pivot["Saldo Líquido"] = df_flow_pivot[col_in] - df_flow_pivot[col_out]

    fig_horizon = _horizon_chart(
        x=df_flow_pivot["data"].values,
        y=df_flow_pivot["Saldo Líquido"].values,
        customize_fig=customize_fig,
    )
    st.plotly_chart(fig_horizon, width="stretch")

    render_footer()
