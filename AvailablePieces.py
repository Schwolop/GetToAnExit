import pygame

import Game
import RoadPiece

class AvailablePieces(pygame.sprite.Sprite):
    def __init__(self,the_game):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game
        self.maximum_pieces = 10
        self.border = 4
        self.spacing = 2
        self.center = ( int(self.the_game.resolution[0]/2), int(0 + self.border + RoadPiece.RoadPiece.size/2) )
        self.top_left = ( int(self.center[0] - (RoadPiece.RoadPiece.size * self.maximum_pieces/2) - self.spacing/2 - ((self.maximum_pieces/2-1) * self.spacing)), self.border)
        self.rect = pygame.Rect( *self.calculate_rect_bounds() )
        self.image = pygame.Surface(self.rect.size)
        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

    def update(self):
        # Recreate self.image and self.rect given current content.
        self.rect = pygame.Rect( *self.calculate_rect_bounds() )
        pygame.draw.rect(self.image, (255,0,0), (0,0,self.rect.width,self.rect.height), self.spacing)

    def calculate_rect_bounds(self):
        return [ self.top_left[0] - self.spacing,
                 self.top_left[1] - self.spacing,
                 (self.center[0]-self.top_left[0])*2 + self.spacing,
                 (self.center[1]-self.top_left[1])*2 + self.spacing]