import pygame

# Configurações
TILE_W, TILE_H = 32, 32     # tamanho real dos blocos no magecity.png
TILESET_PATH = "magecity.png"

def main():
    pygame.init()

    # Carrega a imagem (sem convert ainda)
    raw_img = pygame.image.load(TILESET_PATH)
    sheet_w, sheet_h = raw_img.get_size()

    cols = sheet_w // TILE_W
    rows = sheet_h // TILE_H
    WIDTH, HEIGHT = cols * TILE_W, rows * TILE_H

    # Cria a janela
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Debug Tileset - magecity.png")

    # Agora converte pra usar no Pygame
    imagem = raw_img.convert_alpha()

    # Corta o tileset (com checagem de borda segura)
    tiles = []
    for y in range(0, rows * TILE_H, TILE_H):       # garante que não passa
        linha = []
        for x in range(0, cols * TILE_W, TILE_W):   # garante que não passa
            rect = pygame.Rect(x, y, TILE_W, TILE_H)
            tile = imagem.subsurface(rect).copy()
            linha.append(tile)
        tiles.append(linha)

    font = pygame.font.SysFont("consolas", 14)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((50, 50, 50))

        for row, linha in enumerate(tiles):
            for col, img in enumerate(linha):
                x, y = col * TILE_W, row * TILE_H
                screen.blit(img, (x, y))

                # escreve índice (linha,coluna)
                txt = font.render(f"({row},{col})", True, (255, 0, 0))
                screen.blit(txt, (x + 2, y + 2))

                # desenha grade
                pygame.draw.rect(screen, (200, 200, 200), (x, y, TILE_W, TILE_H), 1)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
