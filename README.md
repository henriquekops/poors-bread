# Dataviz project

> Authors: Gustavo Losch, Henrique Mayer e Henrique Kops

---

### Dashboard

https://dataviz-pucrs.streamlit.app

---

### Project structure

```mermaid
flowchart LR
    
    input_data
    preprocess
    curated_data
    dashboard

    input_data --> preprocess
    preprocess --> curated_data
    curated_data --> dashboard
```

---

### Run csv converter

```bash
python preprocess --convert 
```

---

### Run streamlit locally

```bash
streamlit run dashboard/main.py
```