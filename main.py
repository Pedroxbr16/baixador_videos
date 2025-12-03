import streamlit as st
import yt_dlp
import os


def baixar_videos(urls, caminho_destino="./downloads", stop_on_error=False, logger=print):
    # Cria o diretório se não existir
    if not os.path.exists(caminho_destino):
        os.makedirs(caminho_destino)

    # Template para salvar os arquivos de forma OS-agnóstica
    outtmpl = os.path.join(caminho_destino, "%(title)s.%(ext)s")

    # Opções comuns para todos os downloads
    common_ydl_opts = {
        "outtmpl": outtmpl,
        "overwrites": True,  # Força sobrescrita se o arquivo já existir
        # Sugestão oficial do yt-dlp para o warning de JS runtime:
        # --extractor-args "youtube:player_client=default"
        "extractor_args": {
            "youtube": {
                "player_client": ["default"],
            }
        },
        # Evitar playlists (baixar só o link específico)
        "noplaylist": True,
    }

    # Configuração utilizando cookies.txt (se você tiver subido esse arquivo)
    ydl_opts_cookies = {
        **common_ydl_opts,
        "cookiefile": "www.youtube.com_cookies",
    }

    # Configuração para tentar sem cookies (vídeos públicos)
    ydl_opts_sem_cookies = {
        **common_ydl_opts,
    }

    arquivos_baixados = []

    for url in urls:
        baixou = False

        # 1ª tentativa: com cookies.txt (se existir)
        if os.path.exists("www.youtube.com_cookies"):
            try:
                logger(f"\nIniciando download de: {url} utilizando cookies.txt")
                with yt_dlp.YoutubeDL(ydl_opts_cookies) as ydl:
                    ydl.download([url])
                baixou = True
            except Exception as e:
                error_message = str(e)
                logger(f"\nErro ao baixar com cookies.txt: {error_message}")
                # se der erro, tenta sem cookies (desde que não seja para parar)
                if stop_on_error:
                    logger("Encerrando o processo de download devido ao erro.")
                    return arquivos_baixados

        # 2ª tentativa: sem cookies (para vídeos públicos)
        if not baixou:
            try:
                logger(f"\nTentando download de: {url} sem cookies")
                with yt_dlp.YoutubeDL(ydl_opts_sem_cookies) as ydl:
                    ydl.download([url])
                baixou = True
            except Exception as e:
                error_message = str(e)

                # Tratamento específico para restrição de idade
                if "Sign in to confirm your age" in error_message:
                    logger(
                        f"\nVídeo com restrição de idade detectado: {url}\n"
                        "No ambiente do Streamlit Cloud não é possível usar cookies do navegador "
                        "ou autenticação interativa. Esse vídeo não poderá ser baixado aqui."
                    )
                else:
                    logger(f"\nErro ao baixar {url}: {error_message}")

                if stop_on_error:
                    logger("Encerrando o processo de download devido ao erro.")
                    return arquivos_baixados
                else:
                    continue  # pula para a próxima URL

        if baixou:
            # Após o download, lista os arquivos no diretório destino
            for arquivo in os.listdir(caminho_destino):
                caminho_completo = os.path.join(caminho_destino, arquivo)
                # Garante que é arquivo e evita duplicar caminhos na lista
                if os.path.isfile(caminho_completo) and caminho_completo not in arquivos_baixados:
                    arquivos_baixados.append(caminho_completo)

    return arquivos_baixados


# Interface Streamlit
st.title("Download de Vídeos Gratuito")
st.write("Use a interface para baixar vídeos e depois faça o download para seu computador.")

# Para deploy, usamos um diretório relativo
default_path = "./downloads"
st.write(
    f"Os vídeos serão salvos no diretório: **{default_path}** "
    "(relativo ao diretório da aplicação, enquanto o app estiver rodando)."
)

# Entrada das URLs
urls_input = st.text_area("URLs dos vídeos (uma por linha ou separadas por vírgula/espaço)")

# Opção para interromper o download em caso de erro
stop_on_error = st.checkbox("Parar o processo se ocorrer algum erro?", value=False)

# Área para exibição dos logs
log_placeholder = st.empty()

if st.button("Baixar Vídeos"):
    if not urls_input.strip():
        st.error("Nenhuma URL foi fornecida!")
    else:
        lista_urls = [url.strip() for url in urls_input.replace(",", " ").split() if url.strip()]
        log_messages = []

        def logger(message):
            log_messages.append(message)
            log_placeholder.text("\n".join(log_messages))

        logger("Iniciando o processo de download...")
        arquivos = baixar_videos(lista_urls, default_path, stop_on_error, logger)
        logger("\nProcesso de download finalizado!")

        if arquivos:
            st.success("Download concluído!")
            st.write("Arquivos baixados:")
            for arquivo in arquivos:
                # Disponibiliza um botão de download para cada arquivo
                with open(arquivo, "rb") as f:
                    st.download_button(
                        label=f"Baixar {os.path.basename(arquivo)}",
                        data=f,
                        file_name=os.path.basename(arquivo),
                    )
        else:
            st.error("Nenhum arquivo foi baixado.")
