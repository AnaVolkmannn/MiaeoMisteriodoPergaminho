import pygame
from random import randint
import traceback
import os
import csv

# importa os minigames
from minigame1 import executar_minigame1
from minigame2 import executar_minigame2
from minigame3 import executar_minigame3

# ====================== CONFIGURAÇÕES BÁSICAS ====================== #
WIDTH, HEIGHT = 960, 540       # resolução da janela (16:9)
FPS = 60
SCALE_MIA = 3                  # escala da Mia
TILE = 32                      # tamanho do tile
PLAYER_SPEED = 200             # velocidade do player

# ==================== CONFIGURAÇÃO DO TILESET ====================== #
TILESET_PATH = "magecity.png"
TILESET_TILE_W = 32
TILESET_TILE_H = 32

TILE_PICK = {
    0: ("GRASS",   (0, 0)),
    1: ("DIRT",    (41,2)),
    2: ("WATER",   (7, 1)),
    3: ("ROCK",    (37, 0)),
}

COLOR_UI = (0, 0, 0)

# ============================ UTIL ================================= #
def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def carregar_tileset(caminho: str, tile_w: int, tile_h: int) -> list[list[pygame.Surface]]:
    """Carrega o spritesheet e corta em blocos (tile_w x tile_h)."""
    imagem = pygame.image.load(caminho).convert_alpha()
    sheet_w, sheet_h = imagem.get_size()

    tiles = []
    for y in range(0, sheet_h, tile_h):
        if y + tile_h > sheet_h:
            break
        linha = []
        for x in range(0, sheet_w, tile_w):
            if x + tile_w > sheet_w:
                break
            rect = pygame.Rect(x, y, tile_w, tile_h)
            tile = imagem.subsurface(rect).copy()
            if (tile_w, tile_h) != (TILE, TILE):
                tile = pygame.transform.smoothscale(tile, (TILE, TILE))
            linha.append(tile)
        tiles.append(linha)
    return tiles

# ============================ CÂMERA =============================== #
class Camera:
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

# ============================ TILEMAP ============================== #
class TileMap:
    def __init__(self, w_tiles: int, h_tiles: int, tile_size: int, tileset_grid: list[list[pygame.Surface]]):
        self.w = w_tiles
        self.h = h_tiles
        self.size = tile_size
        self.tileset_grid = tileset_grid
        self.data = self._load_map()
        self.tile_surface = self._build_tile_cache()
        self.debug_mode = False

    def _load_map(self, filename="mapa.csv"):
        mapa = []
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for linha in reader:
                mapa.append([int(x) for x in linha])

        self.h = len(mapa)
        self.w = len(mapa[0]) if mapa else 0
        return mapa

    def _safe_get_tile(self, rc: tuple[int, int]) -> pygame.Surface:
        r, c = rc
        if 0 <= r < len(self.tileset_grid) and 0 <= c < len(self.tileset_grid[r]):
            return self.tileset_grid[r][c]
        base = self.tileset_grid[0][0].copy()
        pygame.draw.rect(base, (255, 0, 255), (0, 0, base.get_width()-1, base.get_height()-1), 2)
        return base

    def _build_tile_cache(self) -> dict[int, pygame.Surface]:
        cache = {}
        for tid, (_, rc) in TILE_PICK.items():
            cache[tid] = self._safe_get_tile(rc)
        return cache

    def draw(self, surf: pygame.Surface, offset: tuple[int, int]):
        offx, offy = offset
        first_x = max(0, offx // self.size)
        first_y = max(0, offy // self.size)
        last_x  = min(self.w, (offx + WIDTH) // self.size + 2)
        last_y  = min(self.h, (offy + HEIGHT) // self.size + 2)

        for y in range(first_y, last_y):
            for x in range(first_x, last_x):
                tile_id = self.data[y][x]
                rx = x * self.size - offx
                ry = y * self.size - offy
                surf.blit(self.tile_surface.get(tile_id, self.tile_surface[0]), (rx, ry))

                if self.debug_mode:
                    font = pygame.font.SysFont("consolas", 14)
                    txt = font.render(str(tile_id), True, (255, 0, 0))
                    surf.blit(txt, (rx + 4, ry + 4))

# ============================ PLAYER =============================== #
SPRITES_BASE_PATH = os.path.join("sprites", "mia")
ANIM_FPS = 10.0

class Player:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 28, 36)
        self.direcao = "front"
        self.movendo = False

        self.anim = {
            "front":   self._carregar_sprites_direcao("front"),
            "back":    self._carregar_sprites_direcao("back"),
            "right":   self._carregar_sprites_direcao("right"),
            "left":    self._carregar_sprites_direcao("left"),
        }
        self.frame = 0
        self.frame_time = 0.0
        self.frame_dur = 1.0 / ANIM_FPS
        self.sprite_w, self.sprite_h = self.anim["front"][0].get_size()

    def _carregar_sprites_direcao(self, direcao: str, frames: int = 6):
        imagens = []
        pasta = os.path.join(SPRITES_BASE_PATH, direcao)
        for i in range(1, frames + 1):
            caminho = os.path.join(pasta, f"{i}.png")
            img = pygame.image.load(caminho).convert_alpha()
            if SCALE_MIA != 1.0:
                w, h = img.get_size()
                img = pygame.transform.scale(img, (int(w * SCALE_MIA), int(h * SCALE_MIA)))
            imagens.append(img)
        return imagens

    def _anim_update(self, dt: float):
        if self.movendo:
            self.frame_time += dt
            if self.frame_time >= self.frame_dur:
                self.frame_time = 0
                self.frame = (self.frame + 1) % len(self.anim[self.direcao])
        else:
            self.frame = 0
            self.frame_time = 0.0

    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        dx = dy = 0.0
        self.movendo = False

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1; self.direcao = "left"; self.movendo = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1; self.direcao = "right"; self.movendo = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1; self.direcao = "back"; self.movendo = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1; self.direcao = "front"; self.movendo = True

        if dx != 0 and dy != 0:
            dx *= 0.7071; dy *= 0.7071

        self.rect.x += int(dx * PLAYER_SPEED * dt)
        self.rect.y += int(dy * PLAYER_SPEED * dt)
        self._anim_update(dt)

    def draw(self, surf: pygame.Surface, offset: tuple[int, int]):
        offx, offy = offset
        img = self.anim[self.direcao][self.frame]
        draw_x = self.rect.centerx - self.sprite_w // 2 - offx
        draw_y = self.rect.bottom  - self.sprite_h     - offy
        surf.blit(img, (draw_x, draw_y))

# ============================ UI HELPER ============================ #
def draw_ui(surf: pygame.Surface, camera: Camera):
    font = pygame.font.SysFont("consolas", 18)
    mode_txt = "SMOOTH (Stardew-like)" if camera.mode == Camera.SMOOTH else "QUADROS (screen-by-screen)"
    text = font.render(f"TAB: alternar câmera  |  Modo atual: {mode_txt}", True, COLOR_UI)
    surf.blit(text, (12, 10))

# ============================ LOOP PRINCIPAL ======================= #
def executar_camera_scroll(nome: str | None = None):
    try:
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.display.get_init():
            pygame.display.init()

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Câmera com Scroll – Tileset + Sprites da Mia")

        clock = pygame.time.Clock()

        if not os.path.exists(TILESET_PATH):
            raise FileNotFoundError(f"Tileset não encontrado: {TILESET_PATH}")
        tileset_grid = carregar_tileset(TILESET_PATH, TILESET_TILE_W, TILESET_TILE_H)

        tilemap = TileMap(0, 0, TILE, tileset_grid)
        world_w_px = tilemap.w * TILE
        world_h_px = tilemap.h * TILE

        player = Player(x=world_w_px // 2, y=200)
        camera = Camera(world_w_px, world_h_px)

        # === Portas para os minigames ===
        portas = [
            (pygame.Rect(world_w_px // 2, 400, 60, 80), executar_minigame1, "Minigame 1"),
            (pygame.Rect(world_w_px // 2 - 200, 600, 60, 80), executar_minigame2, "Minigame 2"),
            (pygame.Rect(world_w_px // 2 + 200, 600, 60, 80), executar_minigame3, "Minigame 3"),
        ]

        font_name = pygame.font.SysFont("consolas", 18) if nome else None
        font_hint = pygame.font.SysFont("consolas", 20)

        running = True
        while running:
            dt = clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_TAB:
                        camera.toggle_mode()
                    elif event.key == pygame.K_F1:
                        tilemap.debug_mode = not tilemap.debug_mode

            player.update(dt)
            camera.update(player.rect, dt)

            screen.fill((50, 50, 50))
            tilemap.draw(screen, camera.offset)
            player.draw(screen, camera.offset)
            draw_ui(screen, camera)

            if nome and font_name:
                label = font_name.render(f"Jogador: {nome}", True, (20, 20, 20))
                screen.blit(label, (12, HEIGHT - 28))

            # === Desenha e checa cada porta ===
            for porta, func, titulo in portas:
                porta_draw = pygame.Rect(
                    porta.x - camera.offset[0],
                    porta.y - camera.offset[1],
                    porta.w,
                    porta.h
                )
                pygame.draw.rect(screen, (139, 69, 19), porta_draw)  # porta provisória

                if player.rect.colliderect(porta):
                    hint = font_hint.render(f"Pressione E para entrar no {titulo}", True, (255, 255, 0))
                    screen.blit(hint, (WIDTH//2 - 150, HEIGHT//2 - 50))
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:
                        func()  # chama o minigame correspondente

            pygame.display.flip()

        return "inicial"

    except Exception:
        print("[camera_scroll] EXCEÇÃO DETECTADA:\n" + traceback.format_exc())
        raise

if __name__ == "__main__":
    executar_camera_scroll(nome="Mia")