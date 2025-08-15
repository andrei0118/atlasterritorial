import pandas as pd
import streamlit as st


@st.cache_data
def get_votacao_data(df_votacao):
    """
    Agrega e calcula o percentual de votos por candidato de um DataFrame já filtrado.
    """
    if df_votacao is None or df_votacao.empty:
        return None

    required_cols = ['NM_URNA_CANDIDATO', 'SG_PARTIDO', 'QT_VOTOS_NOMINAIS']
    if not all(col in df_votacao.columns for col in required_cols):
        return None

    df_agg = df_votacao.groupby(['NM_URNA_CANDIDATO', 'SG_PARTIDO'])[
        'QT_VOTOS_NOMINAIS'].sum().reset_index()

    df_agg.rename(columns={
        'NM_URNA_CANDIDATO': 'Candidatos',
        'SG_PARTIDO': 'Partido',
        'QT_VOTOS_NOMINAIS': 'Quantidade de Votos'
    }, inplace=True)

    total_votos = df_agg['Quantidade de Votos'].sum()

    if total_votos > 0:
        df_agg['Percentual'] = (
            df_agg['Quantidade de Votos'] / total_votos) * 100
    else:
        df_agg['Percentual'] = 0.0

    df_agg['Percentual'] = df_agg['Percentual'].round(2)
    df_agg = df_agg.sort_values('Quantidade de Votos', ascending=False)

    return df_agg
