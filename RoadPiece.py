import pygame


class RoadPiece(pygame.sprite.Sprite):
    size = 32
    def __init__(self, the_game, filename, position, orientation, exits):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game

        self.filename = filename
        self.original_image = pygame.image.load(self.filename)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.orientation = orientation  # Degrees anti-clockwise from -y (Up or North)
        self.exits = exits
        self.exit_list = list(exits.upper())# The list of directions out from (or into) which another tile can come (or go).
        self.exit_list.sort()

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

    def move(self,position,direction_to_face=None):
        self.rect.center = position
        if direction_to_face:
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
        #TODO: Rotate exits too.

    def reverse_exit_list(self):
        reversed_exit_list = []
        for exit in self.exit_list:
            if exit == "N":
                reversed_exit_list.append( "S" )
            elif exit == "E":
                reversed_exit_list.append( "W" )
            elif exit == "S":
                reversed_exit_list.append( "N" )
            elif exit == "W":
                reversed_exit_list.append( "E" )
        reversed_exit_list.sort()
        return reversed_exit_list

    def can_pieces_mate(self,other):
        # Returns true if this and another piece have exits that could mate (if the pieces were touching along this edge).
        reversed_exit_list = self.reverse_exit_list()
        return any((True for exit in reversed_exit_list if exit in other.exits))