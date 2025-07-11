import pygame
import sys
import math

def executar_tela_inicial():
    pygame.init()
    pygame.mixer.init()
    som_clique = pygame.mixer.Sound("cliquebotao.mp3")
    som_clique.set_volume(0.1)

    # Música
    pygame.mixer.music.load("musicafundoinicial.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    tela = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Mia e o Mistério do Pergaminho")
    relogio = pygame.time.Clock()

    COR_TEXTO = (255, 255, 255)
    fonte = pygame.font.Font("GROBOLD.ttf", 38)

    fundo = pygame.image.load("telainicial.jpeg")
    fundo = pygame.transform.scale(fundo, (1280, 720))

    pygame.mouse.set_visible(False)
    cursor_img = pygame.image.load("cursor.png").convert_alpha()

    logo = pygame.image.load("logo.png").convert_alpha()

    img_botao_normal = pygame.image.load("botao.png").convert_alpha()
    img_botao_hover = pygame.image.load("botao_hover.png").convert_alpha()

    botoes = [
        ("JOGAR", 500, 380, 250, 110),
        ("SAIR", 525, 560, 200, 80),
    ]

    som_on = pygame.image.load("som_on.png").convert_alpha()
    som_on_hover = pygame.image.load("som_on_hover.png").convert_alpha()
    som_off = pygame.image.load("som_off.png").convert_alpha()
    som_off_hover = pygame.image.load("som_off_hover.png").convert_alpha()

    botao_mute_rect = pygame.Rect(1170, 30, 68, 68)
    som_mutado = False

    def desenhar_botao(texto, x, y, largura_base, altura_base, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        largura = largura_base
        altura = altura_base
        imagem = img_botao_normal

        ret_base = pygame.Rect(x, y, largura_base, altura_base)
        is_hover = ret_base.collidepoint(mouse_pos)

        if is_hover:
            largura += 10
            altura += 10
            imagem = img_botao_hover

        offset_x = (largura_base - largura) // 2
        offset_y = (altura_base - altura) // 2

        imagem = pygame.transform.scale(imagem, (largura, altura))
        tela.blit(imagem, (x + offset_x, y + offset_y))

        texto_render = fonte.render(texto, True, COR_TEXTO)
        texto_rect = texto_render.get_rect(center=(x + largura_base // 2, y + altura_base // 2))
        tela.blit(texto_render, texto_rect)

    def desenhar_botao_mute(mutado, mouse_pos):
        is_hover = botao_mute_rect.collidepoint(mouse_pos)
        imagem = som_off_hover if mutado and is_hover else \
                 som_off if mutado else \
                 som_on_hover if is_hover else som_on

        largura_base, altura_base = botao_mute_rect.size

        if is_hover:
            escala = 1.3
            nova_largura = int(largura_base * escala)
            nova_altura = int(altura_base * escala)
            imagem = pygame.transform.smoothscale(imagem, (nova_largura, nova_altura))
            offset_x = (nova_largura - largura_base) // 2
            offset_y = (nova_altura - altura_base) // 2
            tela.blit(imagem, (botao_mute_rect.x - offset_x, botao_mute_rect.y - offset_y))
        else:
            tela.blit(imagem, botao_mute_rect.topleft)

    def transicao_fadeout():
        fade_surface = pygame.Surface((1280, 720))
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 255, 10):
            tela.blit(fundo, (0, 0))
            deslocamento_y = math.sin(tempo) * 10
            pos_logo_x = (1280 - logo.get_width()) // 2
            pos_logo_y = 20 + deslocamento_y
            tela.blit(logo, (pos_logo_x, pos_logo_y))

            for texto, bx, by, bw, bh in botoes:
                desenhar_botao(texto, bx, by, bw, bh, pygame.mouse.get_pos())

            desenhar_botao_mute(som_mutado, pygame.mouse.get_pos())

            mouse_x, mouse_y = pygame.mouse.get_pos()
            tela.blit(cursor_img, (mouse_x, mouse_y))

            fade_surface.set_alpha(alpha)
            tela.blit(fade_surface, (0, 0))

            pygame.display.update()
            relogio.tick(60)

    tempo = 0
    rodando = True

    while rodando:
        tempo += 0.03
        deslocamento_y = math.sin(tempo) * 10
        tela.blit(fundo, (0, 0))

        pos_logo_x = (1280 - logo.get_width()) // 2
        pos_logo_y = 20 + deslocamento_y
        tela.blit(logo, (pos_logo_x, pos_logo_y))

        mouse_pos = pygame.mouse.get_pos()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = mouse_pos
                for texto, bx, by, bw, bh in botoes:
                    ret_botao = pygame.Rect(bx, by, bw, bh)
                    if ret_botao.collidepoint((mx, my)):
                        if not som_mutado:
                            som_clique.play()
                        print(f"Botão '{texto}' clicado!")
                        if texto == "SAIR":
                            pygame.quit()
                            sys.exit()
                        elif texto == "JOGAR":
                            transicao_fadeout()
                            import tela_nome
                            tela_nome.executar_tela_nome()
                            rodando = False

                if botao_mute_rect.collidepoint((mx, my)):
                    if not som_mutado:
                        som_clique.play()
                    som_mutado = not som_mutado
                    pygame.mixer.music.set_volume(0 if som_mutado else 0.2)

        for texto, bx, by, bw, bh in botoes:
            desenhar_botao(texto, bx, by, bw, bh, mouse_pos)

        desenhar_botao_mute(som_mutado, mouse_pos)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        tela.blit(cursor_img, (mouse_x, mouse_y))

        pygame.display.update()
        relogio.tick(60)

    pygame.quit()
    sys.exit()
