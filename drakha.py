from personnage import *
import pygame

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
        self._vitesse[1] += 0.03
        # Detection collision
        prev_vitesse_x = self._vitesse[0]
        if self._niveau.collision(self._position_pieds, self._vitesse):
            if self._vitesse[0] == 0:
                self._vitesse[0] = -prev_vitesse_x

        # Mise à jour de la position
        self._position_pieds[0] += self._vitesse[0]
        self._position_pieds[1] += self._vitesse[1]

    def getPositionPixel(self):
        return self._position_pieds

    def contact(self):
        self._niveau._balo.perteEnergie(1)
    
    def dansLeFeu(self):
        self._niveau._personnages.remove(self)
        