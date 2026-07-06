import re
import base64

import requests
import streamlit as st

GITHUB_API = "https://api.github.com"
LEM_DIR = "data/input/LEM"
YEAR_RE = re.compile(r"20\d{2}")


def _github_cfg() -> dict:
    """Read GitHub coordinates and token from Streamlit secrets."""
    cfg = st.secrets["github"]
    return {
        "token": cfg["token"],
        "owner": cfg["owner"],
        "repo": cfg["repo"],
        "branch": cfg.get("branch", "main"),
    }


def _commit_file(filename: str, content: bytes) -> tuple[bool, str]:
    """Create or update an .xlsx in data/input/LEM via the GitHub Contents API."""
    cfg = _github_cfg()
    path = f"{LEM_DIR}/{filename}"
    url = f"{GITHUB_API}/repos/{cfg['owner']}/{cfg['repo']}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {cfg['token']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Fetch existing sha (required to overwrite an existing file)
    sha = None
    get_resp = requests.get(url, headers=headers, params={"ref": cfg["branch"]}, timeout=30)
    if get_resp.status_code == 200:
        sha = get_resp.json().get("sha")

    payload = {
        "message": f"data: upload {filename} via dashboard",
        "content": base64.b64encode(content).decode("ascii"),
        "branch": cfg["branch"],
    }
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(url, headers=headers, json=payload, timeout=60)
    if put_resp.status_code in (200, 201):
        action = "atualizado" if sha else "adicionado"
        return True, f"Arquivo {action} com sucesso."

    detail = put_resp.json().get("message", put_resp.text)
    return False, f"Erro {put_resp.status_code}: {detail}"


@st.dialog("Adicionar arquivo LEM")
def upload_dialog() -> None:
    """Password-gated modal to upload a new LEM .xlsx into the repo."""
    password = st.text_input("Senha", type="password")
    if password != st.secrets["upload"]["password"]:
        if password:
            st.error("Senha incorreta.")
        st.stop()

    st.caption(
        "O nome do arquivo deve conter o ano (ex.: `LEM_2025.xlsx`). "
        "Arquivos com `_partial` no nome são ignorados pelo processamento."
    )
    uploaded = st.file_uploader("Arquivo LEM (.xlsx)", type=["xlsx"])

    if uploaded is None:
        return

    if not YEAR_RE.search(uploaded.name):
        st.warning("O nome do arquivo precisa conter um ano (20XX) para ser processado.")
        return

    if st.button("Enviar", type="primary"):
        with st.spinner("Enviando para o repositório..."):
            ok, msg = _commit_file(uploaded.name, uploaded.getvalue())
        if ok:
            st.success(f"{msg} O dashboard será atualizado em ~1-2 min (após o redeploy).")
        else:
            st.error(msg)
