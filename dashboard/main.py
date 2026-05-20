from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

output_path = f"{Path(__file__).parent.parent}/data/output"

month_order = [
    "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
    "JUL", "AGO", "SET", "OUT", "NOV", "DEZ",
]

df = pd.read_csv(f"{output_path}/processed.csv")

df = df[df["ano"] == 2021].copy()
df["mes_idx"] = df["mes"].map({m: i for i, m in enumerate(month_order)})
df = df.sort_values("mes_idx")

st.title("Poor's Bread")

fig = px.line(
    df,
    x="mes",
    y="valor",
    color="tipo",
    facet_col="area",
    facet_col_wrap=2,
    labels={"mes": "Mês", "valor": "Contagem", "tipo": "Categoria", "area": "Área"},
    category_orders={"mes": month_order},
)

st.plotly_chart(fig, use_container_width=True)
