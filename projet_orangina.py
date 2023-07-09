import sys
import pygame
from enum import Enum
from pygame.locals import *
import pygame.time
from pygame import mixer

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

class Niveau:
    def __init__(self):
        self._personnages = list()
        self._niveaudata = [[dict() for i in range(100)] for j in range(500)]
        self._orig = [0, 0]
        # Chargement des images
        self._image_brique = pygame.image.load("bloc_32.png")
        self._image_herbe = pygame.image.load("bloc_herbe_32.png")
        self._image_piece = pygame.image.load("piece.png")
        self._image_mechant = pygame.image.load("mechant.png")
        self._image_papillon = pygame.image.load("chenille_volante.png")

        # Chargement du niveau
        self.charge("niveau_1.txt")

    def charge(self, cheminNiveau):
        niveau = open(cheminNiveau)
        x, y = 0, 0
        for curline in niveau.readlines():
            x = 0
            for curchar in curline:
                if curchar == 'd':
                    self._balo = Balo([x, y], self)
                    self._position_tile_balo = (x, y)
                elif curchar == '#':
                    self._niveaudata[x][y]['sprite'] = self._image_brique
                elif curchar == 'b':
                    self._niveaudata[x][y]['sprite'] = self._image_herbe
                elif curchar == 'm':
                    mechant = Mechant([x, y], self)
                    self._personnages.append(mechant)
                    #self._niveaudata[x][y]['sprite'] = self._image_mechant
                elif curchar == 'p':
                    self._niveaudata[x][y]['sprite'] = self._image_papillon
                elif curchar == '*':
                    self._niveaudata[x][y]['sprite'] = self._image_piece
                else:
                    self._niveaudata[x][y]['sprite'] = None
                x += 1
            y += 1

    def change_origine(self, origx=0, origy=0):
        self._orig = [origx, origy]

    def dessine(self, ecran):
        # Dessiner tout le niveau
        for x in range(len(self._niveaudata)):
            for y in range(len(self._niveaudata[x])):
                if self._niveaudata[x][y]:
                    sprite = self._niveaudata[x][y]['sprite']
                    if sprite:
                        #print(sprite)
                        ecran.blit(sprite, (x*32 + self._orig[0], y*32 + self._orig[1]))
        # Dessiner Balo
        self._balo.dessine(ecran)
        # Dessiner les méchants
        for personnage in self._personnages:
            personnage.dessine(ecran)

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
        tile =  self._niveaudata[position_tile[0]][position_tile[1]]
        if tile:
            sprite = tile['sprite']
            if sprite:
                return True
        return False

    def collision(self, position_pixel_niveau, vitesse_pixel=[0, 0]):
        # On part du principe qu'on n'est pas encore en collision
        # On regarde s'il y aura une collision en X
        prochaine_position_pixel_niveau_x = [position_pixel_niveau[0]+vitesse_pixel[0],
                                            position_pixel_niveau[1]]
        # S'il y a collision, on annule la vitesse en X
        if self.pixel_en_collision(prochaine_position_pixel_niveau_x):
            vitesse_pixel[0] = 0
            #position_tile = self.conversionPositionPixelNiveauVersTile(prochaine_position_pixel_niveau_x)
            position_pixel_niveau[0] += 1
            print("Collision en X")
            return True
        else:
            position_pixel_niveau[0] += vitesse_pixel[0]

        # On regarde s'il y aura une collision en Y
        prochaine_position_pixel_niveau_y = [position_pixel_niveau[0],
                                            position_pixel_niveau[1]+vitesse_pixel[1]]
        # S'il y a collision, on annule la vitesse en Y
        if self.pixel_en_collision(prochaine_position_pixel_niveau_y):
            vitesse_pixel[1] = 0
            #position_pixel_niveau[1] += 1
            print("Collision en Y")
            return True
        else:
            position_pixel_niveau[1] += vitesse_pixel[1]

        return False

class Personnage:

    def __init__(self, position_tile, niveau):
        self._position_tile = position_tile

class Direction(Enum):
    GAUCHE = -1
    DROITE = 1

class SautBalo(Enum):
    RIEN = 0
    SAUT_COURT = 1
    SAUT_MOYEN = 2
    SAUT_LONG  = 3

class Mechant(Personnage):
    def __init__(self, position_tile, niveau):
        super().__init__(position_tile, niveau)
        self._niveau = niveau
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 16]
        self._image_mechant = niveau._image_mechant
        self._vitesse = [0.4, 0.]

    def dessine(self, ecran):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        ecran.blit(self._image_mechant, (position_ecran[0] - 16, position_ecran[1] - 16) )

    def gestion(self):
        # Detection collision
        if niveau.collision(self._position_pieds, self._vitesse):
            self._vitesse[0] = -self._vitesse[0]
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
        self._image_balo_d = pygame.image.load("balo.png")
        self._image_balo_g = pygame.transform.flip(self._image_balo_d, True, False)

        self._image_balo_feu = [pygame.image.load("balo_crache_1.png"),
                                pygame.image.load("balo_crache_2.png"),
                                pygame.image.load("balo_crache_3.png")]
        self._vitesse = [1, 0]
        self._saut = SautBalo.RIEN
        self._cycle_saut = 0
        self._direction = Direction.DROITE
        self._crache = 0
        self._vies = 3

    def dessine(self, ecran):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        #position_balo_ecran = (self._position_pieds[0] + orig - 16, position_pieds_balo[1] - 64)
        if self._direction == Direction.DROITE:
            if self._crache == 0:
                ecran.blit(self._image_balo_d, (position_ecran[0] - 16, position_ecran[1] - 64) )
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
            ecran.blit(self._image_balo_g, (position_ecran[0] - 16, position_ecran[1] - 64) )
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

    def gestion(self):
        print(self._position_pieds)
        # print(self._cycle_saut)
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

        # Mise à jour de la position
        #self._position_pieds[0] += self._vitesse[0]
        #self._position_pieds[1] += self._vitesse[1]

        # Si Balo est à y=+1000, il est tombé dans un trou
        if self._position_pieds[1] > 2000:
            self.perteVie()


niveau = Niveau()
 
orig = 0
origy = 0
position_pieds_balo = [niveau._position_tile_balo[0]*32 + 16, niveau._position_tile_balo[1]*32 + 32]
acceleration_saut_balo = 0
cycle = 0
mixer.init()
mixer.music.load('niveau1-1.xm')
mixer.music.play()

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
        tiers_ecran = taille_ecran[0]/3
        deuxtiers_ecran = tiers_ecran*2
        if (orig + niveau._balo._position_pieds[0]) < tiers_ecran:
            orig = tiers_ecran - niveau._balo._position_pieds[0]
        if (orig + niveau._balo._position_pieds[0]) > deuxtiers_ecran:
            orig = deuxtiers_ecran - niveau._balo._position_pieds[0]

        # Dessin du niveau
        niveau.change_origine(orig, origy)
        niveau.dessine(ecran)

        pygame.display.flip()
        pygame.time.Clock().tick(60)
