from personnage import *
import pygame


class BlocSauvegarde(Personnage):

    _bloc_selectionne = None

    def __init__(self, position_tile, niveau, extradata):
        super().__init__(position_tile, niveau)
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._images = [
            pygame.image.load("save_1.png"),
            pygame.image.load("save_2.png")
        ]
        self._animation = 0


    def dessine(self, ecran : pygame.Surface):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        if BlocSauvegarde._bloc_selectionne == self:
            ecran.blit(self._images[int(self._animation/30)%2], (position_ecran[0] - 16, position_ecran[1] - 32))
        else:
            ecran.blit(self._images[0], (position_ecran[0] - 16, position_ecran[1] - 32))

    def gestion(self):
        self._animation += 1
        pass

    def actionne(self):
        BlocSauvegarde._bloc_selectionne = self
        self._niveau._balo._position_pieds_origine = [self._position_pieds[0] + 16, self._position_pieds[1] + 16]
        pass
    