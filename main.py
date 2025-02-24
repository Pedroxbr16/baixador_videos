import streamlit as st
import yt_dlp
import os

def baixar_videos(urls, caminho_destino=".", stop_on_error=False, logger=print):
    # Cria o diretório se não existir
    if not os.path.exists(caminho_destino):
        os.makedirs(caminho_destino)

    # Configuração utilizando o arquivo de cookies exportado (cookies.txt)
    ydl_opts_cookies = {
        'outtmpl': f'{caminho_destino}/%(title)s.%(ext)s',
        'cookiefile': 'www.youtube.com_cookies'  # Certifique-se de que este arquivo esteja atualizado
    }
    
    # Configuração utilizando os cookies do navegador Firefox (perfil padrão)
    ydl_opts_firefox = {
        'outtmpl': f'{caminho_destino}/%(title)s.%(ext)s',
        'cookiesfrombrowser': ('firefox',)
    }
    
    for url in urls:
        try:
            logger(f"\nIniciando download de: {url} utilizando cookies.txt")
            with yt_dlp.YoutubeDL(ydl_opts_cookies) as ydl:
                ydl.download([url])
        except Exception as e:
            error_message = str(e)
            # Se o erro indicar restrição de idade, utiliza cookies do Firefox
            if "Sign in to confirm your age" in error_message:
                logger(f"\nVídeo com restrição de idade detectado: {url}")
                logger("Utilizando cookies do navegador (Firefox) para autenticação...")
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_firefox) as ydl:
                        ydl.download([url])
                except Exception as e2:
                    error_message_firefox = str(e2)
                    logger(f"\nErro utilizando cookies do Firefox: {error_message_firefox}")
                    if stop_on_error:
                        logger("Encerrando o processo de download devido ao erro.")
                        return
                    else:
                        continue  # Pula o vídeo problemático e continua
            else:
                # Para outros erros, exibe a mensagem e decide o que fazer conforme a opção
                logger(f"\nErro ao baixar {url}: {error_message}")
                if stop_on_error:
                    logger("Encerrando o processo de download devido ao erro.")
                    return
                else:
                    continue

# Define o caminho padrão para a pasta Downloads do Windows, se aplicável
if os.name == 'nt':  # Verifica se o sistema é Windows
    caminho_padrao = os.path.join(os.environ['USERPROFILE'], 'Downloads')
else:
    caminho_padrao = "."

# Interface Streamlit
st.title("Download de Vídeos Gratuito")
st.write("Utilize a interface abaixo para baixar vídeos informando as URLs e o diretório de destino.")

# Entrada do diretório de destino já configurada para a pasta Downloads do Windows (se estiver no Windows)
caminho = st.text_input("Caminho para salvar os vídeos", value=caminho_padrao)

# Entrada das URLs
urls_input = st.text_area("URLs dos vídeos (informe uma por linha ou separadas por vírgula/espaço)")

# Opção para interromper o download caso ocorra algum erro
stop_on_error = st.checkbox("Parar o processo se ocorrer algum erro?", value=False)

# Área para exibição dos logs
log_placeholder = st.empty()

if st.button("Baixar Vídeos"):
    if not urls_input.strip():
        st.error("Nenhuma URL foi fornecida!")
    else:
        # Processa as URLs informadas (removendo espaços em branco e separando por vírgula, espaço ou nova linha)
        lista_urls = [url.strip() for url in urls_input.replace(',', ' ').split() if url.strip()]
        log_messages = []

        # Função para registrar mensagens na interface
        def logger(message):
            log_messages.append(message)
            log_placeholder.text("\n".join(log_messages))

        logger("Iniciando o processo de download...")
        baixar_videos(lista_urls, caminho, stop_on_error, logger)
        logger("\nProcesso de download finalizado!")
        st.success("Download concluído!")
