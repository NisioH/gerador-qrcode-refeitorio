import streamlit as st
import pandas as pd
import qrcode
import os

# Configurações da aba do navegador
st.set_page_config(page_title="Gerador de QR Code", page_icon="🍽️", layout="centered")

st.title("Gerador de QR Code")
st.subheader("Controle de Refeitório - Fazenda")


# Função central para gerar a imagem
def gerar_qr(inscricao, nome, secao):
    pasta_saida = "qrcodes_gerados"
    os.makedirs(pasta_saida, exist_ok=True)

    dados_qr = f"{inscricao}|{nome}|{secao}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10,
                       border=4)
    qr.add_data(dados_qr)
    qr.make(fit=True)

    imagem = qr.make_image(fill_color="black", back_color="white")
    nome_arquivo = f"{inscricao}_{nome.replace(' ', '_')}.png"
    caminho_completo = os.path.join(pasta_saida, nome_arquivo)
    imagem.save(caminho_completo)

    return caminho_completo


# Criando as abas
tab_planilha, tab_manual = st.tabs(["📋 Lote (Planilha)", "👤 Cadastro Avulso"])

# --- ABA 1: PLANILHA ---
with tab_planilha:
    st.info(
        "Importe a planilha do RH para gerar vários QR Codes de uma vez. Colunas obrigatórias: "
        "**Nome**, **Inscrição**, **Seção**.")

    arquivo_upload = st.file_uploader("Selecione a Planilha (.xlsx)", type=["xlsx", "xls"])

    if arquivo_upload is not None:
        if st.button("Gerar QR Codes em Lote", type="primary"):
            try:
                df = pd.read_excel(arquivo_upload)
                colunas_necessarias = ['Nome', 'Inscrição', 'Seção']

                if not all(col in df.columns for col in colunas_necessarias):
                    st.error(f"Erro: A planilha deve conter as colunas exatas: {', '.join(colunas_necessarias)}")
                else:
                    barra_progresso = st.progress(0)
                    total = len(df)

                    for index, row in df.iterrows():
                        gerar_qr(str(row['Inscrição']), str(row['Nome']), str(row['Seção']))
                        barra_progresso.progress((index + 1) / total)

                    st.success(f"Sucesso! {total} QR Codes foram salvos na pasta 'qrcodes_gerados'.")
            except Exception as ex:
                st.error(f"Erro ao processar o arquivo: {str(ex)}")

# --- ABA 2: MANUAL ---
with tab_manual:
    col1, col2 = st.columns(2)

    with col1:
        inscricao = st.text_input("Inscrição (Ex: 10452)")
        secao = st.text_input("Seção (Ex: Manutenção, Colheita)")
    with col2:
        nome = st.text_input("Nome Completo")

    if st.button("Gerar QR Code Único", type="primary"):
        if not inscricao or not nome or not secao:
            st.warning("Por favor, preencha todos os campos!")
        else:
            try:
                # Gera o QR Code e pega o caminho onde foi salvo
                caminho_img = gerar_qr(inscricao, nome, secao)
                nome_arquivo = os.path.basename(caminho_img)

                st.success(f"QR Code de {nome} gerado com sucesso!")

                # Exibe a imagem na tela
                st.image(caminho_img, caption=f"{inscricao} - {nome}", width=200)

                # NOVO: Lê a imagem salva e cria o botão de download
                with open(caminho_img, "rb") as file:
                    st.download_button(
                        label="⬇️ Baixar Imagem do QR Code",
                        data=file,
                        file_name=nome_arquivo,
                        mime="image/png"
                    )

            except Exception as ex:
                st.error(f"Erro ao gerar: {str(ex)}")