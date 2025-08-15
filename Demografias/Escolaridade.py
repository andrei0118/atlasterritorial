import pandas as pd
import streamlit as st

@st.cache_data
def get_escolaridade_data(df_pnad):
    """
    Filtra os dados de escolaridade da PNAD de um DataFrame já filtrado.
    """
    if df_pnad is None or df_pnad.empty:
        return None
    
    required_cols = ['Escolaridade', 'Total']
    if not all(col in df_pnad.columns for col in required_cols):
        return None

    # Agrega os dados para exibição
    df_agg = df_pnad.groupby('Escolaridade')['Total'].sum().reset_index()
    total_eleitores = df_agg['Total'].sum()
    df_agg['Percentual'] = (df_agg['Total'] / total_eleitores) * 100
    df_agg.rename(columns={'Total': 'Escolaridade Total'}, inplace=True)

    return df_agg