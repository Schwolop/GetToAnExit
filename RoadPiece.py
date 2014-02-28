import pygame

import Game

class RoadPiece(pygame.sprite.Sprite):
    size = 32
    def __init__(self, the_game, filename, position):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game
        self.original_image = pygame.image.load(filename)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = self.centre_of_cell(position)
        self.orientation = 0  # Initially UP, degrees from -y
        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

    def move(self,position,orientation):
        self.rect.center = self.centre_of_cell(position)
        self.orientation = orientation
        self.image = pygame.transform.rotate(self.original_image, self.orientation)

    def centre_of_cell(self, position):
        return (int(position[0] / self.size) * self.size + self.size/2, int(position[1] / self.size) * self.size + self.size/2)