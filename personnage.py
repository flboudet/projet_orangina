import math
from enum import Enum

class Direction(Enum):
    GAUCHE = -1
    DROITE = 1

class Personnage:
    _position_tile : list

    def __init__(self, position_tile, niveau):
        self._position_tile = position_tile
        self._niveau = niveau
    
    def getPositionPixel(self):
        return self._niveau.conversionPositionTile(self._position_tile)

    def distanceCoords(self, coords):
        positionSelf = self.getPositionPixel()
        distanceX = positionSelf[0] - coords[0]
        distanceY = positionSelf[1] - coords[1]
        return math.sqrt(distanceX**2 + distanceY**2)
    
    def distance(self, autrePerso):
        positionSelf = self.getPositionPixel()
        positionAutre = autrePerso.getPositionPixel()
        distanceX = positionSelf[0] - positionAutre[0]
        distanceY = positionSelf[1] - positionAutre[1]
        return math.sqrt(distanceX**2 + distanceY**2)
    
    def actionne(self):
        pass
    
    def contact(self):
        pass
    
    def dansLeFeu(self):
        pass

    def distanceAction(self):
        return 96
    
    def derriereBalo(self):
        return False
