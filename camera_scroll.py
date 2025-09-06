import pygame
from random import randint
import traceback
import os  # <- para carregar sprites

# ---------------------- Configurações básicas ---------------------- #
WIDTH, HEIGHT = 960, 540       # resolução da janela (16:9)
FPS = 60
TILE = 48                      # tamanho de cada tile em px
MAP_W, MAP_H = 80, 60          # tamanho do mapa em tiles

# Cores
COLOR_GRASS  = (139, 115, 85)
COLOR_DIRT   = (168, 124, 84)
COLOR_WATER  = (64, 120, 255)
COLOR_ROCK   = (110, 110, 110)
COLOR_PLAYER = (230, 230, 80)
COLOR_UI     = (0, 0, 0)

# Velocidade do player
PLAYER_SPEED = 220  # px/seg

# Sprites
SPRITES_BASE_PATH = os.path.join("sprites", "mia")
SPRITE_TARGET_SIZE = (192, 192)    # tamanho final de cada frame na tela (ajuste se necessário)
ANIM_FPS = 10.0                  # fps da animação de caminhada


# ---------------------- Util ---------------------- #
def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def carregar_sprites_direcao(base_path: str, direcao: str, frames: int = 6):
    """Carrega e redimensiona os frames para uma dada direção."""
    imagens = []
    pasta = os.path.join(base_path, direcao)
    for i in range(1, frames + 1):
        caminho = os.path.join(pasta, f"{i}.png")
        img = pygame.image.load(caminho).convert_alpha()
        if SPRITE_TARGET_SIZE:
            img = pygame.transform.smoothscale(img, SPRITE_TARGET_SIZE)
        imagens.append(img)
    return imagens


# ---------------------- Câmera ---------------------- #
class Camera:
    """Gerencia o deslocamento (offset) da cena em relação à tela."""
    SMOOTH = 0
    QUADROS = 1

    def __init__(self, world_w_px: int, world_h_px: int):
        self.world_w_px = world_w_px
        self.world_h_px = world_h_px
        self.mode = Camera.SMOOTH
        self.offset_x = 0.0
        self.offset_y = 0.0

    def toggle_mode(self):
        self.mode = Camera.QUADROS if self.mode == Camera.SMOOTH else Camera.SMOOTH

    def update(self, target_rect: pygame.Rect, dt: float):
        if self.mode == Camera.SMOOTH:
            self._follow_smooth(target_rect, dt)
        else:
            self._follow_screens(target_rect)

    def _follow_smooth(self, target_rect: pygame.Rect, dt: float):
        desired_x = target_rect.centerx - WIDTH // 2
        desired_y = target_rect.centery - HEIGHT // 2
        desired_x = max(0, min(desired_x, self.world_w_px - WIDTH))
        desired_y = max(0, min(desired_y, self.world_h_px - HEIGHT))
        smooth = 10.0 * dt
        self.offset_x = lerp(self.offset_x, desired_x, smooth)
        self.offset_y = lerp(self.offset_y, desired_y, smooth)

    def _follow_screens(self, target_rect: pygame.Rect):
        screen_x = target_rect.centerx // WIDTH
        screen_y = target_rect.centery // HEIGHT
        desired_x = int(screen_x) * WIDTH
        desired_y = int(screen_y) * HEIGHT
        desired_x = max(0, min(desired_x, self.world_w_px - WIDTH))
        desired_y = max(0, min(desired_y, self.world_h_px - HEIGHT))
        self.offset_x = float(desired_x)
        self.offset_y = float(desired_y)

    @property
    def offset(self):
        return int(self.offset_x), int(self.offset_y)


# ---------------------- Tilemap dummy ---------------------- #
class TileMap:
    def __init__(self, w_tiles: int, h_tiles: int, tile_size: int):
        self.w = w_tiles
        self.h = h_tiles
        self.size = tile_size
        self.data = self._gen()

    def _gen(self):
        data = [[0 for _ in range(self.w)] for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                r = randint(0, 100)
                if r < 4:
                    data[y][x] = 2  # água
                elif r < 12:
                    data[y][x] = 1  # terra
                elif r < 16:
                    data[y][x] = 3  # rocha
                else:
                    data[y][x] = 0  # grama
        return data

    def draw(self, surf: pygame.Surface, offset: tuple[int, int]):
        offx, offy = offset
        first_x = max(0, offx // self.size)
        first_y = max(0, offy // self.size)
        last_x  = min(self.w, (offx + WIDTH) // self.size + 2)
        last_y  = min(self.h, (offy + HEIGHT) // self.size + 2)

        for y in range(first_y, last_y):
            for x in range(first_x, last_x):
                tile = self.data[y][x]
                if tile == 0:
                    color = COLOR_GRASS
                elif tile == 1:
                    color = COLOR_DIRT
                elif tile == 2:
                    color = COLOR_WATER
                else:
                    color = COLOR_ROCK
                rx = x * self.size - offx
                ry = y * self.size - offy
                pygame.draw.rect(surf, color, (rx, ry, self.size, self.size))


# ---------------------- Player (com sprites) ---------------------- #
class Player:
    """
    Usa um retângulo de colisão (28x36) e desenha o sprite alinhado pelos pés.
    A animação troca os frames quando movendo; parado usa frame 0 da direção atual.
    """
    def __init__(self, x: int, y: int):
        # Retângulo de colisão
        self.rect = pygame.Rect(x, y, 28, 36)

        # Direção/estado
        self.direcao = "front"   # 'front', 'back', 'right', 'left'
        self.movendo = False

        # Sprites por direção
        self.anim = {
            "front":   carregar_sprites_direcao(SPRITES_BASE_PATH, "front"),
            "back":     carregar_sprites_direcao(SPRITES_BASE_PATH, "back"),
            "right":  carregar_sprites_direcao(SPRITES_BASE_PATH, "right"),
            "left": carregar_sprites_direcao(SPRITES_BASE_PATH, "left"),
        }
        self.frame = 0
        self.frame_time = 0.0
        self.frame_dur = 1.0 / ANIM_FPS

        # Cache do tamanho do sprite para desenhar pelos pés
        self.sprite_w, self.sprite_h = SPRITE_TARGET_SIZE

    def _anim_update(self, dt: float):
        if self.movendo:
            self.frame_time += dt
            while self.frame_time >= self.frame_dur:
                self.frame_time -= self.frame_dur
                self.frame = (self.frame + 1) % len(self.anim[self.direcao])
        else:
            self.frame = 0
            self.frame_time = 0.0

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        dx = dy = 0.0
        self.movendo = False

        # Input
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
            self.direcao = "left"
            self.movendo = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
            self.direcao = "right"
            self.movendo = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
            self.direcao = "back"
            self.movendo = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
            self.direcao = "front"
            self.movendo = True

        # Normaliza diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Movimento
        self.rect.x += int(dx * PLAYER_SPEED * dt)
        self.rect.y += int(dy * PLAYER_SPEED * dt)

        # Limites do mundo
        world_w = MAP_W * TILE
        world_h = MAP_H * TILE
        self.rect.left   = max(0, self.rect.left)
        self.rect.top    = max(0, self.rect.top)
        self.rect.right  = min(world_w, self.rect.right)
        self.rect.bottom = min(world_h, self.rect.bottom)

        # Atualiza animação
        self._anim_update(dt)

    def draw(self, surf: pygame.Surface, offset: tuple[int, int]):
        offx, offy = offset

        # Desenha o sprite alinhado pelos pés (base do retângulo)
        img = self.anim[self.direcao][self.frame]

        draw_x = self.rect.centerx - self.sprite_w // 2 - offx
        draw_y = self.rect.bottom  - self.sprite_h     - offy
        surf.blit(img, (draw_x, draw_y))

        # (Opcional) desenhar hitbox para debug:
        # pygame.draw.rect(
        #     surf, (255, 0, 0),
        #     (self.rect.x - offx, self.rect.y - offy, self.rect.w, self.rect.h),
        #     1
        # )


# ---------------------- UI helper ---------------------- #
def draw_ui(surf: pygame.Surface, camera: Camera):
    font = pygame.font.SysFont("consolas", 18)
    mode_txt = "SMOOTH (Stardew-like)" if camera.mode == Camera.SMOOTH else "QUADROS (screen-by-screen)"
    text = font.render(f"TAB: alternar câmera  |  Modo atual: {mode_txt}", True, COLOR_UI)
    surf.blit(text, (12, 10))


# ---------------------- Loop principal ---------------------- #
def executar_camera_scroll(nome: str | None = None):
    """Abre a tela do mapa e roda até o usuário sair (ESC ou fechar)."""
    try:
        # Init robusto
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.display.get_init():
            pygame.display.init()

        print("[camera_scroll] driver de vídeo:", pygame.display.get_driver())

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Câmera com Scroll – Stardew / Quadros")

        # Ping visual (confirma abertura da janela)
        screen.fill((30, 30, 30))
        pygame.display.flip()
        pygame.time.delay(150)

        clock = pygame.time.Clock()

        # Mundo
        tilemap = TileMap(MAP_W, MAP_H, TILE)
        world_w_px = MAP_W * TILE
        world_h_px = MAP_H * TILE

        # Player e câmera
        player = Player(x=world_w_px // 2, y=200)
        camera = Camera(world_w_px, world_h_px)

        # (Opcional) Mostrar o nome do jogador no canto
        font_name = pygame.font.SysFont("consolas", 18) if nome else None

        print("[camera_scroll] Entrando no loop principal…")
        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("[camera_scroll] Evento QUIT recebido.")
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("[camera_scroll] ESC pressionado, saindo.")
                        running = False
                    elif event.key == pygame.K_TAB:
                        camera.toggle_mode()
                        print("[camera_scroll] Modo câmera =", "SMOOTH" if camera.mode == Camera.SMOOTH else "QUADROS")

            # Update
            player.update(dt)
            camera.update(player.rect, dt)

            # Draw
            screen.fill((210, 200, 170))
            tilemap.draw(screen, camera.offset)
            player.draw(screen, camera.offset)
            draw_ui(screen, camera)

            if nome and font_name:
                label = font_name.render(f"Jogador: {nome}", True, (20, 20, 20))
                screen.blit(label, (12, HEIGHT - 28))

            pygame.display.flip()

        print("[camera_scroll] Loop finalizado. Retornando.")
        return "inicial"

    except Exception:
        # Log detalhado
        print("[camera_scroll] EXCEÇÃO DETECTADA:\n" + traceback.format_exc())
        # Feedback visual rápido do erro na janela (se existir)
        try:
            screen = pygame.display.get_surface()
            if screen:
                font = pygame.font.SysFont("consolas", 18)
                msg_lines = ["ERRO no camera_scroll (ver terminal):", " ", *traceback.format_exc().splitlines()[-6:]]
                y = 20
                screen.fill((50, 20, 20))
                for line in msg_lines:
                    txt = font.render(line[:120], True, (255, 220, 220))
                    screen.blit(txt, (20, y))
                    y += 22
                pygame.display.flip()
                pygame.time.delay(2500)
        except:
            pass
        raise