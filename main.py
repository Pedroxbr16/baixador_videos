import os
import subprocess
from pathlib import Path

import streamlit as st
import yt_dlp
from yt_dlp.utils import DownloadError

# -----------------------------
# Função para baixar vídeos
# -----------------------------
def baixar_videos(
    urls,
    caminho_destino="./downloads",
    stop_on_error=False,
    logger=print,
):
    # Cria o diretório se não existir
    if not os.path.exists(caminho_destino):
        os.makedirs(caminho_destino)

    outtmpl = os.path.join(caminho_destino, "%(title)s.%(ext)s")

    # Configuração básica (sem tentar burlar restrições da plataforma)
    ydl_opts = {
        "outtmpl": outtmpl,
        "overwrites": True,
        "noplaylist": True,
        "extractor_args": {
            # Evita necessidade de JS runtime moderno em muitos casos
            "youtube": {
                "player_client": ["default"],
            }
        },
    }

    arquivos_baixados = []

    for url in urls:
        try:
            logger(f"\nIniciando download de: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except DownloadError as e:
            msg = str(e)

            if "HTTP Error 403" in msg:
                logger(
                    f"\n⚠ Não foi possível baixar este vídeo "
                    f"(HTTP 403 - acesso negado pela plataforma):\n{url}"
                )
            else:
                logger(f"\nErro ao baixar {url}: {msg}")

            if stop_on_error:
                logger("Encerrando o processo de download devido ao erro.")
                return arquivos_baixados

            continue
        except Exception as e:
            logger(f"\nErro inesperado ao baixar {url}: {e}")
            if stop_on_error:
                logger("Encerrando o processo de download devido ao erro.")
                return arquivos_baixados
            continue

        # Lista os arquivos no diretório destino (simples, mas funciona bem no contexto)
        for arquivo in os.listdir(caminho_destino):
            caminho_completo = os.path.join(caminho_destino, arquivo)
            if (
                os.path.isfile(caminho_completo)
                and caminho_completo not in arquivos_baixados
            ):
                arquivos_baixados.append(caminho_completo)

    return arquivos_baixados


# -----------------------------
# Função para converter arquivos
# -----------------------------
def converter_arquivo(uploaded_file, formato_saida, logger=print, pasta="./convertidos"):
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    # Salva o arquivo enviado em disco
    input_path = os.path.join(pasta, uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    base_name = Path(uploaded_file.name).stem
    output_path = os.path.join(pasta, f"{base_name}.{formato_saida}")

    # Monta comando base do ffmpeg
    cmd = ["ffmpeg", "-y", "-i", input_path]

    # Ajustes simples dependendo do formato de saída
    if formato_saida == "mp3":
        # -vn remove vídeo, bitrate padrão de 192k
        cmd += ["-vn", "-ab", "192k"]
    elif formato_saida == "wav":
        cmd += ["-vn"]
    # para mkv, mp4, ogg deixamos o ffmpeg escolher defaults razoáveis

    cmd.append(output_path)

    logger(f"Executando ffmpeg:\n{' '.join(cmd)}")

    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        logger("Erro na conversão:")
        logger(proc.stderr)
        raise RuntimeError("Falha ao converter arquivo com ffmpeg.")

    logger("Conversão concluída com sucesso!")
    return output_path


# -----------------------------
# Interface Streamlit
# -----------------------------
st.title("Ferramentas de Vídeo")

tab_download, tab_converter = st.tabs(["🎬 Baixar vídeos", "🔁 Converter arquivos"])


# -----------------------------
# ABA 1 – Baixar vídeos
# -----------------------------
with tab_download:
    st.header("Download de Vídeos (quando permitido pela plataforma)")
    st.write(
        "Use esta aba para baixar vídeos permitidos e depois fazer o download "
        "para o seu computador."
    )

    default_path = "./downloads"
    st.write(
        f"Os vídeos serão salvos no diretório: **{default_path}** "
        "(relativo ao diretório da aplicação)."
    )

    urls_input = st.text_area(
        "URLs dos vídeos (uma por linha ou separadas por vírgula/espaço)"
    )

    stop_on_error = st.checkbox(
        "Parar o processo se ocorrer algum erro?", value=False
    )

    log_placeholder = st.empty()

    if st.button("Baixar Vídeos"):
        if not urls_input.strip():
            st.error("Nenhuma URL foi fornecida!")
        else:
            lista_urls = [
                url.strip()
                for url in urls_input.replace(",", " ").split()
                if url.strip()
            ]
            log_messages = []

            def logger(message):
                log_messages.append(str(message))
                log_placeholder.text("\n".join(log_messages))

            logger("Iniciando o processo de download...")
            arquivos = baixar_videos(
                lista_urls,
                default_path,
                stop_on_error,
                logger,
            )
            logger("\nProcesso de download finalizado!")

            if arquivos:
                st.success("Download concluído para os vídeos permitidos!")
                st.write("Arquivos baixados:")

                for arquivo in arquivos:
                    with open(arquivo, "rb") as f:
                        st.download_button(
                            label=f"Baixar {os.path.basename(arquivo)}",
                            data=f,
                            file_name=os.path.basename(arquivo),
                        )
            else:
                st.warning(
                    "Nenhum arquivo foi baixado.\n\n"
                    "- Verifique se as URLs estão corretas; \n"
                    "- Alguns vídeos podem estar protegidos ou bloqueados "
                    "pela plataforma (ex.: erro HTTP 403)."
                )


# -----------------------------
# ABA 2 – Converter arquivos
# -----------------------------
with tab_converter:
    st.header("Converter arquivo de vídeo/áudio")

    st.write(
        "Envie um arquivo de vídeo ou áudio e escolha o formato de saída "
        "para converter usando **ffmpeg**."
    )

    uploaded_file = st.file_uploader(
        "Selecione um arquivo para converter",
        type=[
            "mp4",
            "mkv",
            "mov",
            "avi",
            "mp3",
            "wav",
            "m4a",
            "flac",
            "ogg",
        ],
    )

    formato_saida = st.selectbox(
        "Formato de saída",
        ["mp3", "wav", "mp4", "mkv", "ogg"],
        index=0,
    )

    conv_log_placeholder = st.empty()
    conv_log_messages = []

    def conv_logger(msg):
        conv_log_messages.append(str(msg))
        conv_log_placeholder.text("\n".join(conv_log_messages))

    if st.button("Converter arquivo"):
        if not uploaded_file:
            st.error("Envie um arquivo primeiro.")
        else:
            conv_logger("Iniciando conversão...")
            try:
                caminho_saida = converter_arquivo(
                    uploaded_file,
                    formato_saida,
                    logger=conv_logger,
                    pasta="./convertidos",
                )
                conv_logger(f"Arquivo convertido salvo em: {caminho_saida}")

                with open(caminho_saida, "rb") as f:
                    st.success("Conversão concluída!")
                    st.download_button(
                        label=f"Baixar arquivo convertido ({os.path.basename(caminho_saida)})",
                        data=f,
                        file_name=os.path.basename(caminho_saida),
                    )
            except Exception as e:
                st.error(f"Erro na conversão: {e}")
