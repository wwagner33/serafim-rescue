import pygame
import math

# ================= CORES E CONFIGURAÇÕES =================
COR_FUNDO = (240, 240, 240)
COR_JOGADOR = (244, 208, 63)
COR_ALIADO = (0, 255, 255)
COR_INIMIGO = (231, 76, 60)
COR_REFEM = (133, 130, 219)
COR_OBSTACULO = (110, 133, 150)

ARMAS = {
    "Soco": {"dano": 15, "municao_max": float('inf'), "alcance": 40, "vel_tiro": 0},
    "Revolver": {"dano": 35, "municao_max": 12, "alcance": 500, "vel_tiro": 15},
    "Espingarda": {"dano": 60, "municao_max": 6, "alcance": 300, "vel_tiro": 20}
}

# ================= CLASSE MÃE =================
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, cor, raio, vida_maxima):
        super().__init__()
        self.image = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, cor, (raio, raio), raio)
        pygame.draw.circle(self.image, (0,0,0), (raio, raio), raio, 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.raio = raio
        self.vida_maxima = vida_maxima
        self.vida = vida_maxima
        self.velocidade = 5
        self.arma_atual = "Revolver"
        self.municao = ARMAS[self.arma_atual]["municao_max"]
        
        self.direcao = 0 # Ângulo em radianos (0 é para a direita)
        self.sala_id = -1 # Identificador da sala para a mecânica de visão

    def desenhar(self, tela):
        # 1. Desenha o círculo do personagem
        tela.blit(self.image, self.rect)
        
        # 2. Desenha o vetor de direção / cano da arma
        comprimento_arma = self.raio + 12
        fim_x = self.rect.centerx + math.cos(self.direcao) * comprimento_arma
        fim_y = self.rect.centery + math.sin(self.direcao) * comprimento_arma
        pygame.draw.line(tela, (0, 0, 0), self.rect.center, (fim_x, fim_y), 4)

        # 3. Desenha a barra de vida (corrigida para baixo)
        largura_barra = 30
        razao = max(0, self.vida / self.vida_maxima)
        px = self.rect.centerx - largura_barra // 2
        py = self.rect.bottom + 5
        pygame.draw.rect(tela, (255, 0, 0), (px, py, largura_barra, 4))
        pygame.draw.rect(tela, (0, 255, 0), (px, py, largura_barra * razao, 4))