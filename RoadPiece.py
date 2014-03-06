import pygame

import Game
import Board

class RoadPiece(pygame.sprite.Sprite):
    size = 32
    def __init__(self, the_game, filename, position, orientation, exits):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game

        self.original_image = pygame.image.load(filename)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = self.centre_of_cell(position)

        # Test if it's valid to create this piece here
        if not self.can_be_placed_here(self.centre_of_cell(position)):
            raise ValueError( "Road cannot be placed here." )

        self.orientation = orientation  # Degrees anti-clockwise from -y (Up or North)
        self.exits = exits.upper().split().sort() # The list of directions out from (or into) which another tile can come (or go).

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

    def move(self,position,direction_to_face):
        self.rect.center = self.centre_of_cell(position)
        self.rotate_to_face_direction(direction_to_face)

    def centre_of_cell(self, position):
        return (int(position[0] / self.size) * self.size + self.size/2, int(position[1] / self.size) * self.size + self.size/2)

    def is_connected_to(self, other):
        # returns true if self and other are connected by a pair of exits, given their positions.
        return True

    def can_be_placed_here(self, position):
        # returns true if it is valid to place this piece here (meaning the position/orientation held by self)
        if self.the_game.board.rect.collidepoint( position ):
            return True
        return False

    def rotate_to_face_direction(self,direction_to_face):
        turns = {'N':0,'E':3,'S':2,'W':1} # Number of 90d turns anti-clockwise to make.
        direction_to_face = direction_to_face.upper()
        self.orientation = 90*turns[direction_to_face]
        self.image = pygame.transform.rotate( self.original_image, self.orientation )
