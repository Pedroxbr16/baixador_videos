import yt_dlp
import os

def baixar_videos(urls, caminho_destino="."):
    # Cria o diretório se não existir
    if not os.path.exists(caminho_destino):
        os.makedirs(caminho_destino)

    # Configuração utilizando o arquivo de cookies exportado (cookies.txt)
    ydl_opts_cookies = {
        'outtmpl': f'{caminho_destino}/%(title)s.%(ext)s',
        'cookiefile': 'www.youtube.com_cookies'  # Certifique-se de que este arquivo esteja atualizado
    }
    
    # Configuração utilizando os cookies do navegador Firefox (perfil padrão)
    ydl_opts_firefox = {
        'outtmpl': f'{caminho_destino}/%(title)s.%(ext)s',
        'cookiesfrombrowser': ('firefox',)
    }
    
    for url in urls:
        try:
            # Tenta primeiro baixar com cookies.txt
            print(f"\nIniciando download de: {url} utilizando cookies.txt")
            with yt_dlp.YoutubeDL(ydl_opts_cookies) as ydl:
                ydl.download([url])
        except Exception as e:
            error_message = str(e)
            # Se o erro indicar restrição de idade, usa diretamente os cookies do Firefox
            if "Sign in to confirm your age" in error_message:
                print(f"\nVídeo com restrição de idade detectado: {url}")
                print("Utilizando cookies do navegador (Firefox) para autenticação...")
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_firefox) as ydl:
                        ydl.download([url])
                except Exception as e2:
                    error_message_firefox = str(e2)
                    print(f"\nErro utilizando cookies do Firefox: {error_message_firefox}")
                    escolha = input("Deseja ignorar este vídeo e continuar com os demais? (S/N): ").strip().lower()
                    if escolha == 's':
                        continue  # Pula o vídeo problemático e continua
                    else:
                        print("Encerrando o processo de download.")
                        return
            else:
                # Para outros erros, informa e pergunta se deve continuar
                print(f"\nErro ao baixar {url}: {error_message}")
                escolha = input("Deseja ignorar este vídeo e continuar com os demais? (S/N): ").strip().lower()
                if escolha == 's':
                    continue
                else:
                    print("Encerrando o processo de download.")
                    return

if __name__ == "__main__":
    caminho = input("Digite o caminho onde deseja salvar os vídeos (ENTER para usar o diretório atual): ").strip()
    if not caminho:
        caminho = "."
    
    while True:
        entrada = input("\nDigite as URLs dos vídeos (separadas por espaço ou vírgula): ").strip()
        if not entrada:
            print("Nenhuma URL foi fornecida!")
            continue

        lista_urls = [url.strip() for url in entrada.replace(',', ' ').split() if url.strip()]
        baixar_videos(lista_urls, caminho)
        
        continuar = input("\nDeseja baixar outros vídeos? (S/N): ").strip().lower()
        if continuar != 's':
            print("Encerrando o programa.")
            break
        
        trocar = input(f"Deseja manter o diretório atual ({caminho}) ou trocar? (M/T): ").strip().lower()
        if trocar == 't':
            novo_caminho = input("Digite o novo caminho para salvar os vídeos: ").strip()
            if novo_caminho:
                caminho = novo_caminho
            else:
                print("Caminho inválido. Mantendo o diretório atual.")
