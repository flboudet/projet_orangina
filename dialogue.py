import pygame

class Dialogue:
    def __init__(self, texte : str):
        self._lignes = texte.splitlines()
        self._cycle = 0
        self._caractere_actuel = 0
        # Création surface pour le dialogue
        self._surface_dialogue = pygame.Surface((600, len(self._lignes) * 32 + 10))
        self._surface_dialogue = self._surface_dialogue.convert_alpha()
    
    def gestion(self):
        if self._cycle % 3 == 0:
            self._caractere_actuel += 1
            self.rend_dialogue()
        self._cycle += 1
        pass

    def rend_dialogue(self):
        self._surface_dialogue.fill((0, 0, 100, 200))
        font = pygame.font.SysFont(None, 32)
        y = 10
        caracteres_restants = self._caractere_actuel

        for textline in self._lignes:
            if len(textline) > caracteres_restants:
                textline = textline[0:caracteres_restants]
            caracteres_restants -= len(textline)
            line = font.render(textline, True, (255, 255, 255, 255))
            self._surface_dialogue.blit(line, (10, y))
            y += 32
            if caracteres_restants < 0:
                return
            
    def dessine(self, ecran : pygame.Surface):
        ecran.blit(self._surface_dialogue, (100, ecran.get_size()[1] - self._surface_dialogue.get_size()[1] - 100))
        pass

