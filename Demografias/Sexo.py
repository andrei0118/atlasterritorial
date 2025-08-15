import pandas as pd
import streamlit as st

@st.cache_data
def get_sexo_data(df_tse):
    """
    Agrega e calcula o percentual de eleitores por sexo de um DataFrame já filtrado.
    """
    # A estrutura do novo DataFrame já possui 'SG_UF', 'NM_MUNICIPIO', 'DS_GENERO', 'QT_ELEITORES_PERFIL'.
    # A filtragem por UF e município agora é feita na consulta DuckDB em app.py.
    # A coluna 'DS_GENERO' ainda contém 'NÃO INFORMADO', por isso a filtragem é necessária.
    if df_tse is None or df_tse.empty:
        return None
    
    required_cols = ['DS_GENERO', 'QT_ELEITORES_PERFIL']
    if not all(col in df_tse.columns for col in required_cols):
        return None
    
    # Adiciona a filtragem para remover a classe 'NÃO INFORMADO'
    df_filtered = df_tse[df_tse['DS_GENERO'] != 'NÃO INFORMADO']

    # Se o DataFrame ficar vazio após a filtragem, retorne None
    if df_filtered.empty:
        return None

    # Agrega os dados por gênero e calcula o percentual
    df_agg = df_filtered.groupby('DS_GENERO')['QT_ELEITORES_PERFIL'].sum().reset_index()
    total = df_agg['QT_ELEITORES_PERFIL'].sum()
    df_agg['Percentual'] = (df_agg['QT_ELEITORES_PERFIL'] / total) * 100
    df_agg.rename(columns={'DS_GENERO': 'Sexo', 'QT_ELEITORES_PERFIL': 'Eleitores'}, inplace=True)
    
    return df_agg