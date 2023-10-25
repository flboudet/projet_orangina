from personnage import *
from enum import Enum
import pygame

#c'est le "e" la lettre.
class EtatEspritSavoir(Enum):
    JAMAIS_PARLE = 0
    PREMIER_DIALOGUE = 1
    EN_TRAIN_DE_SE_TRANSFORMER = 2
    TRANSFORME_EN_FANTOME = 3

class EspritSavoir(Personnage):

    def __init__(self, position_tile, niveau, extradata):
        super().__init__(position_tile, niveau)
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._images_esprit = [
            pygame.image.load("esprit_des_nuages_1.png"),
            pygame.image.load("esprit_des_nuages_2.png")
        ]
        self._images_fantom = [
            pygame.image.load("fantom_1.png"),
            pygame.image.load("fantom_2.png"),
            pygame.image.load("fantom_3.png"),
            pygame.image.load("fantom_4.png"),
        ]
        self._images_fantom_cycle = [
            pygame.image.load("fantom_5.png"),
            pygame.image.load("fantom_6.png"),
        ]
        self._images = self._images_esprit

        self._animation = 0
        self._texte_1 = extradata["text_1"]
        self._texte_2 = extradata["text_2"]
        self._etat_esprit = EtatEspritSavoir.JAMAIS_PARLE

    def dessine(self, ecran : pygame.Surface):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        imagesCount = len(self._images)
        ecran.blit(self._images[int(self._animation/30)%imagesCount], (position_ecran[0] - 16, position_ecran[1] - 32))
        pass

    def gestion(self):
        self._animation += 1
        if self._etat_esprit == EtatEspritSavoir.EN_TRAIN_DE_SE_TRANSFORMER:
            if self._animation == 149:
                self._etat_esprit = EtatEspritSavoir.TRANSFORME_EN_FANTOME
                self._images = self._images_fantom_cycle
        pass

    def actionne(self):
        if self._etat_esprit == EtatEspritSavoir.JAMAIS_PARLE:
            self._niveau.afficheDialogue(self._texte_1)
            self._etat_esprit = EtatEspritSavoir.PREMIER_DIALOGUE

        elif self._etat_esprit == EtatEspritSavoir.PREMIER_DIALOGUE:
            self._niveau.afficheDialogue("")
            self._images = self._images_fantom
            self._animation = 0
            self._etat_esprit = EtatEspritSavoir.EN_TRAIN_DE_SE_TRANSFORMER

        elif self._etat_esprit == EtatEspritSavoir.TRANSFORME_EN_FANTOME:
               self._niveau.afficheDialogue(self._texte_2)
        