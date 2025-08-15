import pandas as pd
import streamlit as st

@st.cache_data
def get_renda_data(df_pnad):
    """
    Agrega os dados de renda de um DataFrame já filtrado.
    """
    if df_pnad is None or df_pnad.empty:
        return None
    
    required_cols = ['Renda', 'Total']
    if not all(col in df_pnad.columns for col in required_cols):
        return None
    
    # Define a ordem correta para as categorias de renda
    ordem_renda = [
        'Até R$ 2000',
        'R$ 2000 a R$ 3000',
        'R$ 3000 a R$ 5000',
        'R$ 5000 a R$ 10000',
        'Acima de R$ 10000'
    ]

    # Converte a coluna 'Renda' para o tipo de dado Categoria com a ordem definida
    df_pnad['Renda'] = pd.Categorical(df_pnad['Renda'], categories=ordem_renda, ordered=True)

    # Agrega os dados e o agrupamento respeitará a ordem definida
    # Adicione observed=False para evitar o FutureWarning do pandas
    df_agg = df_pnad.groupby('Renda', observed=False)['Total'].sum().reset_index()
    total = df_agg['Total'].sum()
    df_agg['Percentual'] = (df_agg['Total'] / total) * 100
    df_agg.rename(columns={'Total': 'Renda Total'}, inplace=True)
    
    # Remove as categorias de renda que não existem nos dados filtrados
    df_agg = df_agg.dropna(subset=['Renda'])
    
    return df_agg