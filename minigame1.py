import pygame
import sys

def executar_minigame1():
    pygame.init()

    # Tamanho da tela
    largura, altura = 960, 540
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Minigame 1 - Números Romanos")

    # === CARREGAR IMAGENS ===
    fundo = pygame.image.load("img/fundoColiseu.png").convert()
    madeira = pygame.image.load("img/madeiraGame01.png").convert_alpha()

    # Redimensionar imagens
    fundo = pygame.transform.scale(fundo, (largura, altura))

    # 🔹 AQUI VOCÊ AJUSTA O TAMANHO DA MADEIRA 🔹
    # Quanto maior os números, maior a madeira
    largura_madeira = 950   # antes era 500
    altura_madeira = 750    # antes era 250
    madeira = pygame.transform.scale(madeira, (largura_madeira, altura_madeira))

    # Fonte e relógio
    fonte = pygame.font.SysFont(None, 50)
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False  # sai do minigame e volta pro mapa

        # === DESENHAR NA TELA ===
        tela.blit(fundo, (0, 0))  # fundo do Coliseu

        # painel de madeira centralizado
        pos_x = (largura - madeira.get_width()) // 2
        pos_y = (altura - madeira.get_height()) // 2
        tela.blit(madeira, (pos_x, pos_y))


        # atualiza a tela
        pygame.display.flip()
        relogio.tick(60)

# Executa o minigame
executar_minigame1()
