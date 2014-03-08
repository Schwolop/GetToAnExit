import pygame

import Game
import Board

class AvailablePiece(pygame.sprite.Sprite):
    size = 32
    def __init__(self, the_game, filename, position, orientation, exits):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game

        self.original_image = pygame.image.load(filename)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.orientation = orientation  # Degrees anti-clockwise from -y (Up or North)
        self.exits = exits.upper().split().sort() # The list of directions out from (or into) which another tile can come (or go).

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

    def move(self,position):
        self.rect.center = position
