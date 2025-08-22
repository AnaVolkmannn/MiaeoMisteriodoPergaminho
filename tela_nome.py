import pygame
import sys
import requests
from tela_inicial import executar_tela_inicial

def executar_tela_nome():
    pygame.init()
    pygame.mixer.init()

    som_clique = pygame.mixer.Sound("audio/cliquebotao.mp3")
    som_clique.set_volume(0.1)

    largura, altura = 1280, 720
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Mia e o Mistério do Pergaminho")
    relogio = pygame.time.Clock()

    # Recursos visuais
    fundo = pygame.image.load("img/telanome.png")
    fundo = pygame.transform.scale(fundo, (largura, altura))

    img_botao_continuar = pygame.image.load("img/botaocontinuar.png").convert_alpha()

    # === BOTÃO HOME com redimensionamento ===
    TAMANHO_BOTAO_HOME = (78, 78)

    img_botaohome_original = pygame.image.load("img/botaohome_hover.png").convert_alpha()
    img_botaohome_hover_original = pygame.image.load("img/botaohome.png").convert_alpha()

    img_botaohome = pygame.transform.scale(img_botaohome_original, TAMANHO_BOTAO_HOME)
    img_botaohome_hover = pygame.transform.scale(img_botaohome_hover_original, TAMANHO_BOTAO_HOME)

    botaohome_pos = (50, altura - TAMANHO_BOTAO_HOME[1] - 50)
    botaohome_rect = pygame.Rect(botaohome_pos, TAMANHO_BOTAO_HOME)

    # Cursor personalizado
    cursor_img = pygame.image.load("img/cursor.png").convert_alpha()
    pygame.mouse.set_visible(False)

    # Fontes
    fonte_principal = pygame.font.Font("fonts/GROBOLD.ttf", 40)
    fonte_explicativa = pygame.font.Font("fonts/RomanAntique.ttf", 50)
    fonte_erro = pygame.font.SysFont("GROBOLD", 28, bold=True)

    input_ativo = True
    nome_digitado = ""
    mostrar_erro = False

    cor_input = (255, 255, 255)

    input_rect = pygame.Rect(250, 350, 400, 60)
    botao_pos = [300, 450]
    botao_size_original = (301, 90)

    # === FADE IN ===
    def fade_in():
        fade_surface = pygame.Surface((largura, altura))
        fade_surface.fill((0, 0, 0))
        for alpha in range(255, -1, -15):
            tela.blit(fundo, (0, 0))
            fade_surface.set_alpha(alpha)
            tela.blit(fade_surface, (0, 0))
            pygame.display.update()
            relogio.tick(60)

    fade_in()

    while True:
        tela.blit(fundo, (0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and input_ativo:
                if evento.key == pygame.K_RETURN:
                    pass
                elif evento.key == pygame.K_BACKSPACE:
                    nome_digitado = nome_digitado[:-1]
                else:
                    if len(nome_digitado) < 20:
                        nome_digitado += evento.unicode
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_rect.collidepoint(evento.pos):
                    som_clique.play()
                #    if nome_digitado.strip() == "":
                #        mostrar_erro = True
                #    else:
                 #       try:
                #            resposta = requests.post("http://127.0.0.1:5000/players", json={"nome": nome_digitado})
                #            if resposta.status_code == 201:
                #                print("Nome salvo com sucesso:", resposta.json())
                #                return
                #            else:
                 #               print("Erro ao salvar:", resposta.json())
                 #       except Exception as e:
                #           print("Erro de conexão com a API:", e)
                elif botaohome_rect.collidepoint(evento.pos):
                    som_clique.play()
                    pygame.mixer.quit()
                    executar_tela_inicial()
                    return

        # Texto explicativo
        linha1 = "Antes de começarmos,"
        linha2 = "diga-nos quem é você..."

        texto_linha1 = fonte_explicativa.render(linha1, True, (0, 0, 0))
        texto_linha2 = fonte_explicativa.render(linha2, True, (0, 0, 0))
        x_central = largura // 2.8
        tela.blit(texto_linha1, texto_linha1.get_rect(center=(x_central, input_rect.y - 110)))
        tela.blit(texto_linha2, texto_linha2.get_rect(center=(x_central, input_rect.y - 70)))

        # Campo de texto
        texto_input = fonte_principal.render(nome_digitado or "Digite seu nome...", True, cor_input)
        tela.blit(texto_input, (input_rect.x + 10, input_rect.y + 10))

        # Botão CONTINUAR com hover proporcional
        mouse_pos = pygame.mouse.get_pos()
        botao_base_rect = pygame.Rect(botao_pos[0], botao_pos[1], *botao_size_original)
        is_hover_continuar = botao_base_rect.collidepoint(mouse_pos)

        escala = 1.1 if is_hover_continuar else 1.0
        nova_largura = int(botao_size_original[0] * escala)
        nova_altura = int(botao_size_original[1] * escala)

        botao_img = pygame.transform.smoothscale(img_botao_continuar, (nova_largura, nova_altura))
        offset_x = (nova_largura - botao_size_original[0]) // 2
        offset_y = (nova_altura - botao_size_original[1]) // 2

        nova_pos = (botao_pos[0] - offset_x, botao_pos[1] - offset_y)
        botao_rect = botao_img.get_rect(topleft=nova_pos)

        tela.blit(botao_img, nova_pos)

        texto_botao = fonte_principal.render("CONTINUAR", True, (255, 215, 0))
        texto_botao_rect = texto_botao.get_rect(center=botao_rect.center)
        tela.blit(texto_botao, texto_botao_rect)

        # Botão Home com hover
        if botaohome_rect.collidepoint(mouse_pos):
            tela.blit(img_botaohome_hover, botaohome_pos)
        else:
            tela.blit(img_botaohome, botaohome_pos)

        # Mensagem de erro
        if mostrar_erro:
            msg = fonte_erro.render("Nome precisa ser preenchido!", True, (255, 255, 255))
            tela.blit(msg, (input_rect.x + 580, input_rect.y - 280))

        # Cursor
        tela.blit(cursor_img, mouse_pos)

        pygame.display.update()
        relogio.tick(60)