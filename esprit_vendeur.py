from personnage import *
import pygame

#c'est le "e" la lettre.

class EspritVendeur(Personnage):

    def __init__(self, position_tile, niveau, extradata):
        super().__init__(position_tile, niveau)
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._images = [
            pygame.image.load("esprit_des_nuages_1.png"),
            pygame.image.load("esprit_des_nuages_2.png")
        ]
        self._animation = 0
        self._texte = extradata["text_1"]
        self._texte2 = extradata["text_2"]


    def dessine(self, ecran : pygame.Surface):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        ecran.blit(self._images[int(self._animation/30)%2], (position_ecran[0] - 16, position_ecran[1] - 32))
        pass

    def gestion(self):
        self._animation += 1
        pass

    def actionne(self):
        self._niveau.afficheDialogue(self._texte)
    