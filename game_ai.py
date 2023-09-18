import pygame
import os
import random
import neat

# variaveis para AI
ai_jogando = True  # Ligar ou desligar a IA
geracao = 0

# config tela
tela_largura = 500
tela_altura = 800

#config imagens
icone = pygame.image.load(os.path.join('img', 'icon.png'))
imagem_cano = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'pipe.png')))
imagem_chao = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'base.png')))
imagem_fundo = pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bg.png')))
imagens_passaro = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('img', 'bird3.png')))
]

# titulo e icone
pygame.display.set_caption('Flappy Bird')
pygame.display.set_icon(icone)

# config fonte
pygame.font.init()
fonte_pontos = pygame.font.SysFont('arial', 50)

# classes de objetos
class Passaro:
    imgs = imagens_passaro
    # animacao passaro
    rotacao_maxima = 25
    velociade_rotacoa = 20
    tempo_animacao = 5
    # posicao passaro
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.imgs[0]
    # pular
    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    # mover
    def mover(self):
        # calcular deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo
        #restringir deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2
        self.y += deslocamento
        # angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.rotacao_maxima:
                self.angulo = self.rotacao_maxima
        else:
            if self.angulo > -90:
                self.angulo -= self.velociade_rotacoa

    def desenhar(self, tela):
        # definir sprites do passaro
        self.contagem_imagem += 1
        if self.contagem_imagem < self.tempo_animacao:
            self.imagem = self.imgs[0]
        elif self.contagem_imagem < self.tempo_animacao*2:
            self.imagem = self.imgs[1]
        elif self.contagem_imagem < self.tempo_animacao*3:
            self.imagem = self.imgs[2]
        elif self.contagem_imagem < self.tempo_animacao*4:
            self.imagem = self.imgs[1]
        elif self.contagem_imagem < self.tempo_animacao*4 + 1:
            self.imagem = self.imgs[0]
            self.contagem_imagem = 0
        # se o passaro cair nao bater asa
        if self.angulo <= -80:
            self.imagem = self.imgs[1]
            self.contagem_imagem = self.tempo_animacao*2
        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        # colisão
        return pygame.mask.from_surface(self.imagem)

class Cano:
    distancia = 200
    velocidade = 5

    # posicao cano
    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.cano_topo = pygame.transform.flip(imagem_cano, False, True)
        self.cano_base = imagem_cano
        self.passou = False
        self.definir_altura()

    # altura cano
    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.cano_topo.get_height()
        self.pos_base = self.altura + self.distancia

    # mover o cano
    def mover(self):
        self.x -= self.velocidade

    #desenhar cano
    def desenhar(self, tela):
        tela.blit(self.cano_topo, (self.x, self.pos_topo))
        tela.blit(self.cano_base, (self.x, self.pos_base))

    # colisao
    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.cano_topo)
        base_mask = pygame.mask.from_surface(self.cano_base)
        # distancia do passaro com o cano
        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))
        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)
        # verificar colisao
        if topo_ponto or base_ponto:
            return True
        else:
            return False

class Chao:
    velocidade = 5
    largura = imagem_chao.get_width()
    imagem = imagem_chao

    def __init__(self, y):
        # duplicar chao
        self.y = y
        self.x0 = 0
        self.x1 = self.largura

    # movimentar
    def mover(self):
        self.x0 -= self.velocidade
        self.x1 -= self.velocidade
        #mover chao 1 para tras
        if self.x0 + self.largura < 0:
            self.x0 = self.x1 + self.largura
        if self.x1 + self.largura < 0:
            self.x1 = self.x0 + self.largura

    # desenhar chao
    def desenhar(self, tela):
        tela.blit(self.imagem, (self.x0, self.y))
        tela.blit(self.imagem, (self.x1, self.y))

# desenhar tela
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(imagem_fundo, (0, 0))
    # desenhar passaros
    for passaro in passaros:
        passaro.desenhar(tela)
    # desenhar canos
    for cano in canos:
        cano.desenhar(tela)
    # desenhar pontuacao
    texto = fonte_pontos.render(f'Pontuação: {pontos}', 1, (255, 255, 255))
    tela.blit(texto, (tela_largura - 10 - texto.get_width(), 10))
    # AI geracoes
    if ai_jogando:
        texto = fonte_pontos.render(f'Geração: {geracao}', 1, (255, 255, 255))
        tela.blit(texto, (10, 10))
    chao.desenhar(tela)
    # atualizar tela
    pygame.display.update()

# jogo
def main(genomas, config):
    # AI geracao
    global geracao
    geracao += 1
    if ai_jogando:
        redes = []
        lista_genomas = []
        passaros = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            passaros.append(Passaro(230, 350))
    else:
        passaros = [Passaro(230, 350)]
    # elementos
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((tela_largura, tela_altura))
    pontos = 0
    relogio = pygame.time.Clock()
    # rodar jogo
    rodando = True
    while rodando:
        relogio.tick(30)
        # interacao com o usuario
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not ai_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()
        indice_cano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].cano_topo.get_width()):
                indice_cano = 1 
        else:
            if ai_jogando:
                rodando = False
                break
        # mover os objetos
        for i, passaro in enumerate(passaros):
            passaro.mover()
            # aumentar fitness
            if ai_jogando:
                lista_genomas[i].fitness += 0.1
                output = redes [i].activate((passaro.y,
                                            abs(passaro.y - canos[indice_cano].altura),
                                            abs(passaro.y - canos[indice_cano].pos_base)))
                 # output > 0.5 = pula
                if output[0] > 0.5:
                    passaro.pular()
        chao.mover()
        # interacao passaro e canos
        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ai_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.cano_topo.get_width() < 0:
                remover_canos.append(cano)
        # gerar canos
        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
            if ai_jogando:
                for genoma in lista_genomas:
                    genoma.fitness += 5
        for cano in remover_canos:
            canos.remove(cano)
        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if ai_jogando:
                    lista_genomas.pop(i)
                    redes.pop(i)
        # desenhar tela
        desenhar_tela(tela, passaros, canos, chao, pontos)

def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())
    if ai_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    caminho = os.path.dirname(__file__)
    caminho_config = os.path.join(caminho, 'config.txt')
    rodar(caminho_config)