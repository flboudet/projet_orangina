import sys
import pygame
from enum import Enum
from pygame.locals import *
import pygame.time
from pygame import mixer

from personnage import *
from esprit_des_nuages import *
from dimmer import *

print("Projet Orangina")

pygame.init()

taille_ecran = 800, 600
ecran = pygame.display.set_mode(taille_ecran)

image_ciel = pygame.image.load("ciel.png")
image_ciel_rect = image_ciel.get_rect()

son_saut = pygame.mixer.Sound("sons/saut.wav")



def dessine_niveau(niveaudata, origx=0, origy=0):
    for x in range(len(niveaudata)):
        for y in range(len(niveaudata[x])):
            if niveaudata[x][y]:
                sprite = niveaudata[x][y]['sprite']
                if sprite:
                    #print(sprite)
                    ecran.blit(sprite, (x*32 + origx, y*32 + origy))

class Bloc:
    def __init__(self, image):
        self._image = image
        
    def dessine(self, ecran, coord, cycle):
        ecran.blit(self._image, coord)

class Bloc_brique(Bloc):
    def __init__(self):
        self._image_brique = pygame.image.load("bloc_32.png")
        super().__init__(self._image_brique)

class Bloc_herbe(Bloc):
    def __init__(self):
        self._image_herbe = pygame.image.load("bloc_herbe_32.png")
        super().__init__(self._image_herbe)

class Bloc_piece(Bloc):
    def __init__(self):
        self._image_piece = pygame.image.load("piece.png")
        super().__init__(self._image_piece)

class Bloc_papillon(Bloc):
    def __init__(self):
        self._image_papillon = pygame.image.load("chenille_volante.png")
        super().__init__(self._image_papillon)

class Bloc_grass(Bloc):
    def __init__(self):
        self._image_grass_load = [pygame.image.load("bloc_grass_1.png"),
                                  pygame.image.load("bloc_grass_2.png"),
                                  pygame.image.load("bloc_grass_3.png")]
        self._image_grass = [self._image_grass_load[0],
                             self._image_grass_load[1],
                             self._image_grass_load[2],
                             self._image_grass_load[1]]
        super().__init__(self._image_grass[0])
        
    def dessine(self, ecran, coord, cycle):
        ecran.blit(self._image_grass[int(cycle/10) % 4], coord)
        
class Niveau:
    def __init__(self):
        self._personnages = list()
        self._niveaudata = [[dict() for i in range(100)] for j in range(1000)]
        self._orig = [0, 0]
        self._affiche_dialogue = False
        # Chargement des images
        self._image_mechant = pygame.image.load("mechant.png")

        # Chargement du niveau
        self.charge("niveau_1.txt")

    def charge(self, cheminNiveau):
        niveau = open(cheminNiveau)
        x, y = 0, 0
        for curline in niveau.readlines():
            x = 0
            for curchar in curline:
                self._niveaudata[x][y]['bloc'] = None
                if curchar == 'd':
                    self._balo = Balo([x, y], self)
                    self._position_tile_balo = (x, y)
                elif curchar == '#':
                    self._niveaudata[x][y]['bloc'] = Bloc_brique()
                elif curchar == 'b':
                    self._niveaudata[x][y]['bloc'] = Bloc_herbe()
                elif curchar == 'g':
                    self._niveaudata[x][y]['bloc'] = Bloc_grass()
                elif curchar == 'm':
                    mechant = Drhaka([x, y], self)
                    self._personnages.append(mechant)
                elif curchar == 'e':
                    esprit = EspritDesNuages([x, y], self)
                    self._personnages.append(esprit)
                elif curchar == 'p':
                    self._niveaudata[x][y]['bloc'] = Bloc_papillon()
                elif curchar == '*':
                    self._niveaudata[x][y]['bloc'] = Bloc_piece()
                else:
                    self._niveaudata[x][y]['sprite'] = None
                x += 1
            y += 1

    def change_origine(self, origx=0, origy=0):
        self._orig = [origx, origy]

    def dessine(self, ecran : pygame.Surface, cycle):
        # Dessiner tout le niveau
        for x in range(len(self._niveaudata)):
            for y in range(len(self._niveaudata[x])):
                if self._niveaudata[x][y]:
                    bloc = self._niveaudata[x][y]['bloc']
                    if bloc:
                        bloc.dessine(ecran, (x*32 + self._orig[0], y*32 + self._orig[1]), cycle=cycle)
        # Dessiner Balo
        self._balo.dessine(ecran)
        # Dessiner les méchants
        for personnage in self._personnages:
            personnage.dessine(ecran)
        # Dessiner le dialogue
        if self._affiche_dialogue:
            ecran.fill((0, 0, 100, 40), (100, 100, 600, 400), pygame.BLEND_RGBA_MULT)

    def dialogue(self):
        self._affiche_dialogue = True
        self._texte_dialogue = "Hello !"

    def gestion(self):
        for personnage in self._personnages:
            personnage.gestion()
        self._balo.gestion()

    def conversionPositionTile(self, position_tile):
        return [position_tile[0] * 32, position_tile[1] * 32]

    def conversionPositionPixelEcran(self, position_pixel_niveau):
        return [position_pixel_niveau[0] + self._orig[0], position_pixel_niveau[1] + self._orig[1]]

    def conversionPositionPixelNiveauVersTile(self, position_pixel_niveau):
        return [int(position_pixel_niveau[0] / 32), int(position_pixel_niveau[1] / 32)]

    def pixel_en_collision(self, position_pixel_niveau):
        position_tile = self.conversionPositionPixelNiveauVersTile(position_pixel_niveau)
        if len(self._niveaudata) < (position_tile[0]+1):
            return False
        if len(self._niveaudata[position_tile[0]]) < (position_tile[1]+1):
            return False
        tile =  self._niveaudata[position_tile[0]][position_tile[1]]
        if tile:
            sprite = tile['bloc']
            if sprite:
                return True
        return False

    def collision(self, position_pixel_niveau, vitesse_pixel=[0, 0]):
        result = False
        # On part du principe qu'on n'est pas encore en collision
        # On regarde s'il y aura une collision en X
        prochaine_position_pixel_niveau_x = [position_pixel_niveau[0]+vitesse_pixel[0],
                                            position_pixel_niveau[1]]
        # S'il y a collision, on annule la vitesse en X
        if self.pixel_en_collision(prochaine_position_pixel_niveau_x):
            position_tile = self.conversionPositionPixelNiveauVersTile(prochaine_position_pixel_niveau_x)
            position_tile_pixel = self.conversionPositionTile(position_tile)
            if vitesse_pixel[0] < 0:
                position_pixel_niveau[0] = position_tile_pixel[0]+32
            else:
                position_pixel_niveau[0] = position_tile_pixel[0] - 1
            vitesse_pixel[0] = 0
            print("Collision en X")
            result = True
        else:
            position_pixel_niveau[0] += vitesse_pixel[0]

        # On regarde s'il y aura une collision en Y
        prochaine_position_pixel_niveau_y = [position_pixel_niveau[0],
                                            position_pixel_niveau[1]+vitesse_pixel[1]]
        # S'il y a collision, on annule la vitesse en Y
        if self.pixel_en_collision(prochaine_position_pixel_niveau_y):
            position_tile = self.conversionPositionPixelNiveauVersTile(prochaine_position_pixel_niveau_x)
            position_tile_pixel = self.conversionPositionTile(position_tile)
            if vitesse_pixel[1] < 0:
                position_pixel_niveau[1] = position_tile_pixel[1]
            else:
                position_pixel_niveau[1] = position_tile_pixel[1]+31
            vitesse_pixel[1] = 0
            print("Collision en Y")
            result = True
        else:
            position_pixel_niveau[1] += vitesse_pixel[1]

        return result

class Direction(Enum):
    GAUCHE = -1
    DROITE = 1

class SautBalo(Enum):
    RIEN = 0
    SAUT_COURT = 1
    SAUT_MOYEN = 2
    SAUT_LONG  = 3

class Drhaka(Personnage):
    def __init__(self, position_tile, niveau):
        super().__init__(position_tile, niveau)
        self._niveau = niveau
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._image_mechant = niveau._image_mechant
        self._vitesse = [0.2, 0.] 

    def dessine(self, ecran):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        ecran.blit(self._image_mechant, (position_ecran[0] - 16, position_ecran[1] - 32) )

    def gestion(self):
        # Gestion de la gravité
        self._vitesse[1] += 0.3
        # Detection collision
        prev_vitesse_x = self._vitesse[0]
        if niveau.collision(self._position_pieds, self._vitesse):
            if self._vitesse[0] == 0:
                self._vitesse[0] = -prev_vitesse_x

        # Mise à jour de la position
        self._position_pieds[0] += self._vitesse[0]
        self._position_pieds[1] += self._vitesse[1]

class Balo(Personnage):

    def __init__(self, position_tile, niveau):
        super().__init__(position_tile, niveau)
        self._niveau = niveau
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._position_pieds_origine = self._position_pieds.copy()
        self._image_balo_d = list()
        self._image_balo_d.append(pygame.image.load("balo.png"))
        self._image_balo_d.append(pygame.image.load("balo_course_1.png"))
        self._image_balo_d.append(pygame.image.load("balo_course_2.png"))
        # Miroir pour faire les images de gauche
        self._image_balo_g = list()
        for balo_image in self._image_balo_d:
            self._image_balo_g.append(pygame.transform.flip(balo_image, True, False))

        self._image_balo_feu = [pygame.image.load("balo_crache_1.png"),
                                pygame.image.load("balo_crache_2.png"),
                                pygame.image.load("balo_crache_3.png")]
        self._vitesse = [1, 0]
        self._saut = SautBalo.RIEN
        self._cycle_marche = 0
        self._cycle_saut = 0
        self._direction = Direction.DROITE
        self._crache = 0
        self._vies = 3
        self._derniere_position_posee = self._position_pieds.copy()

    def dessine(self, ecran):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        #position_balo_ecran = (self._position_pieds[0] + orig - 16, position_pieds_balo[1] - 64)
        if self._direction == Direction.DROITE:
            if self._crache == 0:
                ecran.blit(self._image_balo_d[(int(self._cycle_marche/20)) % 3], (position_ecran[0] - 16, position_ecran[1] - 64) )
            else:
                if self._crache < 10:
                    ecran.blit(self._image_balo_feu[0], (position_ecran[0] - 16, position_ecran[1] - 64) )
                elif self._crache < 20:
                    ecran.blit(self._image_balo_feu[1], (position_ecran[0] - 16, position_ecran[1] - 64) )
                elif self._crache < 70:
                    ecran.blit(self._image_balo_feu[2], (position_ecran[0] - 16, position_ecran[1] - 64) )
                elif self._crache < 80:
                    ecran.blit(self._image_balo_feu[1], (position_ecran[0] - 16, position_ecran[1] - 64) )
                else:
                    ecran.blit(self._image_balo_feu[0], (position_ecran[0] - 16, position_ecran[1] - 64) )
        else:
            image = self._image_balo_g[(int(self._cycle_marche/20)) % 3]
            if image.get_width() == 64:
                ecran.blit(image, (position_ecran[0] - 16 - 32, position_ecran[1] - 64) )
            else:
                ecran.blit(image, (position_ecran[0] - 16, position_ecran[1] - 64) )
        pass

    def court_a_droite(self):
        self._vitesse[0] = 2
        self._direction = Direction.DROITE

    def court_a_gauche(self):
        self._vitesse[0] = -2
        self._direction = Direction.GAUCHE

    def stoppe(self):
        self._vitesse[0] = 0

    def saute(self):
        if self._saut == SautBalo.RIEN:
            self._saut = SautBalo.SAUT_COURT
            self._cycle_saut = 0
            self._vitesse[1] = -3
        elif self._cycle_saut > 20:
            self._saut = SautBalo.SAUT_LONG
        elif self._cycle_saut > 9:
            self._saut = SautBalo.SAUT_MOYEN

    def crache(self):
        self._crache = 1
        pass

    def perteVie(self):
        self._vies = self._vies - 1
        self._position_pieds = self._position_pieds_origine.copy()
        fondu = Dimmer(1)
        for i in range(64):
            fondu.dim(i)
            pygame.time.Clock().tick(60)


    def gestion(self):
        print(self._position_pieds)
        # print(self._cycle_saut)

        # Gestion du déplacement
        if self._vitesse[0] != 0:
            self._cycle_marche += 1
        else:
            self._cycle_marche = 0

        # Gestion du feu
        if self._crache > 0:
            self._crache += 1
            if self._crache == 100:
                self._crache = 0
        # Gestion de la gravité et des sauts
        if self._saut == SautBalo.RIEN \
                 or (self._saut == SautBalo.SAUT_COURT and self._cycle_saut > 20) \
                 or (self._saut == SautBalo.SAUT_MOYEN and self._cycle_saut > 40) \
                 or (self._saut == SautBalo.SAUT_LONG  and self._cycle_saut > 60):
            self._vitesse[1] += 0.3
            # self._saut = SautBalo.RIEN
        else:
            self._cycle_saut += 1

        # Detection collision
        if niveau.collision(self._position_pieds, self._vitesse):
            #self._vitesse[1] = 0
            self._saut = SautBalo.RIEN
            # on mémorise la dernière plateforme sur laquelle on s'est posé
            self._derniere_position_posee = self._position_pieds.copy()

        # Mise à jour de la position
        #self._position_pieds[0] += self._vitesse[0]
        #self._position_pieds[1] += self._vitesse[1]

        # Si Balo est à y=+1000 de sa dernière position posée il est tombé dans un trou
        if self._position_pieds[1] - self._derniere_position_posee[1] > 2000:
            self.perteVie()


niveau = Niveau()
 
orig = 0
origy = 0
position_pieds_balo = [niveau._position_tile_balo[0]*32 + 16, niveau._position_tile_balo[1]*32 + 32]
acceleration_saut_balo = 0
cycle = 0
mixer.init()
#mixer.music.load('Crystal_&_Lord_R.mp3')
#mixer.music.load('dark_fire.mp3')
mixer.music.load('balo_1-1.mp3')

mixer.music.play(-1)

gigot = pygame.image.load("gigot.png")
font = pygame.font.SysFont(None, 32)

while 1:
    cycle += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # On s'occupe du clavier
    touches_pressees = pygame.key.get_pressed()

    if touches_pressees[K_a]:
        orig += 1
    if touches_pressees[K_e]:
        orig -= 1
    if touches_pressees[K_z]:
        origy += 1
    if touches_pressees[K_s]:
        origy -= 1
    if touches_pressees[K_d]:
        niveau.dialogue()
    if touches_pressees[K_LEFT]:
        niveau._balo.court_a_gauche()
    elif touches_pressees[K_RIGHT]:
        niveau._balo.court_a_droite()
    else:
        niveau._balo.stoppe()
    if touches_pressees[K_SPACE]:
        niveau._balo.saute()
    if touches_pressees[K_w]:
        niveau._balo.crache()

    niveau.gestion()

    # Dessin, 1 cycle sur 4
    if cycle % 4 == 0:
        #ecran.fill(black)
        ecran.blit(image_ciel, image_ciel_rect)

        # Calcul de la position de la camera, scrolling horizontal
        tiers_ecran_x = taille_ecran[0]/3
        deuxtiers_ecran_x = tiers_ecran_x*2
        if (orig + niveau._balo._position_pieds[0]) < tiers_ecran_x:
            orig = tiers_ecran_x - niveau._balo._position_pieds[0]
        if (orig + niveau._balo._position_pieds[0]) > deuxtiers_ecran_x:
            orig = deuxtiers_ecran_x - niveau._balo._position_pieds[0]

        tiers_ecran_y = taille_ecran[1]/3
        deuxtiers_ecran_y = tiers_ecran_y*2
        if (origy + niveau._balo._position_pieds[1]) < tiers_ecran_y:
            origy = tiers_ecran_y - niveau._balo._position_pieds[1]
        if (origy + niveau._balo._position_pieds[1]) > deuxtiers_ecran_y:
            origy = deuxtiers_ecran_y - niveau._balo._position_pieds[1]
            
        # Dessin du niveau
        niveau.change_origine(orig, origy)
        niveau.dessine(ecran, cycle=cycle)

        # Dessin du nombre de vies
        ecran.blit(gigot, (10, 0))
        texteVies = "x{0}".format(niveau._balo._vies)
        vies = font.render(texteVies, False, pygame.color.THECOLORS["goldenrod1"])
        viesdark = font.render(texteVies, False, pygame.color.THECOLORS["black"])
        ecran.blit(viesdark, (66, 34))
        ecran.blit(vies, (64, 32))

        pygame.display.flip()
        pygame.time.Clock().tick(60)
