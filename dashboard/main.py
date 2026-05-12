from pathlib import Path

import pandas as pd
import streamlit as st

output_path = f"{Path(__file__).parent.parent}/data/output"

month_order = {
    m: i
    for i, m in enumerate(
        [
            "JAN",
            "FEV",
            "MAR",
            "ABR",
            "MAI",
            "JUN",
            "JUL",
            "AGO",
            "SET",
            "OUT",
            "NOV",
            "DEZ",
        ]
    )
}

df = pd.read_csv(f"{output_path}/processed.csv")

df = df[df["Year"] == 2021]
df["MonthIdx"] = df["Month"].map(month_order)
df = df[["Month", "Value", "Category", "MonthIdx"]].sort_values(
    ["MonthIdx"], ascending=True
)

st.title("Poor's Bread")

st.line_chart(
    df, x="MonthIdx", y="Value", x_label="Mes", y_label="Contagem", color="Category"
)
