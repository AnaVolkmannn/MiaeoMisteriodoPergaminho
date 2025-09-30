import pygame
import sys
import re
from camera_scroll import executar_camera_scroll
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

    # === BOTÃO HOME ===
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
    fonte_erro = pygame.font.Font(None, 28)

    # === RECURSO PARA O BALÃO DE FALA ===
    img_balao_fala = pygame.image.load("img/balao_fala_mia.png").convert_alpha()
    
    # === NOVA FUNÇÃO: QUEBRA DE LINHAS ===
    def quebrar_texto(texto, fonte, largura_max):
        linhas = []
        palavras = texto.split(' ')
        linha_atual = ''
        for palavra in palavras:
            if fonte.size(linha_atual + ' ' + palavra)[0] <= largura_max:
                if linha_atual:
                    linha_atual += ' ' + palavra
                else:
                    linha_atual = palavra
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        if linha_atual:
            linhas.append(linha_atual)
        return linhas

    input_ativo = False
    nome_digitado = ""
    mostrar_erro = False
    texto_erro = ""

    # Backspace contínuo
    backspace_delay = 95
    backspace_timer = 0

    # Cursor piscando
    cursor_visible = True
    cursor_timer = 0
    cursor_interval = 500  # ms

    # Cores
    COR_INPUT = (255, 255, 255)
    COR_INPUT_INVALIDO = (255, 180, 180)
    cor_input_atual = COR_INPUT

    # Layout
    input_rect = pygame.Rect(250, 350, 400, 60)
    botao_pos = [300, 450]
    botao_size_original = (301, 90)
    botao_rect = pygame.Rect(botao_pos[0], botao_pos[1], *botao_size_original)

    # Validação do nome
    PADRAO_NOME = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ ]{2,20}$")
    def is_nome_valido(nome: str):
        n = nome.strip()
        if not n:
            return False, "Digite seu nome."
        if len(n) < 2:
            return False, "O nome precisa ter pelo menos 2 letras."
        if len(n) > 20:
            return False, "O nome pode ter no máximo 20 caracteres."
        if not PADRAO_NOME.fullmatch(n):
            return False, "Use apenas letras e espaços (sem números ou símbolos)."
        return True, ""

    # Fade in
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

    placeholder = "Digite seu nome..."

    while True:
        tela.blit(fundo, (0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # === DIGITAÇÃO ===
            if evento.type == pygame.KEYDOWN and input_ativo:
                if evento.key == pygame.K_RETURN:
                    valido, mensagem = is_nome_valido(nome_digitado)
                    if valido:
                        som_clique.play()
                        pygame.mixer.quit()
                        pygame.display.quit()
                        pygame.display.init()
                        return "mapa", nome_digitado.strip()
                    else:
                        mostrar_erro = True
                        texto_erro = mensagem
                        cor_input_atual = COR_INPUT_INVALIDO

                elif evento.key == pygame.K_BACKSPACE:
                    nome_digitado = nome_digitado[:-1]
                else:
                    if len(nome_digitado) < 20:
                        nome_digitado += evento.unicode
                if nome_digitado:
                    cor_input_atual = COR_INPUT

            # === CLIQUES ===
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos_click = evento.pos
                input_ativo = input_rect.collidepoint(mouse_pos_click)

                # Clique no CONTINUAR
                if botao_rect.collidepoint(mouse_pos_click):
                    som_clique.play()
                    valido, mensagem = is_nome_valido(nome_digitado)
                    if valido:
                        pygame.mixer.quit()
                        pygame.display.quit()
                        pygame.display.init()
                        return "mapa", nome_digitado.strip()
                    else:
                        mostrar_erro = True
                        texto_erro = mensagem
                        cor_input_atual = COR_INPUT_INVALIDO

                # Clique no HOME
                elif botaohome_rect.collidepoint(mouse_pos_click):
                    som_clique.play()
                    pygame.mixer.quit()
                    pygame.display.quit()
                    pygame.display.init()
                    return "inicial", None

        # === BACKSPACE CONTÍNUO ===
        teclas = pygame.key.get_pressed()
        if input_ativo and teclas[pygame.K_BACKSPACE]:
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - backspace_timer > backspace_delay:
                nome_digitado = nome_digitado[:-1]
                backspace_timer = tempo_atual
        else:
            backspace_timer = pygame.time.get_ticks()

        # === TEXTO EXPLICATIVO ===
        linha1 = "Antes de começarmos,"
        linha2 = "diga-nos quem é você..."
        texto_linha1 = fonte_explicativa.render(linha1, True, (0, 0, 0))
        texto_linha2 = fonte_explicativa.render(linha2, True, (0, 0, 0))
        x_central = largura // 2.8
        tela.blit(texto_linha1, texto_linha1.get_rect(center=(x_central, input_rect.y - 110)))
        tela.blit(texto_linha2, texto_linha2.get_rect(center=(x_central, input_rect.y - 70)))

        # === INPUT ===
        if nome_digitado != "":
            texto_input = fonte_principal.render(nome_digitado, True, cor_input_atual)
        else:
            if input_ativo:
                texto_input = fonte_principal.render("", True, cor_input_atual)
            else:
                texto_input = fonte_principal.render(placeholder, True, (220, 220, 220))

        tela.blit(texto_input, (input_rect.x + 14, input_rect.y + 10))

        # Cursor piscando
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - cursor_timer > cursor_interval:
            cursor_visible = not cursor_visible
            cursor_timer = tempo_atual

        if input_ativo and cursor_visible:
            cursor_x = input_rect.x + 14 + fonte_principal.size(nome_digitado)[0]
            cursor_y = input_rect.y + 10
            pygame.draw.line(tela, (0, 0, 0),
                             (cursor_x, cursor_y),
                             (cursor_x, cursor_y + fonte_principal.get_height()), 2)

        # === BOTÕES ===
        mouse_pos = pygame.mouse.get_pos()
        # CONTINUAR
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
        tela.blit(texto_botao, texto_botao.get_rect(center=botao_rect.center))

        # HOME
        if botaohome_rect.collidepoint(mouse_pos):
            tela.blit(img_botaohome_hover, botaohome_pos)
        else:
            tela.blit(img_botaohome, botaohome_pos)

        # === Mensagem de erro com Balão de Fala ===
        if mostrar_erro and texto_erro:
            # Posição da cabeça da personagem na imagem (aproximada)
            x_personagem = 925
            y_personagem = 275
            largura_max_balao = 400
            
            # Quebra o texto em linhas
            largura_max_texto = largura_max_balao - 80 # Adicionei um padding
            linhas_de_texto = quebrar_texto(texto_erro, fonte_erro, largura_max_texto)
            
            # Ajusta o tamanho do balão com base no texto
            largura_balao = max(fonte_erro.size(max(linhas_de_texto, key=len))[0] + 60, 200)
            
            # AQUI: AUMENTAMOS A ALTURA MÍNIMA E ADICIONAMOS MAIS ESPAÇO
            altura_balao = len(linhas_de_texto) * fonte_erro.get_height() + 180
            
            # Redimensiona o balão para o tamanho calculado
            balao_redimensionado = pygame.transform.smoothscale(img_balao_fala, (largura_balao, altura_balao))

            # Posição do balão: acima da cabeça
            pos_balao_x = x_personagem - largura_balao // 2
            pos_balao_y = y_personagem - altura_balao - 50 

            # Exibe o balão
            tela.blit(balao_redimensionado, (pos_balao_x, pos_balao_y))
            
            # Exibe cada linha do texto dentro do balão
            for i, linha in enumerate(linhas_de_texto):
                msg = fonte_erro.render(linha, True, (0, 0, 0))
                # Ajusta a posição vertical para centralizar o texto
                msg_rect = msg.get_rect(center=(pos_balao_x + largura_balao // 2, pos_balao_y + 85 + i * fonte_erro.get_height()))
                tela.blit(msg, msg_rect)

        # Cursor personalizado
        tela.blit(cursor_img, mouse_pos)

        pygame.display.update()
        relogio.tick(60)