import sys
import pygame
from enum import Enum
from pygame.locals import *
import pygame.time
from pygame import mixer

import yaml
import re
from personnage import *
from drakha import *
from papition import *
from dialogue import *
from esprit_des_nuages import *
from esprit_savoir import *
from esprit_vendeur import *
from bloc_sauvegarde import *
from piece import *

from ame_perdue import *
from teleporteur import *
from dimmer import *
from hints import *
from volcan import *

print("Projet Orangina")

pygame.init()

taille_ecran = 800, 600
#ecran = pygame.display.set_mode(size = taille_ecran, flags=pygame.SCALED|pygame.DOUBLEBUF|pygame.SHOWN|pygame.FULLSCREEN)
ecran = pygame.display.set_mode(size = taille_ecran, flags=pygame.SCALED|pygame.DOUBLEBUF|pygame.SHOWN)

print("SDL version:{0}".format(pygame.get_sdl_version()))
print("SDL backend: {0}".format(pygame.display.get_driver()))
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
    
    def isPlatform(self):
        return True
    
    def collision(self):
        pass

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

class Bloc_golder(Bloc):
    def __init__(self):
        self._image_golder = pygame.image.load("pierre_golder.png")
        super().__init__(self._image_golder)

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
        self._niveaudata = [[dict() for i in range(1000)] for j in range(1000)]
        self._orig = [0, 0]
        self._affiche_dialogue = False
        # Chargement des images
        self._image_mechant = pygame.image.load("mechant.png")

        # Chargement du niveau
        self.charge("niveau_1.txt")

        # Indice
        self._hints = Hints(self)

    def afficherIndice(self, coords):
        self._hints.setObjectif(coords)
        pass

    def charge(self, cheminNiveau):
        extraniveau = open(cheminNiveau + ".yaml")
        extraniveau_data = yaml.load(extraniveau, Loader=yaml.Loader)
        print(extraniveau_data)
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
                elif curchar == 'G':
                    self._niveaudata[x][y]['bloc'] = Bloc_golder()
                elif curchar == 'm':
                    mechant = Drhaka([x, y], self)
                    self._personnages.append(mechant)
                elif re.match("[0-9]", curchar):
                    extradata = extraniveau_data["object"][int(curchar)]
                    klass = globals()[extradata["class"]]
                    perso = klass([x, y], self, extradata)
                    #perso = EspritDesNuages([x, y], self, extradata)
                    self._personnages.append(perso)
                elif curchar == 'p':
                    mechant = Papition([x, y], self)
                    self._personnages.append(mechant)
                    #self._niveaudata[x][y]['bloc'] = Bloc_papillon()
                elif curchar == '*':
                    self._niveaudata[x][y]['bloc'] = Piece([x, y], self)
                else:
                    self._niveaudata[x][y]['sprite'] = None
                x += 1
            y += 1

    def change_origine(self, origx=0, origy=0):
        self._orig = [origx, origy]

    def dessine(self, ecran : pygame.Surface, cycle):
        # Dessiner uniquement ce qu'on voit à l'écran
        first_tile_x = int(-self._orig[0] / 32) - 1
        last_tile_x = int(first_tile_x + (taille_ecran[0]/32)) + 2
        first_tile_y = int(-self._orig[1] / 32) - 1
        last_tile_y = int(first_tile_y + (taille_ecran[1]/32)) + 2

        for x in range(first_tile_x, last_tile_x): #range(len(self._niveaudata)):
            for y in range(first_tile_y, last_tile_y): #range(len(self._niveaudata[x])):
                if self._niveaudata[x][y]:
                    bloc = self._niveaudata[x][y]['bloc']
                    if bloc:
                        bloc.dessine(ecran, (x*32 + self._orig[0], y*32 + self._orig[1]), cycle=cycle)
        # Dessiner les personnages et objets spéciaux
        for personnage in self._personnages:
            if personnage.derriereBalo():
                personnage.dessine(ecran)
        # Dessiner Balo
        self._balo.dessine(ecran)
        # Dessiner les personnages et objets spéciaux
        for personnage in self._personnages:
            if not personnage.derriereBalo():
                personnage.dessine(ecran)
        # Dessiner le dialogue
        if self._affiche_dialogue:
            self._dialogue.dessine(ecran)
        # Dessiner les indices
        self._hints.dessine(ecran)

    def afficheDialogue(self, texte):
        if len(texte):
            self._affiche_dialogue = True
            self._dialogue = Dialogue(texte)
        else:
            self._affiche_dialogue = False

    def gestion(self):
        for personnage in self._personnages:
            personnage.gestion()
        self._balo.gestion()
        if self._affiche_dialogue:
            self._dialogue.gestion()


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
                sprite.collision()
                if sprite.isPlatform():
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
            # print("Collision en X")
            result = True
        else:
            position_pixel_niveau[0] += vitesse_pixel[0]

        # On regarde s'il y aura une collision en Y
        prochaine_position_pixel_niveau_y = [position_pixel_niveau[0],
                                            position_pixel_niveau[1]+vitesse_pixel[1]]
        # S'il y a collision, on annule la vitesse en Y
        if self.pixel_en_collision(prochaine_position_pixel_niveau_y):
            position_tile = self.conversionPositionPixelNiveauVersTile(prochaine_position_pixel_niveau_y)
            position_tile_pixel = self.conversionPositionTile(position_tile)
            if vitesse_pixel[1] < 0:
                position_pixel_niveau[1] = position_tile_pixel[1]+33
            else:
                position_pixel_niveau[1] = position_tile_pixel[1]-0.1
            vitesse_pixel[1] = 0
            # print("Collision en Y")
            result = True
        else:
            position_pixel_niveau[1] += vitesse_pixel[1]

        return result

class SautBalo(Enum):
    RIEN = 0
    SAUT_COURT = 1
    SAUT_MOYEN = 2
    SAUT_LONG  = 3

class Balo(Personnage):
    _niveau : Niveau

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

        self._image_balo_feu_d = [pygame.image.load("balo_crache_1.png"),
                                  pygame.image.load("balo_crache_2.png"),
                                  pygame.image.load("balo_crache_3.png")]
        self._image_balo_feu_g = [pygame.transform.flip(x, True, False) for x in self._image_balo_feu_d]

        self._image_balo_prend_d = [pygame.image.load("balo_ramasse_1.png"),
                                    pygame.image.load("balo_ramasse_2.png")]
        self._image_balo_prend_g = [pygame.transform.flip(x, True, False) for x in self._image_balo_prend_d]

        self._vitesse = [0, 0]
        self._saut = SautBalo.RIEN
        self._cycle_marche = 0
        self._cycle_saut = 0
        self._direction = Direction.DROITE
        self._en_course = False
        self._crache = 0
        self._prend = 0
        self._vies = 3
        self._energie = 4
        self._invulnerable = 0
        self._derniere_position_posee = self._position_pieds.copy()

    def getPositionPixel(self):
        return self._position_pieds

    def dessine(self, ecran):
        # Clignottement quand on est invulnérable
        if self._invulnerable > 0:
            if self._invulnerable % 30 > 15:
                return

        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        #position_balo_ecran = (self._position_pieds[0] + orig - 16, position_pieds_balo[1] - 64)
        if self._direction == Direction.DROITE:
            if self._crache == 0 and self._prend == 0:
                ecran.blit(self._image_balo_d[(int(self._cycle_marche/20)) % 3], (position_ecran[0] - 16, position_ecran[1] - 64) )
            elif self._crache > 0:
                if self._crache < 10:
                    ecran.blit(self._image_balo_feu_d[0], (position_ecran[0] - 16, position_ecran[1] - 64) )
                elif self._crache < 20:
                    ecran.blit(self._image_balo_feu_d[1], (position_ecran[0] - 16, position_ecran[1] - 64) )
                elif self._crache < 70:
                    ecran.blit(self._image_balo_feu_d[2], (position_ecran[0] - 16, position_ecran[1] - 64) )
                elif self._crache < 80:
                    ecran.blit(self._image_balo_feu_d[1], (position_ecran[0] - 16, position_ecran[1] - 64) )
                else:
                    ecran.blit(self._image_balo_feu_d[0], (position_ecran[0] - 16, position_ecran[1] - 64) )
            elif self._prend > 0:
                if self._prend < 50:
                    ecran.blit(self._image_balo_prend_d[0], (position_ecran[0] - 16, position_ecran[1] - 64) );
                else:
                    ecran.blit(self._image_balo_prend_d[1], (position_ecran[0] - 16, position_ecran[1] - 64) );
        else: # Direction.GAUCHE
            if self._prend == 0:
                if self._crache > 0:
                    if self._crache < 10:
                        image = self._image_balo_feu_g[0]
                    elif self._crache < 20:
                        image = self._image_balo_feu_g[1]
                    elif self._crache < 70:
                        image = self._image_balo_feu_g[2]
                    elif self._crache < 80:
                        image = self._image_balo_feu_g[1]
                    else:
                        image = self._image_balo_feu_g[0]
                else:
                    image = self._image_balo_g[(int(self._cycle_marche/20)) % 3]
            else:
                if self._prend < 50:
                    image = self._image_balo_prend_g[0]
                else:
                    image = self._image_balo_prend_g [1]
            if image.get_width() == 64:
                ecran.blit(image, (position_ecran[0] - 16 - 32, position_ecran[1] - 64) )
            else:
                ecran.blit(image, (position_ecran[0] - 16, position_ecran[1] - 64) )
        pass

    def court_a_droite(self):
        self._vitesse[0] = 2
        self._en_course = True
        self._direction = Direction.DROITE

    def court_a_gauche(self):
        self._vitesse[0] = -2
        self._en_course = True
        self._direction = Direction.GAUCHE

    def stoppe(self):
        self._vitesse[0] = 0
        self._en_course = False

    def saute(self, dvitesse = -3):
        if self._saut == SautBalo.RIEN:
#            mixer.Sound.play(son_saut)
            self._saut = SautBalo.SAUT_COURT
            self._cycle_saut = 0
            self._vitesse[1] = dvitesse
        elif self._cycle_saut > 20:
            self._saut = SautBalo.SAUT_LONG
        elif self._cycle_saut > 9:
            self._saut = SautBalo.SAUT_MOYEN

    def crache(self):
        self._crache = 1
        pass

    def prend(self):
        self._prend = 1
        pass

    def action(self):
        for perso in self._niveau._personnages:
            if perso != self:
                distance_perso = self.distance(perso)
                if distance_perso < perso.distanceAction():
                    perso.actionne()
                    return;


    def perteVie(self):
        self._vies = self._vies - 1
        self._energie = 4
        self._position_pieds = self._position_pieds_origine.copy() # self._derniere_position_posee.copy()
        self._vitesse = [0,0]
        self._saut = SautBalo.RIEN
        fondu = Dimmer(1)
        for i in range(64):
            fondu.dim(i)
            pygame.time.Clock().tick(60)

    def perteEnergie(self, quantite):
        if self._invulnerable:
            return
        
        self.stoppe()
        if self._direction == Direction.DROITE:
            self._vitesse = [-10, -5]
        else:
            self._vitesse = [10, -5]
        self._energie -= quantite
        self._invulnerable = 500
        if self._energie < 1:
            self.perteVie()

    def gestion(self):
        # print(self._position_pieds)
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
        # Gestion du prend
        if self._prend > 0:
            self._prend += 1
            if self._prend == 100:
                self._prend = 0
        # Gestion de la gravité et des sauts
        if self._saut == SautBalo.RIEN \
                 or (self._saut == SautBalo.SAUT_COURT and self._cycle_saut > 20) \
                 or (self._saut == SautBalo.SAUT_MOYEN and self._cycle_saut > 40) \
                 or (self._saut == SautBalo.SAUT_LONG  and self._cycle_saut > 60):
            self._vitesse[1] += 0.3
            # Gestion du freinage
            if not self._en_course:
                self._vitesse[0] /= 1.3
            if abs(self._vitesse[0]) < 0.4:
                self._vitesse[0] = 0
            # self._saut = SautBalo.RIEN
        else:
            self._cycle_saut += 1

        # Detection collision
        if niveau.collision(self._position_pieds, self._vitesse):
            #self._vitesse[1] = 0
            self._saut = SautBalo.RIEN
            # on mémorise la dernière plateforme sur laquelle on s'est posé
            self._derniere_position_posee = self._position_pieds.copy()

        # Detection contact personnages (TODO: harmoniser avec collisions ?)
        for perso in self._niveau._personnages:
            if perso != self:
                distance_perso = self.distance(perso)
                if self._crache > 10:
                    if distance_perso < 40:
                        distance_x = perso._position_pieds[0] - self._position_pieds[0]
                        if ((self._direction == Direction.DROITE) and (distance_x > 0)) or ((self._direction == Direction.GAUCHE) and (distance_x < 0)):
                            if abs(perso._position_pieds[1] - self._position_pieds[1]) < 5:
                                perso.dansLeFeu()
                if distance_perso < 28:
                    perso.contact()

        # Mise à jour de la position
        #self._position_pieds[0] += self._vitesse[0]
        #self._position_pieds[1] += self._vitesse[1]

        # Gestion de l'invulnérabilité
        if self._invulnerable > 0:
            self._invulnerable -= 1

        # Si Balo est à y=+1000 de sa dernière position posée il est tombé dans un trou
        if self._position_pieds[1] - self._derniere_position_posee[1] > 1200:
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

energies = [pygame.image.load("vie_1.png"),
            pygame.image.load("vie_2.png"),
            pygame.image.load("vie_3.png"),
            pygame.image.load("vie_4.png")]
gigot = pygame.image.load("gigot.png")
font = pygame.font.SysFont(None, 32)

_actionne = False

# Masque de la nuit 0.00028935
nuit = pygame.Surface(ecran.get_size())
nuit.fill((0,0,50))           # this fills the entire surface
cycle_nuit = 0
delta_nuit = 0.0028935

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
        if not _actionne:
            niveau._balo.action()
            _actionne = True
    else:
        _actionne = False

    if touches_pressees[K_f]:
        niveau.afficheDialogue("")

    if touches_pressees[K_LEFT]:
        if not niveau._balo._en_course:
            niveau._balo.court_a_gauche()
    elif touches_pressees[K_RIGHT]:
        if not niveau._balo._en_course:
            niveau._balo.court_a_droite()
    else:
        if niveau._balo._en_course:
            niveau._balo.stoppe()
    
    if touches_pressees[K_SPACE]:
        niveau._balo.saute()
    if touches_pressees[K_w]:
        niveau._balo.crache()

    niveau.gestion()

    # Dessin, 1 cycle sur 4
    if cycle % 4 == 0:
        #ecran.fill(black)
        cycle_nuit += delta_nuit
        if cycle_nuit > 164:
            delta_nuit = -delta_nuit
        if cycle_nuit < 0:
            delta_nuit = -delta_nuit
        nuit.set_alpha(cycle_nuit)                # alpha level
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

        # Dessin de la nuit
        ecran.blit(nuit, (0,0))
        # Dessin du nombre de vies
        ecran.blit(gigot, (10, 0))
        texteVies = "x{0}".format(niveau._balo._vies)
        vies = font.render(texteVies, False, pygame.color.THECOLORS["goldenrod1"])
        viesdark = font.render(texteVies, False, pygame.color.THECOLORS["black"])
        ecran.blit(viesdark, (66, 34))
        ecran.blit(vies, (64, 32))
        # Dessin de l'energie
        ecran.blit(energies[4 - niveau._balo._energie], (taille_ecran[0] - 70, 0))

        pygame.display.flip()
        pygame.time.Clock().tick(60)
