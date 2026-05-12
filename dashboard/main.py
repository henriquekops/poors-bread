from pathlib import Path

import pandas as pd
import streamlit as st

output_path = f"{Path(__file__).parent.parent}/data/output"

df = pd.read_csv(f"{output_path}/processed.csv")
df = df[df["Category"] == "Atendimentos indvidual"].sort_values(["Month"])
df = df[["Month", "Value", "Category"]].head()


st.title("Poor's Bread")
st.line_chart(df, x="Month", y="Value", color="Category")
