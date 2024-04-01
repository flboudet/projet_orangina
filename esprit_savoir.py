from personnage import *
from enum import Enum
import pygame
import ame_perdue

#c'est le "e" la lettre.
class EtatEspritSavoir(Enum):
    JAMAIS_PARLE = 0
    PREMIER_DIALOGUE = 1
    EN_TRAIN_DE_SE_TRANSFORMER = 2
    TRANSFORME_EN_FANTOME = 3
    QUETE_DES_ESPRITS = 4
    FIN_QUETE = 5
    FIN_QUETE_ANIM = 6
    FIN_QUETE_DIALOGUE = 7
    MODE_TOUTOU = 8



class EspritSavoir(Personnage):
    _esprit_savoir = None

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
        self._images_fantom_reverse = self._images_fantom.copy()
        self._images_fantom_reverse.reverse()

        self._images = self._images_esprit
        self._flacons = [
            pygame.image.load("Flacon_0.png"),
            pygame.image.load("Flacon_1.png"),
            pygame.image.load("Flacon_2.png"),
            pygame.image.load("Flacon_3.png"),
            pygame.image.load("Flacon_4.png")
        ]

        self._animation = 0
        self._texte_1 = extradata["text_1"]
        self._texte_2 = extradata["text_2"]
        self._texte_3 = extradata["text_3"]
        self._texte_fin_quete = extradata["text_4"]
        self._texte_fin_quete_2 = extradata["text_5"]
        self._etat_esprit = EtatEspritSavoir.JAMAIS_PARLE
        EspritSavoir._esprit_savoir = self
        self._nombre_esprits = 0

    def dessine(self, ecran : pygame.Surface):
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        imagesCount = len(self._images)
        ecran.blit(self._images[int(self._animation/30)%imagesCount], (position_ecran[0] - 16, position_ecran[1] - 32))
        if self._etat_esprit == EtatEspritSavoir.QUETE_DES_ESPRITS:
            ecran.blit(self._flacons[self._nombre_esprits % 4], (10, ecran.get_height() - 50))
        pass

    def gestion(self):
        self._animation += 1
        if self._etat_esprit == EtatEspritSavoir.EN_TRAIN_DE_SE_TRANSFORMER:
            if self._animation == 149:
                self._etat_esprit = EtatEspritSavoir.TRANSFORME_EN_FANTOME
                self._images = self._images_fantom_cycle

        elif self._etat_esprit == EtatEspritSavoir.FIN_QUETE_ANIM:
            if self._animation == 149:
                self._niveau.afficheDialogue(self._texte_fin_quete_2)
                self._etat_esprit = EtatEspritSavoir.MODE_TOUTOU
                self._images = self._images_esprit

        elif self._etat_esprit == EtatEspritSavoir.MODE_TOUTOU:
            balo = self._niveau._balo
            cible = balo._position_pieds.copy()
            if balo._direction == Direction.DROITE:
                cible[0] -= 32
                cible[1] -= 32
            else:
                cible[0] += 32
                cible[1] -= 32
            self._position_pieds[0] += (cible[0] - self._position_pieds[0])/10.
            self._position_pieds[1] += (cible[1] - self._position_pieds[1])/10.
            
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
            self._etat_esprit = EtatEspritSavoir.QUETE_DES_ESPRITS
            ame_perdue.AmePerdue.indiceProchaineAme()

        elif self._etat_esprit == EtatEspritSavoir.QUETE_DES_ESPRITS:
            if self._nombre_esprits < 4:
                self._niveau.afficheDialogue(self._texte_3.format(4-self._nombre_esprits))
            else:
                self._niveau.afficheDialogue(self._texte_fin_quete)
                self._etat_esprit = EtatEspritSavoir.FIN_QUETE
        
        elif self._etat_esprit == EtatEspritSavoir.FIN_QUETE:
            self._niveau.afficheDialogue("")
            self._images = self._images_fantom_reverse
            self._animation = 0
            self._etat_esprit = EtatEspritSavoir.FIN_QUETE_ANIM
