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

    def collision(self, position_pixel_niveau):
        # Calcul du tile dans laquelle se trouve le pixel
        position_tile = [int(position_pixel_niveau[0] / 32), int(position_pixel_niveau[1] / 32)]
        tile =  self._niveaudata[position_tile[0]][position_tile[1]]
        if tile:
            sprite = tile['sprite']
            if sprite:
                return True
        return False

class Personnage:

    def __init__(self, position_tile, niveau):
        self._position_tile = position_tile

class Balo(Personnage):

    def __init__(self, position_tile, niveau):
        super().__init__(position_tile, niveau)
        self._niveau = niveau
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._image_balo = pygame.image.load("balo.png")
        self._vitesse = [1, 0]

    def dessine(self, ecran):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        #position_balo_ecran = (self._position_pieds[0] + orig - 16, position_pieds_balo[1] - 64)
        ecran.blit(self._image_balo, (position_ecran[0] - 16, position_ecran[1] - 64) )
        pass

    def court_a_droite(self):
        self._vitesse[0] = -1

    def court_a_gauche(self):
        self._vitesse[0] = 1

    def stoppe(self):
        self._vitesse[0] = 0

    def saute(self):
        self._vitesse[1] = -1

    def gestion(self):
        self._position_pieds[0] += self._vitesse[0]
        self._position_pieds[1] += self._vitesse[1]
        self._vitesse[1] += 1
        # Detection collision
        if niveau.collision(self._position_pieds):
            self._vitesse[1] = 0

class EtatBalo(Enum):
    RIEN = 0
    SAUT_COURT = 1
    SAUT_LONG = 2

niveau = Niveau()

etat_balo = EtatBalo.RIEN
orig = 0
position_pieds_balo = [niveau._position_tile_balo[0]*32 + 16, niveau._position_tile_balo[1]*32 + 32]
acceleration_saut_balo = 0

def gestion_balo(nouvel_etat = None):
    global etat_balo
    global position_pieds_balo
    global acceleration_saut_balo

    if nouvel_etat:
        if etat_balo != nouvel_etat:
            etat_balo = nouvel_etat
            if nouvel_etat == EtatBalo.SAUT_COURT:
                pygame.mixer.Sound.play(son_saut)
                acceleration_saut_balo = -5

    # Gestion de la gravité
    acceleration_saut_balo += 1

    # Gestion des collisions
    position_pieds_balo[1] += acceleration_saut_balo


    #if etat_balo == EtatBalo.SAUT_COURT:
    #    if acceleration_saut_balo

while 1:

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # On s'occupe du clavier
    touches_pressees = pygame.key.get_pressed()

    if touches_pressees[K_a]:
        orig += 1
    if touches_pressees[K_z]:
        orig -= 1
    if touches_pressees[K_LEFT]:
        niveau._balo.court_a_droite()
    elif touches_pressees[K_RIGHT]:
        niveau._balo.court_a_gauche()
    else:
        niveau._balo.stoppe()
    if touches_pressees[K_SPACE]:
        niveau._balo.saute()
        gestion_balo(EtatBalo.SAUT_COURT)
    gestion_balo()
    niveau.gestion()
    #ecran.fill(black)
    ecran.blit(image_ciel, image_ciel_rect)

    # Dessin du niveau
    niveau.change_origine(orig)
    niveau.dessine(ecran)

    # calcul des coordonnees de balo
    #position_balo_ecran = (position_pieds_balo[0] + orig - 16, position_pieds_balo[1] - 64)
    #ecran.blit(image_balo, position_balo_ecran)
    #ecran.blit(image_brique, position_brique)
    #position_brique[1] = position_brique[1] + 1

    pygame.display.flip()
    pygame.time.Clock().tick(60)
