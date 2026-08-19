import altair as alt
import os
import pandas as pd
import re
import streamlit as st


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Painel de Dados - SC",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    '<html lang="pt-BR">',
    unsafe_allow_html=True,
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Remove espaço superior */
    .stMainBlockContainer,
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0px !important;
    }

    /* Remove cabeçalho nativo */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Esconde elementos nativos */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    /* Título */
    h1 {
        font-size: 28px !important;
        font-weight: 700 !important;
        padding-bottom: 10px !important;
    }

    /* Selectbox */
    div[data-baseweb="select"] {
        width: max-content !important;
        min-width: 400px;
    }

    div[data-testid="stSelectbox"] {
        width: max-content !important;
    }

    /* Cabeçalho da tabela */
    [data-testid="stDataFrameHeaderCell"],
    [data-testid="stDataFrameHeaderCell"] div,
    [data-testid="stDataFrameHeaderCell"] span {
        text-align: center !important;
        justify-content: center !important;
    }

    /* Células da tabela */
    [data-testid="stDataFrameDataCell"] div,
    [data-testid="stDataFrameDataCell"] span {
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        align-items: center !important;
    }

    /* Gráfico */
    .grafico-container {
        overflow-x: auto;
        overflow-y: auto;
        width: 100%;
        padding-bottom: 15px;
    }

    .vega-actions {
        display: none !important;
    }

    /* Legenda */
    .legenda-container {
        display: flex;
        gap: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
        font-family: sans-serif;
    }

    .legenda-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        font-size: 14px;
    }

    .legenda-cor {
        width: 24px;
        height: 12px;
        border-radius: 3px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOGO
# ============================================================

if os.path.exists("logo3.png"):

    st.image(
        "logo3.png",
        width="stretch",
    )

else:

    st.warning(
        "⚠️ Arquivo 'logo3.png' não encontrado no diretório do projeto."
    )


# ============================================================
# TÍTULO
# ============================================================

st.title("📊 Violência contra mulher / Dados por região")


# ============================================================
# BOTÃO ATUALIZAR
# ============================================================

if st.button("🔄 Atualizar Dados da Planilha"):

    st.cache_data.clear()
    st.rerun()


# ============================================================
# PLANILHA
# ============================================================

CHAVE_PLANILHA = (
    "2PACX-1vQphTOOMb4O8THD00u-DFnJJLRN2tTcfDwWWL-X4spLdQL6TfHY4XeFA5mGKuhN90f6lBwgFVWclx1_"
)


# ============================================================
# REGIÕES
# ============================================================

MAPA_REGIOES = {
    "Grande Florianópolis": "0",
    "Norte": "2083350771",
    "Oeste": "1832830464",
    "Serrana": "1821320456",
    "Sul": "993904023",
    "Itajai": "575766075",
}

MAPA_REGIOES = dict(sorted(MAPA_REGIOES.items()))


# ============================================================
# CARREGAR DADOS
# ============================================================

@st.cache_data(ttl=60)
def carregar_dados_brutos(chave, gid):

    url_csv = (
        f"https://docs.google.com/spreadsheets/d/e/"
        f"{chave}/pub?gid={gid}&single=true&output=csv"
    )

    df = pd.read_csv(
        url_csv,
        header=None,
        dtype=str,
    )

    return df


# ============================================================
# MENU DE NAVEGAÇÃO
# ============================================================

pagina_selecionada = st.radio(
    "Modo de Navegação:",
    [
        "📊 Dados por Região (Detalhado)",
        "🗺️ Comparativo Geral entre Regiões",
    ],
    horizontal=True,
)

st.write("---")


# ============================================================
# LIMPAR DASHBOARD
# ============================================================

def limpar_dashboard():

    # Região volta para o estado inicial
    st.session_state["regiao_guia"] = "Escolha a Região..."

    # Remove seleções dinâmicas
    chaves_para_remover = [
        chave
        for chave in list(st.session_state.keys())
        if chave.startswith("seletor_ocorrencia_")
        or chave.startswith("radio_")
        or chave.startswith("c_")
    ]

    for chave in chaves_para_remover:

        if chave != "regiao_guia":
            del st.session_state[chave]


# ============================================================
# PÁGINA DE DADOS POR REGIÃO
# ============================================================

if pagina_selecionada == "📊 Dados por Região (Detalhado)":

    try:

        # --------------------------------------------------------
        # REGIÃO + BOTÃO LIMPAR
        # --------------------------------------------------------

        opcoes_regiao = [
            "Escolha a Região..."
        ] + list(MAPA_REGIOES.keys())

        col_regiao, col_limpar = st.columns([5, 1])

        with col_regiao:

            aba_selecionada = st.selectbox(
                "Selecione a Região (Guia):",
                options=opcoes_regiao,
                key="regiao_guia",
            )

        with col_limpar:

            st.write("")
            st.write("")

            st.button(
                "🗑 Limpar Seleção",
                on_click=limpar_dashboard,
                use_container_width=True,
            )


        # --------------------------------------------------------
        # NENHUMA REGIÃO SELECIONADA
        # --------------------------------------------------------

        if aba_selecionada == "Escolha a Região...":

            st.info(
                "ℹ️ Por favor, selecione uma região acima para começar."
            )


        # --------------------------------------------------------
        # REGIÃO SELECIONADA
        # --------------------------------------------------------

        else:

            gid_atual = MAPA_REGIOES[aba_selecionada]

            with st.spinner(
                f"Carregando dados de: {aba_selecionada}..."
            ):

                df_bruto = carregar_dados_brutos(
                    CHAVE_PLANILHA,
                    gid_atual,
                )


            # ----------------------------------------------------
            # POPULAÇÃO
            # ----------------------------------------------------

            populacao_atual = None

            texto_populacao_formatado = (
                "Não localizada na célula E3"
            )

            try:

                if (
                    df_bruto.shape[0] > 2
                    and df_bruto.shape[1] > 4
                ):

                    celula_e3 = str(
                        df_bruto.iloc[2, 4]
                    ).strip()

                    apenas_numeros = re.sub(
                        r"\D",
                        "",
                        celula_e3,
                    )

                    if apenas_numeros:

                        populacao_atual = float(
                            apenas_numeros
                        )

                        texto_populacao_formatado = (
                            f"{int(populacao_atual):,}"
                            .replace(",", ".")
                        )

            except Exception:
                pass


            if not populacao_atual or populacao_atual == 0:

                populacao_atual = 1000000

                texto_populacao_formatado = (
                    "Erro de leitura / Célula vazia"
                )


            st.metric(
                label="👥 População Feminina Aproximada",
                value=texto_populacao_formatado,
            )


            # ----------------------------------------------------
            # LOCALIZAR OCORRÊNCIAS
            # ----------------------------------------------------

            indices_titulos = []
            nomes_titulos = []

            for idx, row in df_bruto.iterrows():

                celula_texto = str(
                    row.iloc[0]
                ).upper()

                if (
                    "FATO COMUNICADO" in celula_texto
                    or "OCORRÊNCIA" in celula_texto
                ):

                    indices_titulos.append(idx)

                    nomes_titulos.append(
                        str(row.iloc[0]).strip()
                    )


            if not nomes_titulos:

                st.warning(
                    "⚠️ Nenhum padrão 'FATO COMUNICADO' "
                    "localizado nesta guia."
                )

                opcoes_combo = [
                    "Padrão não encontrado"
                ]

            else:

                opcoes_combo = [
                    "Escolha a Ocorrência..."
                ] + nomes_titulos


            # ----------------------------------------------------
            # SELECTBOX OCORRÊNCIA
            # ----------------------------------------------------

            chave_seletor_dinamico = (
                f"seletor_ocorrencia_{aba_selecionada}"
            )

            titulo_selecionado = st.selectbox(
                "Selecione o Tipo de Ocorrência:",
                options=opcoes_combo,
                key=chave_seletor_dinamico,
            )


            # ----------------------------------------------------
            # ESTADO INICIAL
            # ----------------------------------------------------

            if (
                titulo_selecionado
                == "Escolha a Ocorrência..."
            ):

                st.info(
                    "ℹ️ Por favor, selecione o tipo "
                    "de ocorrência desejado."
                )


            # ----------------------------------------------------
            # PADRÃO NÃO ENCONTRADO
            # ----------------------------------------------------

            elif (
                titulo_selecionado
                == "Padrão não encontrado"
            ):

                st.dataframe(
                    df_bruto,
                    use_container_width=True,
                )


            # ----------------------------------------------------
            # OCORRÊNCIA SELECIONADA
            # ----------------------------------------------------

            else:

                st.write("---")

                idx_selecionado = nomes_titulos.index(
                    titulo_selecionado
                )

                linha_inicio_titulo = (
                    indices_titulos[idx_selecionado]
                )

                linha_cabecalho_colunas = (
                    linha_inicio_titulo + 1
                )

                linha_inicio_dados = (
                    linha_inicio_titulo + 2
                )


                if (
                    idx_selecionado + 1
                    < len(indices_titulos)
                ):

                    linha_fim_dados = (
                        indices_titulos[
                            idx_selecionado + 1
                        ]
                    )

                else:

                    linha_fim_dados = len(df_bruto)


                # ------------------------------------------------
                # BLOCO DE DADOS
                # ------------------------------------------------

                df_bloco = df_bruto.iloc[
                    linha_inicio_dados:
                    linha_fim_dados
                ].copy()


                nomes_colunas = []

                for i in range(
                    df_bloco.shape[1]
                ):

                    celula_cabecalho = str(
                        df_bruto.iloc[
                            linha_cabecalho_colunas,
                            i
                        ]
                    ).strip()


                    nomes_colunas.append(
                        celula_cabecalho
                        if (
                            celula_cabecalho.lower()
                            != "nan"
                            and celula_cabecalho
                            != ""
                        )
                        else f"Unnamed_{i}"
                    )


                df_bloco.columns = nomes_colunas

                df_bloco = (
                    df_bloco
                    .dropna(how="all")
                    .reset_index(drop=True)
                )


                # ------------------------------------------------
                # LOCALIZAR COLUNAS
                # ------------------------------------------------

                coluna_ano_real = (
                    df_bloco.columns[0]
                )

                coluna_casos_reais = None


                for col in df_bloco.columns:

                    nome_coluna = str(
                        col
                    ).lower()

                    if "ano" in nome_coluna:

                        coluna_ano_real = col

                    if (
                        "caso" in nome_coluna
                        or "real" in nome_coluna
                    ):

                        coluna_casos_reais = col


                # ------------------------------------------------
                # COLUNAS PERMITIDAS
                # ------------------------------------------------

                colunas_permitidas = []

                for col in df_bloco.columns:

                    c_low = str(col).lower()

                    if "unnamed" not in c_low:

                        if (
                            col == coluna_ano_real
                            or col == coluna_casos_reais
                            or "pa" in c_low
                            or "pg" in c_low
                            or "media" in c_low
                            or "média" in c_low
                        ):

                            colunas_permitidas.append(
                                col
                            )


                df_exibicao = (
                    df_bloco[
                        colunas_permitidas
                    ].copy()
                )


                df_exibicao = df_exibicao[
                    df_exibicao[
                        coluna_ano_real
                    ]
                    .astype(str)
                    .str.strip()
                    .str.isnumeric()
                ]


                # ------------------------------------------------
                # CÁLCULOS
                # ------------------------------------------------

                if (
                    coluna_casos_reais
                    and not df_exibicao.empty
                ):

                    vetor_casos = (
                        df_exibicao[
                            coluna_casos_reais
                        ]
                        .astype(str)
                        .str.replace(
                            ".",
                            "",
                            regex=False,
                        )
                        .str.replace(
                            ",",
                            ".",
                            regex=False,
                        )
                    )


                    numeros_finais = (
                        pd.to_numeric(
                            vetor_casos,
                            errors="coerce",
                        )
                        .to_numpy()
                    )


                    strings_var_final = [
                        "-----"
                    ]

                    valores_per_capita = []


                    if len(numeros_finais) > 0:

                        if pd.isna(
                            numeros_finais[0]
                        ):

                            valores_per_capita.append(
                                "-----"
                            )

                        else:

                            calc_pc = (
                                numeros_finais[0]
                                / populacao_atual
                            ) * 1000

                            valores_per_capita.append(
                                f"{round(calc_pc, 1):.1f}"
                            )


                    for idx in range(
                        1,
                        len(numeros_finais),
                    ):

                        anterior = (
                            numeros_finais[
                                idx - 1
                            ]
                        )

                        atual = (
                            numeros_finais[
                                idx
                            ]
                        )


                        if (
                            pd.isna(anterior)
                            or pd.isna(atual)
                            or anterior == 0
                        ):

                            strings_var_final.append(
                                "-----"
                            )

                        else:

                            calc = (
                                (
                                    atual
                                    - anterior
                                )
                                / anterior
                            ) * 100

                            calc_arredondado = round(
                                calc,
                                1,
                            )


                            if (
                                calc_arredondado
                                == 0.0
                            ):

                                strings_var_final.append(
                                    "-----"
                                )

                            else:

                                strings_var_final.append(
                                    f"{'+' if calc_arredondado > 0 else ''}"
                                    f"{calc_arredondado:.1f}%"
                                )


                        if pd.isna(atual):

                            valores_per_capita.append(
                                "-----"
                            )

                        else:

                            calc_pc = (
                                atual
                                / populacao_atual
                            ) * 1000

                            valores_per_capita.append(
                                f"{round(calc_pc, 1):.1f}"
                            )


                    df_exibicao[
                        "VARIAÇÃO %"
                    ] = strings_var_final

                    df_exibicao[
                        "Taxa por 1.000 Hab."
                    ] = valores_per_capita


                    # Reorganiza colunas

                    todas_cols = list(
                        df_exibicao.columns
                    )


                    if (
                        "VARIAÇÃO %"
                        in todas_cols
                    ):

                        todas_cols.remove(
                            "VARIAÇÃO %"
                        )


                    if (
                        "Taxa por 1.000 Hab."
                        in todas_cols
                    ):

                        todas_cols.remove(
                            "Taxa por 1.000 Hab."
                        )


                    idx_pos = (
                        todas_cols.index(
                            coluna_casos_reais
                        )
                    )


                    todas_cols.insert(
                        idx_pos + 1,
                        "VARIAÇÃO %",
                    )

                    todas_cols.insert(
                        idx_pos + 2,
                        "Taxa por 1.000 Hab.",
                    )


                    df_exibicao = (
                        df_exibicao[
                            todas_cols
                        ]
                    )


                # ------------------------------------------------
                # LIMPAR VALORES
                # ------------------------------------------------

                for coluna in df_exibicao.columns:

                    df_exibicao[coluna] = (
                        df_exibicao[coluna]
                        .astype(str)
                        .str.strip()
                        .replace(
                            [
                                "",
                                "None",
                                "none",
                                "NaN",
                                "nan",
                                None,
                            ],
                            "-----",
                        )
                    )


                # ------------------------------------------------
                # TABELA
                # ------------------------------------------------

                st.subheader(
                    f"📋 Tabela de Dados — "
                    f"{titulo_selecionado}"
                )


                if not df_exibicao.empty:

                    st.dataframe(
                        df_exibicao,
                        width=950,
                        hide_index=True,
                    )


                    # --------------------------------------------
                    # GRÁFICO
                    # --------------------------------------------

                    if coluna_casos_reais:

                        st.write("---")

                        st.subheader(
                            "📊 Visualização Gráfica"
                        )


                        tipo_grafico = st.radio(
                            "Escolha o formato do gráfico:",
                            options=[
                                "Linha",
                                "Barra",
                            ],
                            horizontal=True,
                            key=(
                                f"radio_"
                                f"{aba_selecionada}_"
                                f"{idx_selecionado}"
                            ),
                        )


                        # ----------------------------------------
                        # CHECKBOXES
                        # ----------------------------------------

                        mapeamento_checkboxes = {}


                        for col in df_exibicao.columns:

                            c_low = col.lower()


                            if (
                                col
                                == coluna_ano_real
                                or col
                                == coluna_casos_reais
                                or "variação"
                                in c_low
                                or "1.000"
                                in c_low
                            ):

                                continue


                            if (
                                "pa" in c_low
                                and "media"
                                not in c_low
                            ):

                                mapeamento_checkboxes[
                                    "Projeções PA"
                                ] = col


                            elif (
                                "pg" in c_low
                                and "media"
                                not in c_low
                            ):

                                mapeamento_checkboxes[
                                    "Projeções PG"
                                ] = col


                            elif (
                                "aumento"
                                in c_low
                            ):

                                mapeamento_checkboxes[
                                    "Aumento"
                                ] = col


                            elif (
                                "redução"
                                in c_low
                            ):

                                mapeamento_checkboxes[
                                    "Redução"
                                ] = col


                        colunas_selecionadas_reais = []


                        if mapeamento_checkboxes:

                            st.markdown(
                                "**Selecione as projeções desejadas:**"
                            )


                            opcoes_labels = list(
                                mapeamento_checkboxes.keys()
                            )


                            cols_checkboxes = st.columns(
                                len(opcoes_labels)
                            )


                            for i, label in enumerate(
                                opcoes_labels
                            ):

                                with cols_checkboxes[i]:

                                    if st.checkbox(
                                        label,
                                        key=(
                                            f"c_"
                                            f"{label}_"
                                            f"{aba_selecionada}_"
                                            f"{idx_selecionado}"
                                        ),
                                    ):

                                        colunas_selecionadas_reais.append(
                                            mapeamento_checkboxes[
                                                label
                                            ]
                                        )


                        # ----------------------------------------
                        # LEGENDA
                        # ----------------------------------------

                        st.markdown(
                            """
                            <div class="legenda-container">

                                <div class="legenda-item">
                                    <div
                                        class="legenda-cor"
                                        style="background-color:#007bff;">
                                    </div>
                                    <span>Casos Reais</span>
                                </div>

                                <div class="legenda-item">
                                    <div
                                        class="legenda-cor"
                                        style="background-color:#28a745;">
                                    </div>
                                    <span>Projeções PA</span>
                                </div>

                                <div class="legenda-item">
                                    <div
                                        class="legenda-cor"
                                        style="background-color:#dc3545;">
                                    </div>
                                    <span>Projeções PG</span>
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


                        # ----------------------------------------
                        # PREPARAR GRÁFICO
                        # ----------------------------------------

                        df_grafico = (
                            df_exibicao.copy()
                        )


                        colunas_para_plotar = (
                            [coluna_casos_reais]
                            + colunas_selecionadas_reais
                        )


                        for col in colunas_para_plotar:

                            df_grafico[col] = (
                                pd.to_numeric(
                                    df_grafico[col]
                                    .astype(str)
                                    .str.replace(
                                        ".",
                                        "",
                                        regex=False,
                                    )
                                    .str.replace(
                                        ",",
                                        ".",
                                        regex=False,
                                    ),
                                    errors="coerce",
                                )
                            )


                        df_grafico[
                            coluna_ano_real
                        ] = pd.to_numeric(
                            df_grafico[
                                coluna_ano_real
                            ],
                            errors="coerce",
                        )


                        df_grafico = (
                            df_grafico
                            .dropna(
                                subset=[
                                    coluna_ano_real
                                ]
                            )
                            .sort_values(
                                by=coluna_ano_real
                            )
                        )


                        # ----------------------------------------
                        # CORES
                        # ----------------------------------------

                        mapeamento_cores = {}


                        for col in colunas_para_plotar:

                            c_low = col.lower()


                            if (
                                col
                                == coluna_casos_reais
                            ):

                                mapeamento_cores[
                                    col
                                ] = "#007bff"


                            elif "pa" in c_low:

                                mapeamento_cores[
                                    col
                                ] = "#28a745"


                            elif "pg" in c_low:

                                mapeamento_cores[
                                    col
                                ] = "#dc3545"


                            else:

                                mapeamento_cores[
                                    col
                                ] = "#6c757d"


                        # ----------------------------------------
                        # FORMATO LONGO
                        # ----------------------------------------

                        df_longo = (
                            df_grafico.melt(
                                id_vars=[
                                    coluna_ano_real
                                ],
                                value_vars=[
                                    *colunas_para_plotar
                                ],
                                var_name="Métrica",
                                value_name="Valores",
                            )
                        )


                        if not df_longo.dropna(
                            subset=["Valores"]
                        ).empty:

                            base = alt.Chart(
                                df_longo
                            ).encode(

                                x=alt.X(
                                    f"{coluna_ano_real}:O",
                                    title="Ano",
                                    axis=alt.Axis(
                                        labelAngle=0
                                    ),
                                ),

                                y=alt.Y(
                                    "Valores:Q",
                                    title="Quantidade de Casos",
                                ),

                                color=alt.Color(
                                    "Métrica:N",
                                    scale=alt.Scale(
                                        domain=list(
                                            mapeamento_cores.keys()
                                        ),
                                        range=list(
                                            mapeamento_cores.values()
                                        ),
                                    ),
                                    legend=None,
                                ),
                            )


                            if tipo_grafico == "Linha":

                                chart = base.mark_line(
                                    strokeWidth=4,
                                    point=alt.OverlayMarkDef(
                                        size=80,
                                        filled=True,
                                    ),
                                )

                            else:

                                chart = (
                                    base.mark_bar()
                                    .encode(
                                        xOffset="Métrica:N"
                                    )
                                )


                            st.markdown(
                                '<div class="grafico-container">',
                                unsafe_allow_html=True,
                            )


                            st.altair_chart(
                                chart.properties(
                                    width=900,
                                    height=450,
                                ).interactive(),
                                use_container_width=False,
                            )


                            st.markdown(
                                "</div>",
                                unsafe_allow_html=True,
                            )


                        else:

                            st.warning(
                                "⚠️ Dados insuficientes "
                                "para plotagem do gráfico."
                            )


                else:

                    st.warning(
                        "⚠️ Bloco sem dados estruturados."
                    )


    except Exception as e:

        st.error(
            f"Erro: {e}"
        )


# ============================================================
# COMPARATIVO GERAL
# ============================================================

else:

    st.subheader(
        "🗺️ Média Geral Histórica por Tipo de "
        "Ocorrência e Região"
    )


    st.write(
        "Selecione o tipo de ocorrência abaixo para "
        "visualizar a tabela com a **média geral "
        "proporcional** (taxa média por 1.000 habitantes "
        "femininas considerando todos os anos disponíveis) "
        "de cada região."
    )


    try:

        primeira_regiao_gid = (
            list(MAPA_REGIOES.values())[0]
        )


        df_modelo = (
            carregar_dados_brutos(
                CHAVE_PLANILHA,
                primeira_regiao_gid,
            )
        )


        nomes_titulos_geral = []


        for idx, row in df_modelo.iterrows():

            celula_texto = str(
                row.iloc[0]
            ).upper()


            if (
                "FATO COMUNICADO"
                in celula_texto
                or "OCORRÊNCIA"
                in celula_texto
            ):

                nomes_titulos_geral.append(
                    str(row.iloc[0]).strip()
                )


        if not nomes_titulos_geral:

            st.warning(
                "⚠️ Não foi possível carregar "
                "as ocorrências padrão."
            )


        else:

            ocorrencia_escolhida = st.selectbox(
                "Selecione a Ocorrência para Média Geral:",
                options=[
                    "Escolha a Ocorrência..."
                ] + nomes_titulos_geral,
            )


            if (
                ocorrencia_escolhida
                != "Escolha a Ocorrência..."
            ):

                st.write("---")


                with st.spinner(
                    "Calculando as médias gerais "
                    "proporcionais de todas as regiões..."
                ):

                    dados_comparativos = []


                    # --------------------------------------------
                    # TODAS AS REGIÕES
                    # --------------------------------------------

                    for nome_reg, gid_reg in (
                        MAPA_REGIOES.items()
                    ):

                        try:

                            df_b = (
                                carregar_dados_brutos(
                                    CHAVE_PLANILHA,
                                    gid_reg,
                                )
                            )


                            # ------------------------------------
                            # POPULAÇÃO
                            # ------------------------------------

                            pop = 1000000


                            if (
                                df_b.shape[0] > 2
                                and df_b.shape[1] > 4
                            ):

                                num_str = re.sub(
                                    r"\D",
                                    "",
                                    str(
                                        df_b.iloc[
                                            2,
                                            4
                                        ]
                                    ),
                                )


                                if num_str:

                                    pop = float(
                                        num_str
                                    )


                            # ------------------------------------
                            # LOCALIZAR OCORRÊNCIA
                            # ------------------------------------

                            idx_titulo = -1


                            for idx, row in (
                                df_b.iterrows()
                            ):

                                if (
                                    str(
                                        row.iloc[0]
                                    ).strip()
                                    == ocorrencia_escolhida
                                ):

                                    idx_titulo = idx
                                    break


                            if (
                                idx_titulo != -1
                                and idx_titulo + 2
                                < len(df_b)
                            ):

                                prox_titulo = (
                                    len(df_b)
                                )


                                for other_idx in range(
                                    idx_titulo + 1,
                                    len(df_b),
                                ):

                                    txt_out = str(
                                        df_b.iloc[
                                            other_idx,
                                            0
                                        ]
                                    ).upper()


                                    if (
                                        "FATO COMUNICADO"
                                        in txt_out
                                        or "OCORRÊNCIA"
                                        in txt_out
                                    ):

                                        prox_titulo = (
                                            other_idx
                                        )

                                        break


                                df_sub = (
                                    df_b.iloc[
                                        idx_titulo + 2:
                                        prox_titulo
                                    ]
                                    .dropna(
                                        how="all"
                                    )
                                )


                                # --------------------------------
                                # COLUNA DE CASOS
                                # --------------------------------

                                col_caso = None


                                for c_idx in range(
                                    df_b.shape[1]
                                ):

                                    c_name = str(
                                        df_b.iloc[
                                            idx_titulo + 1,
                                            c_idx
                                        ]
                                    ).lower()


                                    if (
                                        "caso"
                                        in c_name
                                        or "real"
                                        in c_name
                                    ):

                                        col_caso = c_idx
                                        break


                                if (
                                    col_caso is not None
                                    and not df_sub.empty
                                ):

                                    taxas_anuais = []
                                    casos_totais = []


                                    for (
                                        row_i,
                                        r_val
                                    ) in df_sub.iterrows():

                                        ano_val = str(
                                            r_val.iloc[0]
                                        ).strip()


                                        caso_val_raw = str(
                                            r_val.iloc[
                                                col_caso
                                            ]
                                        ).strip()


                                        if (
                                            ano_val.isdigit()
                                            and caso_val_raw
                                            not in [
                                                "",
                                                "nan",
                                                "None",
                                                "-----",
                                            ]
                                        ):

                                            num_casos = (
                                                pd.to_numeric(
                                                    caso_val_raw
                                                    .replace(
                                                        ".",
                                                        "",
                                                    )
                                                    .replace(
                                                        ",",
                                                        ".",
                                                    ),
                                                    errors="coerce",
                                                )
                                            )


                                            if not pd.isna(
                                                num_casos
                                            ):

                                                taxa_anual = (
                                                    num_casos
                                                    / pop
                                                ) * 1000


                                                taxas_anuais.append(
                                                    taxa_anual
                                                )


                                                casos_totais.append(
                                                    num_casos
                                                )


                                    # ----------------------------
                                    # MÉDIAS
                                    # ----------------------------

                                    if taxas_anuais:

                                        media_taxa = (
                                            sum(
                                                taxas_anuais
                                            )
                                            / len(
                                                taxas_anuais
                                            )
                                        )


                                        media_casos = (
                                            sum(
                                                casos_totais
                                            )
                                            / len(
                                                casos_totais
                                            )
                                        )


                                        dados_comparativos.append(
                                            {
                                                "Região": nome_reg,
                                                "População Feminina": int(
                                                    pop
                                                ),
                                                "Média de Casos Reais": round(
                                                    media_casos,
                                                    1,
                                                ),
                                                "Média da Taxa por 1.000 Hab.": round(
                                                    media_taxa,
                                                    2,
                                                ),
                                            }
                                        )


                        except Exception:

                            continue


                    # --------------------------------------------
                    # RESULTADO
                    # --------------------------------------------

                    if dados_comparativos:

                        df_comp = pd.DataFrame(
                            dados_comparativos
                        )


                        df_comp = (
                            df_comp
                            .sort_values(
                                by=(
                                    "Média da Taxa "
                                    "por 1.000 Hab."
                                ),
                                ascending=False,
                            )
                            .reset_index(drop=True)
                        )


                        st.subheader(
                            "📋 Tabela de Média Geral "
                            f"Histórica — "
                            f"{ocorrencia_escolhida}"
                        )


                        st.dataframe(
                            df_comp,
                            use_container_width=True,
                            hide_index=True,
                        )


                    else:

                        st.warning(
                            "⚠️ Não foram encontrados "
                            "dados suficientes para "
                            "esta ocorrência em todas "
                            "as regiões."
                        )


            else:

                st.info(
                    "ℹ️ Selecione uma ocorrência acima "
                    "para visualizar a média geral "
                    "por região."
                )


    except Exception as e:

        st.error(
            f"Erro ao carregar o comparativo: {e}"
        )