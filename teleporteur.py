from personnage import *
import pygame

#c'est le "e" la lettre.

_destinations = dict[str, list]()

class Teleporteur(Personnage):

    def __init__(self, position_tile, niveau, extradata):
        super().__init__(position_tile, niveau)
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._images = [
            pygame.image.load("teleporteur_1.png"),
            pygame.image.load("teleporteur_2.png")
        ]
        self._animation = 0
        # On ajoute ce téléporteur à la liste des destinations
        self._destination = extradata["destination"]
        if self._destination not in _destinations:
            _destinations[self._destination] = list()
        _destinations[self._destination].append(self)

    def dessine(self, ecran : pygame.Surface):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        ecran.blit(self._images[int(self._animation/30)%2], (position_ecran[0] - 16, position_ecran[1] - 32))
        pass

    def gestion(self):
        self._animation += 1
        pass

    def actionne(self):
        print("TP action")
        # On recherche les destinations
        for dest in _destinations[self._destination]:
            if dest is self: # si c'est nous (le point de depart), on n'y va pas
                pass
            else: # sinon, on se téléporte
                self._niveau._balo._position_pieds = dest._position_pieds.copy()
                return
        pass
    