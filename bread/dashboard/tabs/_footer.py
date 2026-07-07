"""Shared footer rendered at the bottom of every tab."""
import base64
from pathlib import Path

import streamlit as st

_ASSETS = Path(__file__).resolve().parent.parent / "assets"


def render_footer() -> None:
    st.markdown("---")

    left, right = st.columns([1, 2], gap="large")

    with left:
        pucrs_path = _ASSETS / "pucrs.png"
        if pucrs_path.exists():
            b64 = base64.b64encode(pucrs_path.read_bytes()).decode()
            st.markdown(
                f'<img src="data:image/png;base64,{b64}" height="20" '
                f'style="opacity:0.85;" alt="PUCRS"/>',
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            """
            <div style="
                display:flex;align-items:center;height:48px;
                color:#888;font-size:0.8rem;
            ">
                Visualização de Dados &nbsp;·&nbsp; PUCRS
                &nbsp;·&nbsp; Dashboard Pão dos Pobres
            </div>
            """,
            unsafe_allow_html=True,
        )
