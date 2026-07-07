from pathlib import Path
import base64
import streamlit as st

from ._footer import render_footer


_ASSETS = Path(__file__).resolve().parent.parent / "assets"

_AUTHORS = [
    {
        "name": "Gustavo Losch do Amaral",
        "email": "g.losch@edu.pucrs.br",
        "linkedin": "gustavo-losch",
    },
    {
        "name": "Henrique Kops",
        "email": "henrique.kops@edu.pucrs.br",
        "linkedin": "henriquekops",
    },
    {
        "name": "Henrique Ramos Mayer",
        "email": "h.ramos@edu.pucrs.br",
        "linkedin": "henrique-ramos-mayer-7897911b2",
    },
]

_APP_URL = "https://poors-bread.streamlit.app"


_LINKEDIN_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="white">
  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762
           0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5
           -12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764
           1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604
           c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777
           7 2.476v6.759z"/>
</svg>
"""

_BTN_BASE = """
    display:inline-flex;align-items:center;gap:6px;
    text-decoration:none;border-radius:6px;
    padding:5px 12px;font-size:0.82rem;font-weight:600;
    transition:opacity 0.15s;
"""

def _author_card(author: dict) -> str:
    linkedin_url = author.get("linkedin", "")
    if linkedin_url and not linkedin_url.startswith("http"):
        linkedin_url = f"https://linkedin.com/in/{linkedin_url}"

    linkedin_btn = (
        f'<a href="{linkedin_url}" target="_blank" title="LinkedIn" style="{_BTN_BASE}'
        f'background:#0a66c2;color:white;">{_LINKEDIN_SVG.strip()}</a>'
        if linkedin_url
        else f'<span style="{_BTN_BASE}background:rgba(128,128,128,0.12);color:#aaa;cursor:default;">'
             f'{_LINKEDIN_SVG.strip()}</span>'
    )

    email = author.get("email", "")
    email_btn = (
        f'<a href="mailto:{email}" style="{_BTN_BASE}'
        f'background:rgba(15,81,110,0.1);color:#0f516e;border:1px solid rgba(15,81,110,0.25);">'
        f'{email}</a>'
        if email
        else '<span style="color:#bbb;font-size:0.82rem;">—</span>'
    )

    return f"""
    <div style="
        background:rgba(128,128,128,0.06);
        border:1px solid rgba(128,128,128,0.13);
        border-radius:10px;
        padding:14px 20px;
        margin-bottom:12px;
    ">
        <div style="font-weight:700;font-size:1.5rem;margin-bottom:10px;">{author['name']}</div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            {linkedin_btn}
            {email_btn}
        </div>
    </div>
    """



def render():
    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown("#### Autores")
        st.markdown("<br>", unsafe_allow_html=True)

        for author in _AUTHORS:
            st.markdown(_author_card(author), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Link de Acesso ao Dashboard", unsafe_allow_html=True)
        st.page_link(f"{_APP_URL}", label=f"{_APP_URL}")


    with right:
        st.markdown("#### QR Code")
        st.markdown(
            "<p style='color:#888;font-size:0.85rem;margin-bottom:12px;'>"
            "Aponte a câmera do celular para acessar o dashboard diretamente.</p>",
            unsafe_allow_html=True,
        )

        qr_path = _ASSETS / "qrcode.jpg"
        if qr_path.exists():
            # Render at fixed small width via HTML so it doesn't stretch full column
            qr_b64 = base64.b64encode(qr_path.read_bytes()).decode()
            st.markdown(
                f"""
                <div style="text-align:left;">
                    <img src="data:image/jpeg;base64,{qr_b64}"
                         width="300"
                         style="border-radius:8px;border:1px solid rgba(128,128,128,0.2);"
                         alt="QR Code poors-bread.streamlit.app"/>
                    <p style="font-size:0.75rem;color:#888;margin-top:6px;">{_APP_URL}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning("QR code não encontrado em assets/qrcode.png")
            st.markdown(f"[{_APP_URL}]({_APP_URL})")

    render_footer()
