import pygame
import sys

def executar_minigame4():
    largura, altura = 960, 540
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Minigame 4 - Números Romanos")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont(None, 60)

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False  # sai do minigame e volta pro mapa

        tela.fill((200, 180, 150))
        texto = fonte.render("Bem-vindo ao Minigame 4!", True, (50, 30, 10))
        tela.blit(texto, (200, 200))

        pygame.display.flip()
        relogio.tick(60)