import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import zipfile

# Configurações da aba do navegador
st.set_page_config(page_title="Gerador de QR Code", page_icon="🍽️", layout="centered")

st.title("Gerador de QR Code")
st.subheader("Controle de Refeitório - Fazenda")


# Função pra gerar o qrcode
def gerar_qr_bytes(inscricao, nome, secao):
    dados_qr = f"{inscricao}|{nome}|{secao}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(dados_qr)
    qr.make(fit=True)

    imagem = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)

    nome_arquivo = f"{inscricao}_{nome.replace(' ', '_')}.png"
    return buffer, nome_arquivo


# Criando as abas
tab_planilha, tab_manual = st.tabs(["📋 Lote (Planilha)", "👤 Cadastro Avulso"])

with tab_planilha:
    st.info(
        "Importe a planilha do RH para gerar vários QR Codes de uma vez. Colunas obrigatórias: "
        "**Nome**, **Inscrição**, **Seção**."
    )

    arquivo_upload = st.file_uploader("Selecione a Planilha (.xlsx)", type=["xlsx", "xls"])

    if arquivo_upload is not None:
        if st.button("Gerar QR Codes em Lote", type="primary"):
            try:
                df = pd.read_excel(arquivo_upload)
                colunas_necessarias = ['Nome', 'Inscrição', 'Seção']

                if not all(col in df.columns for col in colunas_necessarias):
                    st.error(
                        f"Erro: A planilha deve conter as colunas exatas: "
                        f"{', '.join(colunas_necessarias)}"
                    )
                else:
                    barra_progresso = st.progress(0)
                    total = len(df)

                    # zip pra depois baixar
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for index, row in df.iterrows():
                            img_buffer, nome_arquivo = gerar_qr_bytes(
                                str(row['Inscrição']),
                                str(row['Nome']),
                                str(row['Seção'])
                            )
                            zip_file.writestr(nome_arquivo, img_buffer.getvalue())
                            barra_progresso.progress((index + 1) / total)

                    zip_buffer.seek(0)

                    st.success(f"Sucesso! {total} QR Codes prontos para download.")

                    st.download_button(
                        label="⬇️ Baixar todos os QR Codes (.zip)",
                        data=zip_buffer,
                        file_name="qrcodes_refeitorio.zip",
                        mime="application/zip",
                        type="primary",
                    )
            except Exception as ex:
                st.error(f"Erro ao processar o arquivo: {str(ex)}")

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
                img_buffer, nome_arquivo = gerar_qr_bytes(inscricao, nome, secao)

                st.success(f"QR Code de {nome} gerado com sucesso!")

                # Exibe a imagem na tela
                st.image(img_buffer, caption=f"{inscricao} - {nome}", width=200)

                img_buffer.seek(0)  # garante o ponteiro no início
                st.download_button(
                    label="⬇️ Baixar Imagem do QR Code",
                    data=img_buffer,
                    file_name=nome_arquivo,
                    mime="image/png",
                )
            except Exception as ex:
                st.error(f"Erro ao gerar: {str(ex)}")