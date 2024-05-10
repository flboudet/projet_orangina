from personnage import *
import pygame

class Volcan(Personnage):

    def __init__(self, position_tile, niveau, extradata):
        super().__init__(position_tile, niveau)
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._images = [
            pygame.image.load("volcan_1.png"),
            pygame.image.load("volcan_2.png"),
            pygame.image.load("volcan_3.png")
        ]
        self._animation = 0
        

    def dessine(self, ecran : pygame.Surface):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        ecran.blit(self._images[int(self._animation/30)%2], (position_ecran[0] - 16, position_ecran[1] - 32))
        pass

    def gestion(self):
        self._animation += 1
        pass

    def actionne(self):
        print("Volcan action")
        self._niveau._balo._position_pieds = [self._position_pieds[0] + 16, self._position_pieds[1]]
        self._niveau._balo.saute(-20)
        pass
    
    def distanceAction(self):
        return 40