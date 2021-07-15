import sys
import pygame
from enum import Enum
from pygame.locals import *

print("Projet Orangina")

pygame.init()

taille_ecran = 800, 600
ecran = pygame.display.set_mode(taille_ecran)
image_ciel = pygame.image.load("ciel.png")
image_ciel_rect = image_ciel.get_rect()

image_brique = pygame.image.load("bloc_32.png")
image_piece = pygame.image.load("piece.png")
image_mechant = pygame.image.load("mechant.png")
image_papillon = pygame.image.load("chenille_volante.png")

image_balo = pygame.image.load("balo.png")

son_saut = pygame.mixer.Sound("sons/saut.wav")

niveaudata = [[dict() for i in range(100)] for j in range(500)]

niveau = open("niveau_1.txt")
x, y = 0, 0
for curline in niveau.readlines():
    x = 0
    for curchar in curline:
        if curchar == 'd':
            position_tile_balo = (x, y)
        elif curchar == '#':
            niveaudata[x][y]['sprite'] = image_brique
        elif curchar == 'm':
            niveaudata[x][y]['sprite'] = image_mechant
        elif curchar == 'p':
            niveaudata[x][y]['sprite'] = image_papillon
        elif curchar == '*':
            niveaudata[x][y]['sprite'] = image_piece
        else:
            niveaudata[x][y]['sprite'] = None
        x += 1
    y += 1

def dessine_niveau(niveaudata, origx=0, origy=0):
    for x in range(len(niveaudata)):
        for y in range(len(niveaudata[x])):
            if niveaudata[x][y]:
                sprite = niveaudata[x][y]['sprite']
                if sprite:
                    #print(sprite)
                    ecran.blit(sprite, (x*32 + origx, y*32 + origy))

class EtatBalo(Enum):
    RIEN = 0
    SAUT_COURT = 1
    SAUT_LONG = 2
    
etat_balo = EtatBalo.RIEN
orig = 0
position_pieds_balo = [position_tile_balo[0]*32 + 16, position_tile_balo[1]*32 + 32]
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
        position_pieds_balo[0] -= 1
    if touches_pressees[K_RIGHT]:
        position_pieds_balo[0] += 1
    if touches_pressees[K_SPACE]:
        gestion_balo(EtatBalo.SAUT_COURT)
    gestion_balo()
    #ecran.fill(black)
    ecran.blit(image_ciel, image_ciel_rect)
    
    # Dessin des briques
    dessine_niveau(niveaudata, orig)
    
    # calcul des coordonnees de balo
    position_balo_ecran = (position_pieds_balo[0] + orig - 16, position_pieds_balo[1] - 64)
    ecran.blit(image_balo, position_balo_ecran)
    #ecran.blit(image_brique, position_brique)
    #position_brique[1] = position_brique[1] + 1
    
    pygame.display.flip()
    
