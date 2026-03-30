import math
from config import Entidade, COR_REFEM

class Refem(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, COR_REFEM, 12, 100)
        self.resgatado = False
        self.velocidade = 4
        self.sala_id = 2 # O refém nasce na Sala 3 (índice 2)

    def update(self, alvo):
        if self.resgatado:
            # O refém passa a pertencer à mesma sala do jogador
            self.sala_id = alvo.sala_id 
            
            distancia = math.hypot(alvo.rect.centerx - self.rect.centerx, 
                                   alvo.rect.centery - self.rect.centery)
            
            if distancia > 40:
                dx = (alvo.rect.centerx - self.rect.centerx) / distancia
                dy = (alvo.rect.centery - self.rect.centery) / distancia
                self.rect.x += dx * self.velocidade
                self.rect.y += dy * self.velocidade
                
                # Atualiza a direção do refém para onde ele está andando
                self.direcao = math.atan2(dy, dx)