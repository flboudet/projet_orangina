from personnage import *
import pygame

class EtatPapition(Enum):
    TRANQUILLE = 0
    POURSUITE = 1
    RETOUR = 2

class Papition(Personnage):
    def __init__(self, position_tile, niveau):
        super().__init__(position_tile, niveau)
        self._niveau = niveau
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._position_pieds_origine = self._position_pieds.copy()
        self._images_g = [pygame.image.load("papition_1.png"),
                          pygame.image.load("papition_2.png")]
        self._images_d = [pygame.transform.flip(x, True, False) for x in self._images_g]
        self._vitesse = [0.4, 0.]
        self._t = 0
        self._animation = 0
        self._mode = EtatPapition.TRANQUILLE

    def getPositionPixel(self):
        return self._position_pieds
    
    def dessine(self, ecran):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        if self._vitesse[0] < 0:
            images = self._images_g
        else:
            images = self._images_d
        imagesCount = len(images)
        ecran.blit(images[int(self._animation/30)%imagesCount], (position_ecran[0] - 16, position_ecran[1] - 32) )

    def gestion(self):
        self._animation += 1
        self._t += 0.05
        distance_balo = self.distance(self._niveau._balo)

        if self._mode == EtatPapition.TRANQUILLE:
            # Si Balo est trop près et qu'on le regarde, on passe en mode poursuite
            if (distance_balo < 100):
                self._mode = EtatPapition.POURSUITE
            # Mise à jour de la vitesse
            self._vitesse[1] = math.sin(self._t)/2
            distance_origine = self.distanceCoords(self._position_pieds_origine)
            if distance_origine > 200:
                self._vitesse[0] = - self._vitesse[0]

        elif self._mode == EtatPapition.POURSUITE:
            position_balo = self._niveau._balo._position_pieds
            if distance_balo > 300:
                self._mode = EtatPapition.RETOUR
            if position_balo[0] < self._position_pieds[0]:
                self._vitesse[0] = -1.
            else:
                self._vitesse[0] = 1.
            if position_balo[1] < self._position_pieds[1]:
                self._vitesse[1] = -1.
            else:
                self._vitesse[1] = 1.
            pass

        elif self._mode == EtatPapition.RETOUR:
            # Si Balo est trop près et qu'on le regarde, on passe en mode poursuite
            if (distance_balo < 100):
                self._mode = EtatPapition.POURSUITE
            # Mise à jour de la vitesse
            distance_origine = self.distanceCoords(self._position_pieds_origine)
            if distance_origine < 2:
                self._position_pieds = self._position_pieds_origine.copy()
                self._mode = EtatPapition.TRANQUILLE
            else:
                if self._position_pieds_origine[0] < self._position_pieds[0]:
                    self._vitesse[0] = -1.
                else:
                    self._vitesse[0] = 1.
                if self._position_pieds_origine[1] < self._position_pieds[1]:
                    self._vitesse[1] = -1.
                else:
                    self._vitesse[1] = 1.
            pass
        
        # Mise à jour de la position
        self._position_pieds[0] += self._vitesse[0]
        self._position_pieds[1] += self._vitesse[1]

    def getPositionPixel(self):
        return self._position_pieds

    def contact(self):
        self._niveau._balo.perteEnergie(1)

    def dansLeFeu(self):
        self._niveau._personnages.remove(self)
