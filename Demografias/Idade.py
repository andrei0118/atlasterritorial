import pandas as pd
import streamlit as st

@st.cache_data
def get_idade_data(df_tse):
    """
    Agrega e calcula o percentual de eleitores por faixa etária de um DataFrame já filtrado.
    """
    # A estrutura do novo DataFrame já possui 'SG_UF', 'NM_MUNICIPIO', 'DS_FAIXA_ETARIA', 'QT_ELEITORES_PERFIL'.
    # A filtragem por UF e município agora é feita na consulta DuckDB em app.py.
    if df_tse is None or df_tse.empty:
        return None

    required_cols = ['DS_FAIXA_ETARIA', 'QT_ELEITORES_PERFIL']
    if not all(col in df_tse.columns for col in required_cols):
        return None
    
    # Agrega os dados por faixa etária e calcula o percentual
    df_agg = df_tse.groupby('DS_FAIXA_ETARIA')['QT_ELEITORES_PERFIL'].sum().reset_index()
    total = df_agg['QT_ELEITORES_PERFIL'].sum()
    df_agg['Percentual'] = (df_agg['QT_ELEITORES_PERFIL'] / total) * 100
    df_agg.rename(columns={'DS_FAIXA_ETARIA': 'Faixa Etária', 'QT_ELEITORES_PERFIL': 'Eleitores'}, inplace=True)
    
    return df_agg