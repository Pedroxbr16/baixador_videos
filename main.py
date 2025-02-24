import streamlit as st
import yt_dlp
import os

def baixar_videos(urls, caminho_destino="./downloads", stop_on_error=False, logger=print):
    # Cria o diretório se não existir
    if not os.path.exists(caminho_destino):
        os.makedirs(caminho_destino)

    # Template para salvar os arquivos de forma OS-agnóstica
    outtmpl = os.path.join(caminho_destino, '%(title)s.%(ext)s')

    # Configuração utilizando cookies.txt
    ydl_opts_cookies = {
        'outtmpl': outtmpl,
        'cookiefile': 'www.youtube.com_cookies',
        'overwrites': True  # Força sobrescrita se o arquivo já existir
    }
    
    # Configuração utilizando cookies do Firefox
    ydl_opts_firefox = {
        'outtmpl': outtmpl,
        'cookiesfrombrowser': ('firefox',),
        'overwrites': True
    }
    
    arquivos_baixados = []
    
    for url in urls:
        try:
            logger(f"\nIniciando download de: {url} utilizando cookies.txt")
            with yt_dlp.YoutubeDL(ydl_opts_cookies) as ydl:
                ydl.download([url])
        except Exception as e:
            error_message = str(e)
            if "Sign in to confirm your age" in error_message:
                logger(f"\nVídeo com restrição de idade detectado: {url}")
                logger("Utilizando cookies do navegador (Firefox) para autenticação...")
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_firefox) as ydl:
                        ydl.download([url])
                except Exception as e2:
                    logger(f"\nErro utilizando cookies do Firefox: {str(e2)}")
                    if stop_on_error:
                        logger("Encerrando o processo de download devido ao erro.")
                        return arquivos_baixados
                    else:
                        continue
            else:
                logger(f"\nErro ao baixar {url}: {error_message}")
                if stop_on_error:
                    logger("Encerrando o processo de download devido ao erro.")
                    return arquivos_baixados
                else:
                    continue
        
        # Após o download, tenta identificar o arquivo baixado
        # Aqui, consideramos que o título do vídeo pode ter sido sanitizado
        # Para simplificar, listamos os arquivos no diretório destino
        for arquivo in os.listdir(caminho_destino):
            caminho_completo = os.path.join(caminho_destino, arquivo)
            # Se o arquivo estiver presente e for recente, adiciona à lista
            arquivos_baixados.append(caminho_completo)
    
    return arquivos_baixados

# Interface Streamlit
st.title("Download de Vídeos Gratuito")
st.write("Use a interface para baixar vídeos e depois faça o download para seu computador.")

# Para deploy, usamos um diretório relativo
default_path = "./downloads"
st.write(f"Os vídeos serão salvos no diretório: **{default_path}** (relativo ao diretório da aplicação)")

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
        lista_urls = [url.strip() for url in urls_input.replace(',', ' ').split() if url.strip()]
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
                    st.download_button(label=f"Baixar {os.path.basename(arquivo)}", data=f, file_name=os.path.basename(arquivo))
        else:
            st.error("Nenhum arquivo foi baixado.")
