import pygame
import math
import random
import sys

from config import Entidade, ARMAS, COR_FUNDO, COR_JOGADOR, COR_ALIADO, COR_INIMIGO, COR_OBSTACULO
from refem import Refem

pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 1200, 700
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Serafim Rescue Team")
FPS = 60

# ================= CONSTANTES DE BALANCEAMENTO =================
VIDA_BASE_INIMIGO = 50
VIDA_JOGADOR = int(VIDA_BASE_INIMIGO * 1.5) # O Jogador tem sempre 50% a mais de vida

# ================= CLASSES FILHAS =================

class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, COR_JOGADOR, 15, VIDA_JOGADOR)

    def mover(self, teclas, obstaculos, areas_pisaveis):
        dx, dy = 0, 0
        
        if teclas[pygame.K_w] or teclas[pygame.K_UP]: dy -= self.velocidade
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]: dy += self.velocidade
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]: dx -= self.velocidade
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dx += self.velocidade

        if dx != 0 or dy != 0:
            self.direcao = math.atan2(dy, dx)

        # Movimento e Colisão X
        self.rect.x += dx
        for obs in obstaculos:
            if self.rect.colliderect(obs):
                if dx > 0: self.rect.right = obs.left
                if dx < 0: self.rect.left = obs.right
                
        if not any(area.collidepoint(self.rect.center) for area in areas_pisaveis):
            self.rect.x -= dx

        # Movimento e Colisão Y
        self.rect.y += dy
        for obs in obstaculos:
            if self.rect.colliderect(obs):
                if dy > 0: self.rect.bottom = obs.top
                if dy < 0: self.rect.top = obs.bottom
                
        if not any(area.collidepoint(self.rect.center) for area in areas_pisaveis):
            self.rect.y -= dy

        self.rect.clamp_ip(TELA.get_rect())


class Aliado(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, COR_ALIADO, 15, VIDA_JOGADOR) # Mesmo life do jogador
        self.arma_atual = "Revolver"
        self.municao_maxima = 6 # Poucas balas para o Joventino
        self.municao = self.municao_maxima
        self.velocidade = 4 # Um pouco mais lento que o jogador
        self.cooldown_tiro = random.randint(40, 80)
        self.vivo = True

    def atualizar(self, jogador, inimigos, projeteis, obstaculos):
        if not self.vivo:
            return

        self.sala_id = jogador.sala_id

        # 1. Movimento Didático (Seguir o jogador)
        dist_jogador = math.hypot(jogador.rect.centerx - self.rect.centerx, jogador.rect.centery - self.rect.centery)
        
        # Só se move se estiver longe do jogador
        if dist_jogador > 80: 
            dx = ((jogador.rect.centerx - self.rect.centerx) / dist_jogador) * self.velocidade
            dy = ((jogador.rect.centery - self.rect.centery) / dist_jogador) * self.velocidade
            
            # Movimento e colisão básica (para não atravessar caixas)
            self.rect.x += dx
            for obs in obstaculos:
                if self.rect.colliderect(obs):
                    if dx > 0: self.rect.right = obs.left
                    if dx < 0: self.rect.left = obs.right
                    
            self.rect.y += dy
            for obs in obstaculos:
                if self.rect.colliderect(obs):
                    if dy > 0: self.rect.bottom = obs.top
                    if dy < 0: self.rect.top = obs.bottom

        # 2. IA de Tiro Didática
        inimigos_visiveis = [ini for ini in inimigos if ini.sala_id == self.sala_id]
        if inimigos_visiveis and self.municao > 0:
            alvo = min(inimigos_visiveis, key=lambda ini: math.hypot(ini.rect.centerx - self.rect.centerx, ini.rect.centery - self.rect.centery))
            
            # Aponta para o inimigo
            self.direcao = math.atan2(alvo.rect.centery - self.rect.centery, alvo.rect.centerx - self.rect.centerx)
            
            self.cooldown_tiro -= 1
            if self.cooldown_tiro <= 0:
                projeteis.add(Projetil(self.rect.centerx, self.rect.centery, self.direcao, "aliado", self.arma_atual))
                self.municao -= 1
                self.cooldown_tiro = random.randint(50, 100) # Demora um pouco para atirar de novo
        elif dist_jogador > 80:
            # Se não há inimigos, a arma aponta para onde ele está andando
            self.direcao = math.atan2(dy, dx)


class Inimigo(Entidade):
    def __init__(self, x, y, sala_id):
        super().__init__(x, y, COR_INIMIGO, 15, VIDA_BASE_INIMIGO)
        self.arma_atual = "Revolver"
        self.municao = ARMAS[self.arma_atual]["municao_max"]
        self.velocidade = 1 # Mais lentos para dar tempo de reagir
        self.sala_id = sala_id
        self.direcao = random.uniform(0, math.pi * 2) 
        self.cooldown_tiro = random.randint(60, 120) 

    def mover(self, jogador, obstaculos):
        # Estratégia didática de perseguição simples
        if self.sala_id == jogador.sala_id:
            dist = math.hypot(jogador.rect.centerx - self.rect.centerx, jogador.rect.centery - self.rect.centery)
            
            # Se estiver mais longe que 150 pixels, tenta se aproximar
            if dist > 150: 
                # Usa a mesma direção que ele está apontando (que já é na direção do jogador)
                dx = math.cos(self.direcao) * self.velocidade
                dy = math.sin(self.direcao) * self.velocidade
                
                self.rect.x += dx
                for obs in obstaculos:
                    if self.rect.colliderect(obs):
                        if dx > 0: self.rect.right = obs.left
                        if dx < 0: self.rect.left = obs.right
                        
                self.rect.y += dy
                for obs in obstaculos:
                    if self.rect.colliderect(obs):
                        if dy > 0: self.rect.bottom = obs.top
                        if dy < 0: self.rect.top = obs.bottom


class Projetil(pygame.sprite.Sprite):
    def __init__(self, x, y, angulo, dono, tipo_arma):
        super().__init__()
        self.dono = dono # Pode ser "jogador", "aliado" ou "inimigo"
        self.arma = ARMAS[tipo_arma]
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        cor_tiro = (255, 0, 0) if dono == "inimigo" else (0, 0, 0)
        pygame.draw.circle(self.image, cor_tiro, (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.dx = math.cos(angulo) * self.arma["vel_tiro"]
        self.dy = math.sin(angulo) * self.arma["vel_tiro"]
        self.x_flut, self.y_flut = x, y
        self.distancia_percorrida = 0

    def update(self):
        self.x_flut += self.dx
        self.y_flut += self.dy
        self.rect.centerx = int(self.x_flut)
        self.rect.centery = int(self.y_flut)
        self.distancia_percorrida += math.hypot(self.dx, self.dy)
        
        if self.distancia_percorrida > self.arma["alcance"]:
            self.kill()

# ================= FUNÇÕES DO JOGO =================

def gerar_cenario():
    salas = [
        pygame.Rect(150, 250, 250, 180), # Sala 0
        pygame.Rect(500, 250, 250, 180), # Sala 1
        pygame.Rect(850, 250, 200, 180), # Sala 2 (Refém)
        pygame.Rect(700, 480, 200, 180), # Sala 3
    ]
    corredores = [
        pygame.Rect(50, 315, 90, 50),    
        pygame.Rect(400, 315, 100, 50),  
        pygame.Rect(750, 315, 100, 50),  
        pygame.Rect(775, 365, 50, 115)   
    ]
    portas = [
        pygame.Rect(140, 315, 10, 50),   
        pygame.Rect(390, 315, 10, 50),   
        pygame.Rect(500, 315, 10, 50),   
        pygame.Rect(740, 315, 10, 50),   
        pygame.Rect(850, 315, 10, 50),   
        pygame.Rect(775, 470, 50, 10)    
    ]
    obstaculos = [
        pygame.Rect(200, 350, 120, 40), 
        pygame.Rect(300, 260, 50, 40),  
        pygame.Rect(550, 270, 60, 40),  
        pygame.Rect(650, 270, 60, 40),  
        pygame.Rect(650, 370, 60, 40),  
        pygame.Rect(900, 300, 40, 80)   
    ]
    
    areas_pisaveis = salas + corredores + portas

    grupo_inimigos = pygame.sprite.Group()
    
    def espalhar_inimigos(qtd, sala_rect, id_sala):
        for _ in range(qtd):
            posicao_valida = False
            tentativas = 0
            while not posicao_valida and tentativas < 100:
                ix = random.randint(sala_rect.left + 20, sala_rect.right - 20)
                iy = random.randint(sala_rect.top + 20, sala_rect.bottom - 20)
                rect_teste = pygame.Rect(ix - 15, iy - 15, 30, 30)
                
                bateu_em_obstaculo = any(rect_teste.colliderect(obs) for obs in obstaculos)
                if not bateu_em_obstaculo:
                    grupo_inimigos.add(Inimigo(ix, iy, id_sala))
                    posicao_valida = True
                tentativas += 1

    espalhar_inimigos(1, salas[0], 0)
    espalhar_inimigos(3, salas[1], 1)
    espalhar_inimigos(5, salas[3], 3)
    espalhar_inimigos(random.choice([0, 2]), salas[2], 2)
            
    refem = Refem(950, 340)
    refem.sala_id = 2
            
    return salas, corredores, portas, obstaculos, areas_pisaveis, grupo_inimigos, refem


# ================= MENU PRINCIPAL =================
def menu_principal():
    rodando_menu = True
    fonte_titulo = pygame.font.SysFont("Courier", 60, bold=True)
    fonte_botao = pygame.font.SysFont("Courier", 30, bold=True)
    
    largura_botao, altura_botao = 200, 60
    botao_play = pygame.Rect(LARGURA // 2 - largura_botao // 2, ALTURA // 2 + 50, largura_botao, altura_botao)
    
    while rodando_menu:
        TELA.fill((40, 44, 52)) 
        
        mouse_pos = pygame.mouse.get_pos()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: 
                    if botao_play.collidepoint(mouse_pos):
                        rodando_menu = False 
        
        texto_titulo = fonte_titulo.render("SERAFIM RESCUE TEAM", True, (255, 200, 0))
        rect_titulo = texto_titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50))
        TELA.blit(texto_titulo, rect_titulo)
        
        if botao_play.collidepoint(mouse_pos):
            cor_botao = (0, 200, 0)
        else:
            cor_botao = (0, 150, 0) 
            
        pygame.draw.rect(TELA, cor_botao, botao_play, border_radius=10)
        
        texto_botao = fonte_botao.render("PLAY", True, (255, 255, 255))
        rect_botao_texto = texto_botao.get_rect(center=botao_play.center)
        TELA.blit(texto_botao, rect_botao_texto)
        
        pygame.display.flip()

# ================= LOOP PRINCIPAL DO JOGO =================

def main():
    relogio = pygame.time.Clock()
    jogador = Jogador(90, 340) 
    joventino = Aliado(60, 340) # Instancia o Joventino um pouco atrás do jogador
    
    salas, corredores, portas, obstaculos, areas_pisaveis, inimigos, refem = gerar_cenario()
    projeteis = pygame.sprite.Group()
    
    rodando = True
    vitoria = False
    derrota = False

    while rodando:
        TELA.fill(COR_FUNDO)
        
        # 1. Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if jogador.municao > 0:
                        projeteis.add(Projetil(jogador.rect.centerx, jogador.rect.centery, jogador.direcao, "jogador", jogador.arma_atual))
                        jogador.municao -= 1
                    else:
                        for inimigo in inimigos:
                            if inimigo.sala_id == jogador.sala_id:
                                distancia = math.hypot(inimigo.rect.centerx - jogador.rect.centerx, 
                                                       inimigo.rect.centery - jogador.rect.centery)
                                
                                if distancia <= ARMAS["Soco"]["alcance"]:
                                    inimigo.vida -= ARMAS["Soco"]["dano"]
                                    if inimigo.vida <= 0:
                                        inimigo.kill()
                                    break
                
                if evento.key == pygame.K_r:
                    jogador.municao = ARMAS[jogador.arma_atual]["municao_max"]
                
                # NOVO EVENTO: Recarregar a arma do Joventino
                if evento.key == pygame.K_j and joventino.vivo:
                    joventino.municao = joventino.municao_maxima

        # 2. Atualizações e Lógica
        teclas = pygame.key.get_pressed()
        jogador.mover(teclas, obstaculos, areas_pisaveis) 
        
        # Atualiza a lógica do aliado Joventino
        joventino.atualizar(jogador, inimigos, projeteis, obstaculos)

        projeteis.update()

        jogador.sala_id = -1
        for i, sala in enumerate(salas):
            if jogador.rect.colliderect(sala):
                jogador.sala_id = i
                break

        # ================= AUTO-MIRA JOGADOR =================
        if jogador.sala_id != -1: 
            inimigos_visiveis = [ini for ini in inimigos if ini.sala_id == jogador.sala_id]
            if inimigos_visiveis:
                alvo_mais_proximo = min(inimigos_visiveis, key=lambda ini: math.hypot(ini.rect.centerx - jogador.rect.centerx, ini.rect.centery - jogador.rect.centery))
                jogador.direcao = math.atan2(alvo_mais_proximo.rect.centery - jogador.rect.centery, alvo_mais_proximo.rect.centerx - jogador.rect.centerx)

        # ================= IA DOS INIMIGOS =================
        for inimigo in inimigos:
            if inimigo.sala_id == jogador.sala_id:
                # Inimigo se movimenta em direção ao jogador
                inimigo.mover(jogador, obstaculos)

                angulo_para_jogador = math.atan2(jogador.rect.centery - inimigo.rect.centery, 
                                                 jogador.rect.centerx - inimigo.rect.centerx)
                inimigo.direcao = angulo_para_jogador
                
                inimigo.cooldown_tiro -= 1
                if inimigo.cooldown_tiro <= 0:
                    projeteis.add(Projetil(inimigo.rect.centerx, inimigo.rect.centery, inimigo.direcao, "inimigo", inimigo.arma_atual))
                    inimigo.cooldown_tiro = random.randint(60, 120)

        # ================= COLISÕES DE TIROS =================
        for projetil in projeteis:
            hit_parede = projetil.rect.collidelist(obstaculos) != -1
            
            # Tiros do Jogador OU do Aliado dão dano nos inimigos
            if projetil.dono in ["jogador", "aliado"]:
                hit = pygame.sprite.spritecollideany(projetil, inimigos)
                if hit:
                    hit.vida -= projetil.arma["dano"]
                    projetil.kill()
                    if hit.vida <= 0: hit.kill()
                elif hit_parede:
                    projetil.kill()
                    
            # Tiros do Inimigo dão dano no Jogador OU no Aliado
            elif projetil.dono == "inimigo":
                acertou_alguem = False
                
                if projetil.rect.colliderect(jogador.rect):
                    jogador.vida -= projetil.arma["dano"]
                    acertou_alguem = True
                    if jogador.vida <= 0:
                        derrota = True
                        rodando = False
                
                elif joventino.vivo and projetil.rect.colliderect(joventino.rect):
                    joventino.vida -= projetil.arma["dano"]
                    acertou_alguem = True
                    if joventino.vida <= 0:
                        joventino.vivo = False # Joventino caiu!
                
                if acertou_alguem or hit_parede:
                    projetil.kill()

        # Lógica do Refém
        if not refem.resgatado and jogador.rect.colliderect(refem.rect):
            refem.resgatado = True

        refem.update(jogador)

        if refem.resgatado and jogador.rect.x < 130:
            vitoria = True
            rodando = False

        # 3. Desenho
        for corr in corredores:
            pygame.draw.rect(TELA, (210, 210, 210), corr)
            pygame.draw.rect(TELA, (150, 150, 150), corr, 1)
            
        for sala in salas:
            pygame.draw.rect(TELA, (225, 225, 225), sala)
            pygame.draw.rect(TELA, (100, 100, 100), sala, 2)
            
        for porta in portas:
            pygame.draw.rect(TELA, (0, 0, 0), porta)
        
        for obs in obstaculos:
            pygame.draw.rect(TELA, COR_OBSTACULO, obs)
            pygame.draw.rect(TELA, (0, 0, 0), obs, 2)

        jogador.desenhar(TELA)
        
        if joventino.vivo:
            joventino.desenhar(TELA)
        
        for inimigo in inimigos:
            if inimigo.sala_id == jogador.sala_id:
                inimigo.desenhar(TELA)
            
        if refem.sala_id == jogador.sala_id or refem.resgatado:
            refem.desenhar(TELA)
            if refem.resgatado:
                fonte_msg = pygame.font.SysFont("Arial", 14, bold=True)
                txt = fonte_msg.render("RESGATADO!", True, (0, 150, 0))
                TELA.blit(txt, (refem.rect.x - 10, refem.rect.y - 20))

        projeteis.draw(TELA)

        # UI Atualizada com os dados do Joventino
        fonte = pygame.font.SysFont("Courier", 18, bold=True)
        
        texto_jogador = f"Munição: {jogador.municao}/{ARMAS[jogador.arma_atual]['municao_max']}"
        if jogador.municao == 0:
            texto_jogador += " [R: RECARREGAR]"
        
        ui_texto = fonte.render(f"JOGADOR -> {texto_jogador} | Vida: {max(0, int(jogador.vida))}", True, (0, 0, 0))
        TELA.blit(ui_texto, (20, 10))
        
        if joventino.vivo:
            texto_jov = f"Munição: {joventino.municao}/{joventino.municao_maxima}"
            if joventino.municao == 0:
                texto_jov += " [TECLe 'J' PARA RECARREGAR O ALIADO]"
            ui_jov = fonte.render(f"JOVENTINO -> {texto_jov} | Vida: {max(0, int(joventino.vida))}", True, (0, 100, 150))
            TELA.blit(ui_jov, (20, 35))
        else:
            ui_jov = fonte.render("JOVENTINO CAIU EM COMBATE!", True, (200, 0, 0))
            TELA.blit(ui_jov, (20, 35))

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()
    
    if vitoria:
        print("\n" + "="*50)
        print("🏆 VITÓRIA! O refém foi extraído com segurança.")
        print("="*50 + "\n")
    elif derrota:
        print("\n" + "="*50)
        print("💀 GAME OVER! Você foi abatido em combate.")
        print("="*50 + "\n")
    
    sys.exit()

if __name__ == "__main__":
    menu_principal()
    main()