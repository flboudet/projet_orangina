from personnage import *
import esprit_savoir
import pygame

class EtatAmePerdue(Enum):
    PAS_PRISE = 0
    EN_PRISE = 1
    PRISE = 2

class AmePerdue(Personnage):
    _toutesLesAmes = []

    def __init__(self, position_tile, niveau, extradata):
        super().__init__(position_tile, niveau)
        position_coingauche = niveau.conversionPositionTile(self._position_tile)
        self._position_pieds = [position_coingauche[0] + 16, position_coingauche[1] + 32]
        self._images = [
            pygame.image.load("ame_perdue_1.png"),
            pygame.image.load("ame_perdue_2.png"),
            pygame.image.load("ame_perdue_3.png"),
            pygame.image.load("ame_perdue_4.png")
        ]
        self._animation = 0
        self._etat = EtatAmePerdue.PAS_PRISE
        AmePerdue._toutesLesAmes.append(self)

    def dessine(self, ecran : pygame.Surface):
        if self._etat == EtatAmePerdue.PRISE:
            return
        if esprit_savoir.EspritSavoir._esprit_savoir:
            if esprit_savoir.EspritSavoir._esprit_savoir._etat_esprit.value < esprit_savoir.EtatEspritSavoir.TRANSFORME_EN_FANTOME.value:
                return
        position_ecran = self._niveau.conversionPositionPixelEcran(self._position_pieds)
        ecran.blit(self._images[int(self._animation/30)%4], (position_ecran[0] - 16, position_ecran[1] - 32))
        pass

    def gestion(self):
        self._animation += 1
        if self._etat == EtatAmePerdue.EN_PRISE:
            if self._niveau._balo._prend == 0:
                self._etat = EtatAmePerdue.PRISE
                esprit_savoir.EspritSavoir._esprit_savoir._nombre_esprits += 1
        pass

    def actionne(self):
        if esprit_savoir.EspritSavoir._esprit_savoir._etat_esprit == esprit_savoir.EtatEspritSavoir.QUETE_DES_ESPRITS:
            if self._etat ==EtatAmePerdue.PAS_PRISE:
                self._niveau._balo.prend()
                self._etat = EtatAmePerdue.EN_PRISE
                AmePerdue.indiceProchaineAme()
        pass
    
    @classmethod
    def indiceProchaineAme(cls):
        # Etape 1 : on recherche l'ame la plus proche de Balo
        pluspetitedist = 1e100
        prochaineame = None
        for ame in cls._toutesLesAmes:
            curdist = ame._niveau._balo.distance(ame)
            if curdist < pluspetitedist:
                pluspetitedist = curdist
                prochaineame = ame
        # Etape 2 : on indique l'ame la plus proche
        if prochaineame:
            prochaineame._niveau.afficherIndice(prochaineame._position_pieds)
        
