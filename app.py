import streamlit as st
import pandas as pd
import os
import duckdb

# Importa as funções dos módulos de dados
from Demografias.Sexo import get_sexo_data
from Demografias.Idade import get_idade_data
from Demografias.Renda import get_renda_data
from Demografias.Escolaridade import get_escolaridade_data
from Eleicoes.Votacao import get_votacao_data

# Dicionário de mapeamento de siglas para nomes de estados
UF_NAMES = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia",
    "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins"
}

st.set_page_config(
    page_title="Atlas Territorial",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Navegação na barra lateral
st.sidebar.image("assets/logo-atlasintel.png", width=180)
paginas = ["Demografias", "Eleições"]
selecao_pagina = st.sidebar.radio("Selecione a página:", paginas)

# --- Lógica Centralizada de Carregamento de Dados


@st.cache_data
def run_duckdb_query(query, file_path):
    """
    Função para executar uma consulta no DuckDB contra um arquivo Parquet.
    """
    if not os.path.exists(file_path):
        st.error(f"Erro: Arquivo '{file_path}' não encontrado.")
        return pd.DataFrame()

    try:
        conn = duckdb.connect(database=':memory:', read_only=False)
        # A consulta agora pode ler diretamente do arquivo Parquet
        df = conn.execute(query).fetchdf()
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao executar consulta no DuckDB: {e}")
        return pd.DataFrame()


# Carrega os conjuntos de dados. ATUALIZADO para os novos arquivos do TSE.
pnad_renda_file = 'data/dados_pnad_renda.parquet'
pnad_escolaridade_file = 'data/pnad_escolaridade_2023.parquet'
tse_genero_file = 'data/eleitores_por_genero.parquet'
tse_idade_file = 'data/eleitores_por_faixa_etaria.parquet'
eleicoes_file = 'data/dados_votacao_candidato_munzona_2022_BR.parquet'

# --- Widgets de Seleção no topo da página
st.header(selecao_pagina)

col1, col2 = st.columns(2)
with col1:
    ufs_list = sorted(list(UF_NAMES.values()))
    ufs_list.insert(0, "Brasil")
    selecao_local = st.selectbox(
        "Selecionar Local (País e Estados)",
        ufs_list
    )

uf_param_tse = None
titulo_local = selecao_local
municipios_disponiveis = ["Todos"]
selecao_municipio = "Todos"

# O seletor de município do topo agora só aparece na página de Demografias
if selecao_pagina == "Demografias":
    if selecao_local != "Brasil":
        uf_param_tse = next(
            (key for key, value in UF_NAMES.items() if value == selecao_local), None)
        if uf_param_tse:
            query = f"SELECT DISTINCT NM_MUNICIPIO FROM '{tse_genero_file}' WHERE SG_UF = '{uf_param_tse}' ORDER BY NM_MUNICIPIO;"
            municipios_df = run_duckdb_query(query, tse_genero_file)
            if not municipios_df.empty:
                municipios = municipios_df['NM_MUNICIPIO'].tolist()
                municipios_disponiveis = ["Todos"] + municipios

    with col2:
        selecao_municipio = st.selectbox(
            "Selecionar Município",
            municipios_disponiveis,
            key="municipio_demografias"
        )

uf_param_pnad = None
if selecao_local != "Brasil":
    uf_param_pnad = selecao_local

# --- Exibe a página selecionada
if selecao_pagina == "Demografias":
    # --- Seção de Gênero
    if os.path.exists(tse_genero_file):
        query_sexo_base = f"SELECT * FROM '{tse_genero_file}'"
        where_clauses_sexo = []
        if uf_param_tse:
            where_clauses_sexo.append(f"SG_UF = '{uf_param_tse}'")
        if selecao_municipio and selecao_municipio != "Todos":
            where_clauses_sexo.append(f"NM_MUNICIPIO = '{selecao_municipio}'")

        final_query_sexo = query_sexo_base
        if where_clauses_sexo:
            final_query_sexo += " WHERE " + " AND ".join(where_clauses_sexo)

        df_sexo_filtered = run_duckdb_query(final_query_sexo, tse_genero_file)
        df_sexo = get_sexo_data(df_sexo_filtered)

        with st.container(border=True):
            st.subheader(f"Sexo")
            st.caption("Fonte: TSE (Tribunal Superior Eleitoral) Mês atual")
            if df_sexo is not None:
                st.dataframe(df_sexo.style.format({
                    'Eleitores': '{:,.0f}',
                    'Percentual': '{:,.1f}%'
                }), use_container_width=True, hide_index=True)
            else:
                st.info(
                    f"Não há dados de sexo disponíveis para {titulo_local} e o município selecionado.")
    else:
        st.warning(
            "Não foi possível carregar os dados de gênero do TSE. Verifique o arquivo Parquet.")

    # --- Seção de Faixa Etária
    if os.path.exists(tse_idade_file):
        query_idade_base = f"SELECT * FROM '{tse_idade_file}'"
        where_clauses_idade = []
        if uf_param_tse:
            where_clauses_idade.append(f"SG_UF = '{uf_param_tse}'")
        if selecao_municipio and selecao_municipio != "Todos":
            where_clauses_idade.append(f"NM_MUNICIPIO = '{selecao_municipio}'")

        final_query_idade = query_idade_base
        if where_clauses_idade:
            final_query_idade += " WHERE " + " AND ".join(where_clauses_idade)

        df_idade_filtered = run_duckdb_query(final_query_idade, tse_idade_file)
        df_idade = get_idade_data(df_idade_filtered)

        with st.container(border=True):
            st.subheader(f"Faixa Etária")
            st.caption("Fonte: TSE (Tribunal Superior Eleitoral) Mês atual")
            if df_idade is not None:
                st.dataframe(df_idade.style.format({
                    'Eleitores': '{:,.0f}',
                    'Percentual': '{:,.1f}%'
                }), use_container_width=True, hide_index=True)
            else:
                st.info(
                    f"Não há dados de faixa etária disponíveis para {titulo_local} e o município selecionado.")
    else:
        st.warning(
            "Não foi possível carregar os dados de faixa etária do TSE. Verifique o arquivo Parquet.")

    st.markdown("---")
    st.subheader("Análise Socioeconômica da PNAD")
    st.info("Os dados a seguir são por região e dependem apenas do Estado, ignorando a seleção de Município.")

    # Mapeamento e lógica de seleção de região AJUSTADA para incluir "Todas as Regiões"
    regioes_map_simple_to_full = {
        "Todas as Regiões": ["Capital", "Resto da RM (Região Metropolitana, excluindo a capital)", "Resto da RIDE (Região Integrada de Desenvolvimento Econômico, excluindo a capital)", "Resto da UF (Unidade da Federação, excluindo a região metropolitana e a RIDE)"],
        "Capital": ["Capital"],
        "Região Metropolitana": ["Resto da RM (Região Metropolitana, excluindo a capital)"],
        "RIDE": ["Resto da RIDE (Região Integrada de Desenvolvimento Econômico, excluindo a capital)"],
        "Interior": ["Resto da UF  (Unidade da Federação, excluindo a região metropolitana e a RIDE)"],

    }

    # Adiciona "Todas as Regiões" como primeira opção
    regioes_disponiveis = list(regioes_map_simple_to_full.keys())

    # Define a seleção padrão com base no local
    # Se "Brasil" ou "Todos" os municípios, a opção padrão é "Todas as Regiões"
    index_padrao = 0
    if selecao_local != "Brasil" and selecao_municipio != "Todos":
        # Se um estado e um município são selecionados, a seleção padrão é "Capital"
        # Esta é uma suposição, pode ser ajustado conforme a necessidade
        index_padrao = regioes_disponiveis.index(
            "Capital") if "Capital" in regioes_disponiveis else 0

    regiao_selecionada_simples = st.radio(
        "Selecione a Região:",
        regioes_disponiveis,
        index=index_padrao,
        key="regiao_pnad"
    )

    regioes_selecionadas_full_names = regioes_map_simple_to_full[regiao_selecionada_simples]

    if os.path.exists(pnad_renda_file) and os.path.exists(pnad_escolaridade_file):
        query_renda_base = f"SELECT * FROM '{pnad_renda_file}'"
        where_clauses_renda = []
        if uf_param_pnad:
            where_clauses_renda.append(f"UF = '{uf_param_pnad}'")
        if regioes_selecionadas_full_names:
            regioes_str = "','".join(regioes_selecionadas_full_names)
            where_clauses_renda.append(f"Região IN ('{regioes_str}')")

        final_query_renda = query_renda_base
        if where_clauses_renda:
            final_query_renda += " WHERE " + " AND ".join(where_clauses_renda)

        df_pnad_renda_filtered = run_duckdb_query(
            final_query_renda, pnad_renda_file)

        with st.container(border=True):
            st.subheader(f"Renda")
            st.caption(
                "Fonte: PNADc (Pesquisa Nacional por Amostra de Domicílios Contínua) 2023")
            df_renda = get_renda_data(df_pnad_renda_filtered)
            if df_renda is not None:
                st.dataframe(df_renda.style.format(
                    {'Renda Total': '{:,.2f}', 'Percentual': '{:,.1f}%'}), use_container_width=True, hide_index=True)
            else:
                st.info(
                    f"Não há dados de renda disponíveis para {titulo_local} e as regiões selecionadas.")

        query_escolaridade_base = f"SELECT * FROM '{pnad_escolaridade_file}'"
        where_clauses_escolaridade = []
        if uf_param_pnad:
            where_clauses_escolaridade.append(f"UF = '{uf_param_pnad}'")
        if regioes_selecionadas_full_names:
            regioes_str = "','".join(regioes_selecionadas_full_names)
            where_clauses_escolaridade.append(f"Região IN ('{regioes_str}')")

        final_query_escolaridade = query_escolaridade_base
        if where_clauses_escolaridade:
            final_query_escolaridade += " WHERE " + \
                " AND ".join(where_clauses_escolaridade)

        df_pnad_escolaridade_filtered = run_duckdb_query(
            final_query_escolaridade, pnad_escolaridade_file)

        with st.container(border=True):
            st.subheader(f"Escolaridade")
            st.caption(
                "Fonte: PNADc (Pesquisa Nacional por Amostra de Domicílios Contínua) 2023")
            df_escolaridade = get_escolaridade_data(
                df_pnad_escolaridade_filtered)
            if df_escolaridade is not None:
                st.dataframe(df_escolaridade.style.format(
                    {'Escolaridade Total': '{:,.2f}', 'Percentual': '{:,.1f}%'}), use_container_width=True, hide_index=True)
            else:
                st.info(
                    f"Não há dados de escolaridade disponíveis para {titulo_local} e as regiões selecionadas.")
    else:
        st.warning(
            "Não foi possível carregar os dados de renda ou escolaridade. Verifique os arquivos Parquet.")

elif selecao_pagina == "Eleições":
    st.markdown("---")
    st.caption("Fonte: TSE (Tribunal Superior Eleitoral)")
    if os.path.exists(eleicoes_file):
        query_uf_eleicoes = f"SELECT DISTINCT SG_UF FROM '{eleicoes_file}' ORDER BY SG_UF;"
        ufs_disponiveis_eleicoes_df = run_duckdb_query(
            query_uf_eleicoes, eleicoes_file)
        ufs_disponiveis_eleicoes = ufs_disponiveis_eleicoes_df['SG_UF'].tolist(
        )

        uf_param_eleicoes = next((key for key, value in UF_NAMES.items(
        ) if value == selecao_local), None) if selecao_local != "Brasil" else None

        # Modificação para filtrar a lista de municípios para a página de Eleições
        municipios_disponiveis_eleicoes = ["Todos"]
        if uf_param_eleicoes:
            query_municipios = f"SELECT DISTINCT NM_MUNICIPIO FROM '{eleicoes_file}' WHERE SG_UF = '{uf_param_eleicoes}' ORDER BY NM_MUNICIPIO;"
            municipios_df = run_duckdb_query(query_municipios, eleicoes_file)
            if not municipios_df.empty:
                municipios_disponiveis_eleicoes = sorted(
                    municipios_df['NM_MUNICIPIO'].tolist())
                municipios_disponiveis_eleicoes.insert(0, "Todos")

        col_loc, col_turn, col_cargo = st.columns(3)
        with col_loc:
            selecao_municipio_eleicoes = st.selectbox(
                "Selecionar Município",
                municipios_disponiveis_eleicoes,
                key="municipio_eleicoes"
            )
        with col_turn:
            turnos_query = f"SELECT DISTINCT NR_TURNO FROM '{eleicoes_file}' ORDER BY NR_TURNO;"
            turnos_df = run_duckdb_query(turnos_query, eleicoes_file)
            turnos = sorted(turnos_df['NR_TURNO'].tolist())
            selecao_turno = st.selectbox("Selecione o Turno:", turnos)
        with col_cargo:
            ordem_cargos = [
                "Presidente",
                "Governador",
                "Senador"
            ]
            selecao_cargo = st.selectbox(
                "Selecione o Cargo:", ordem_cargos, index=0)

        st.subheader(f"Resultados de Votação por Candidato")

        query_votacao_base = f"SELECT NM_URNA_CANDIDATO, SG_PARTIDO, QT_VOTOS_NOMINAIS FROM '{eleicoes_file}'"
        where_clauses_votacao = []
        if uf_param_eleicoes:
            where_clauses_votacao.append(f"SG_UF = '{uf_param_eleicoes}'")
        if selecao_municipio_eleicoes and selecao_municipio_eleicoes != "Todos":
            where_clauses_votacao.append(
                f"NM_MUNICIPIO = '{selecao_municipio_eleicoes}'")
        if selecao_turno:
            where_clauses_votacao.append(f"NR_TURNO = {selecao_turno}")
        if selecao_cargo:
            where_clauses_votacao.append(f"DS_CARGO = '{selecao_cargo}'")

        final_query_votacao = query_votacao_base
        if where_clauses_votacao:
            final_query_votacao += " WHERE " + \
                " AND ".join(where_clauses_votacao)

        df_votacao_filtered = run_duckdb_query(
            final_query_votacao, eleicoes_file)

        df_votacao = get_votacao_data(df_votacao_filtered)

        if df_votacao is not None and not df_votacao.empty:
            st.dataframe(df_votacao.style.format({
                'Quantidade de Votos': '{:,.0f}',
                'Percentual': '{:,.2f}%'
            }), use_container_width=True, hide_index=True)
        else:
            st.info(f"Não há dados de votação para a seleção atual.")
    else:
        st.warning(
            "Não foi possível carregar os dados de votação. Verifique o arquivo Parquet.")

st.markdown("---")
