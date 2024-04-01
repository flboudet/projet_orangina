from personnage import *
import pygame

class Piece():
    def __init__(self, position_tile, niveau):
        self._image_piece = pygame.image.load("piece.png")
        self._visible = True
        #super().__init__(self._image_piece)
    
    def isPlatform(self):
        return False
    
    def collision(self):
        self._visible = False

    def dessine(self, ecran, coord, cycle):
        if self._visible:
            ecran.blit(self._image_piece, coord)


        