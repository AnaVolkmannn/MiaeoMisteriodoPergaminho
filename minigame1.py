import pygame
import sys

def executar_minigame1():
    pygame.init()

    # === CONFIGURAÇÕES DA TELA ===
    largura, altura = 960, 540
    tela = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption("Minigame 1 - Números Romanos")

    # === CARREGAR IMAGENS ===
    fundo = pygame.image.load("img/fundoColiseu.png").convert()
    madeira = pygame.image.load("img/madeiraGame01.png").convert_alpha()

    # Redimensionar imagens
    fundo = pygame.transform.scale(fundo, (largura, altura))
    largura_madeira = 960
    altura_madeira = 750
    madeira = pygame.transform.scale(madeira, (largura_madeira, altura_madeira))

    # === TEXTO ===
    texto_historia = (
        "Mia entra sozinha no Coliseu silencioso. No centro da arena, tres alvos aguardam, "
        "cada um marcado com um numero romano. Desta vez, nao ha guerreiros a sua espera, "
        "apenas o desafio silencioso deixado pelos guardioes do pergaminho perdido. "
        "Apenas um revela o ano verdadeiro da criação das Olimpiadas: DCCLXXVI a.C. "
        "Para conquistar o fragmento da chave e seguir em sua busca pelo pergaminho perdido, "
        "Mia devera acertar o alvo correto com seu arco. "
        "Objetivo: Acerte o alvo com o ano correto da criacao das olimpiadas para ganhar o fragmento da chave."
    )

    fonte = pygame.font.Font("fonts/PIXELADE.ttf", 25)
    cor_texto = (255, 255, 255)
    relogio = pygame.time.Clock()

    # === FUNÇÃO DE TEXTO MULTILINHA ===
    def renderizar_texto_multilinha(superficie, texto, fonte, cor, rect, espaco_linha=5):
        palavras = texto.split(" ")
        linhas = []
        linha_atual = ""

        for palavra in palavras:
            test_linha = linha_atual + palavra + " "
            if fonte.size(test_linha)[0] < rect.width:
                linha_atual = test_linha
            else:
                linhas.append(linha_atual)
                linha_atual = palavra + " "
        linhas.append(linha_atual)

        total_altura = len(linhas) * (fonte.get_height() + espaco_linha)
        y = rect.centery - total_altura // 2

        for linha in linhas:
            texto_surface = fonte.render(linha.strip(), True, cor)
            texto_rect = texto_surface.get_rect(centerx=rect.centerx, y=y)
            superficie.blit(texto_surface, texto_rect)
            y += fonte.get_height() + espaco_linha

    # === LOOP PRINCIPAL ===
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                rodando = False

        # === DESENHAR ===
        tela.blit(fundo, (0, 0))

        # Madeira centralizada
        pos_x = (largura - madeira.get_width()) // 2
        pos_y = (altura - madeira.get_height()) // 2
        tela.blit(madeira, (pos_x, pos_y))

        # 🔹 Caixa de texto *central* da madeira (região interna do painel)
        # Essas margens foram ajustadas visualmente para o centro da madeira.
        caixa_texto = pygame.Rect(
            pos_x + 190,  # margem lateral esquerda
            pos_y + 280,  # margem superior — mais próxima do centro
            largura_madeira - 360,  # reduz largura útil
            altura_madeira - 520    # reduz altura útil
        )

        # Renderizar texto
        renderizar_texto_multilinha(tela, texto_historia, fonte, cor_texto, caixa_texto)

        pygame.display.flip()
        relogio.tick(60)

# Executa o minigame
executar_minigame1()
