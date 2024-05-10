import pygame
import math

class Hints:
    def __init__(self, niveau) -> None:
        self._niveau = niveau
        self._objectif = None
        self._fleche = pygame.image.load("fleche.png")
        self._fleche_angle = dict()
        for rot in range(0, 360):
            self._fleche_angle[rot] = pygame.transform.rotate(self._fleche, rot)
        pass

    def setObjectif(self, coords):
        self._objectif = coords

    def dessine(self, ecran : pygame.Surface):
        if self._objectif:
            # Calculer la direction de l'objectif
            # c'est à dire l'angle du segment entre le centre de Balo et l'objectif
            pieds_balo = self._niveau._balo._position_pieds
            angle = math.atan2(pieds_balo[0] - self._objectif[0], pieds_balo[1] - self._objectif[1])
            angle_deg = int(math.degrees(angle))
            if angle_deg < 0:
                angle_deg += 360
            ecran.blit(self._fleche_angle[angle_deg], (700, 500))
        pass
