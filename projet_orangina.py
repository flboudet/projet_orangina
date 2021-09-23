import sys
import pygame
from enum import Enum
from pygame.locals import *
import pygame.time

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
        self._niveaudata = [[dict() for i in range(100)] for j in range(500)]
        self._orig = [0, 0]
        # Chargement des images
        self._image_brique = pygame.image.load("bloc_32.png")
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
                elif curchar == 'm':
                    self._niveaudata[x][y]['sprite'] = self._image_mechant
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

    def gestion(self):
        self._balo.gestion()

    def conversionPositionTile(self, position_tile):
        return [position_tile[0] * 32, position_tile[1] * 32]

    def conversionPositionPixelEcran(self, position_pixel_niveau):
        return [position_pixel_niveau[0] + self._orig[0], position_pixel_niveau[1] + self._orig[1]]

    def conversionPositionPixelNiveauVersTile(self, position_pixel_niveau):
        return [int(position_pixel_niveau[0] / 32), int(position_pixel_niveau[1] / 32)]

    def collision(self, position_pixel_niveau, vitesse_pixel=[0, 0]):
        # Calcul de la prochaine position du pixel
        prochaine_position_pixel_niveau = [position_pixel_niveau[0]+vitesse_pixel[0],
                                           position_pixel_niveau[1]+vitesse_pixel[1]]
        # Calcul du tile dans laquelle se trouve le pixel
        position_tile = self.conversionPositionPixelNiveauVersTile(position_pixel_niveau)
        prochaine_position_tile = self.conversionPositionPixelNiveauVersTile(prochaine_position_pixel_niveau)
        tile =  self._niveaudata[position_tile[0]][position_tile[1]]
        if tile:
            sprite = tile['sprite']
            if sprite:
                # On met la position a jour hors collision
                position_pixel_niveau[1] = self.conversionPositionTile(position_tile)[1] - 1
                return True
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

class Balo(Personnage):

    def __init__(self, position_tile, niveau):
        super().__init__(position_tile, niveau)
        self._niveau = niveau
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._image_balo_d = pygame.image.load("balo.png")
        self._image_balo_g = pygame.transform.flip(self._image_balo_d, True, False)
        self._vitesse = [1, 0]
        self._saut = SautBalo.RIEN
        self._cycle_saut = 0
        self._direction = Direction.DROITE

    def dessine(self, ecran):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        #position_balo_ecran = (self._position_pieds[0] + orig - 16, position_pieds_balo[1] - 64)
        if self._direction == Direction.DROITE:
            ecran.blit(self._image_balo_d, (position_ecran[0] - 16, position_ecran[1] - 64) )
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

    def gestion(self):
        # print(self._saut)
        # print(self._cycle_saut)
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
            self._vitesse[1] = 0
            self._saut = SautBalo.RIEN

        # Mise à jour de la position
        self._position_pieds[0] += self._vitesse[0]
        self._position_pieds[1] += self._vitesse[1]



niveau = Niveau()

orig = 0
position_pieds_balo = [niveau._position_tile_balo[0]*32 + 16, niveau._position_tile_balo[1]*32 + 32]
acceleration_saut_balo = 0
cycle = 0

while 1:
    cycle += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # On s'occupe du clavier
    touches_pressees = pygame.key.get_pressed()

    if touches_pressees[K_a]:
        orig += 1
    if touches_pressees[K_z]:
        orig -= 1
    if touches_pressees[K_LEFT]:
        niveau._balo.court_a_gauche()
    elif touches_pressees[K_RIGHT]:
        niveau._balo.court_a_droite()
    else:
        niveau._balo.stoppe()
    if touches_pressees[K_SPACE]:
        niveau._balo.saute()

    niveau.gestion()

    # Dessin, 1 cycle sur 4
    if cycle % 4 == 0:
        #ecran.fill(black)
        ecran.blit(image_ciel, image_ciel_rect)

        # Calcul de la position de la camera
        tiers_ecran = taille_ecran[0]/3
        deuxtiers_ecran = tiers_ecran*2
        if (orig + niveau._balo._position_pieds[0]) < tiers_ecran:
            orig = tiers_ecran - niveau._balo._position_pieds[0]
        if (orig + niveau._balo._position_pieds[0]) > deuxtiers_ecran:
            orig = deuxtiers_ecran - niveau._balo._position_pieds[0]

        # Dessin du niveau
        niveau.change_origine(orig)
        niveau.dessine(ecran)

        pygame.display.flip()
        pygame.time.Clock().tick(60)
