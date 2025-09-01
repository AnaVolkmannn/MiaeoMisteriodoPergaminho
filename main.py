import pygame
import sys
from tela_inicial import executar_tela_inicial
from tela_nome import executar_tela_nome
from camera_scroll import executar_camera_scroll

def main():
    pygame.init()

    estado = "inicial"
    nome_jogador = None

    while True:
        if estado == "inicial":
            estado = executar_tela_inicial()
        
        elif estado == "nome":
            estado, nome_jogador = executar_tela_nome()
        
        elif estado == "mapa":
            estado = executar_camera_scroll(nome_jogador)
        
        elif estado == "sair":
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
