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
        self.exit_list = RoadPiece.exit_string_to_list(self.exits)

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

    @staticmethod
    def exit_string_to_list(exits):
        exit_list = list(exits.upper())# The list of directions out from (or into) which another tile can come (or go).
        exit_list.sort()
        return exit_list

    def move(self,position,direction_to_face=None):
        self.rect.center = position
        if direction_to_face:
            self.rotate_to_face_direction(direction_to_face)

    def centre_of_cell(self, position):
        return (int(position[0] / self.size) * self.size + self.size/2, int(position[1] / self.size) * self.size + self.size/2)

    def rotate_to_face_direction(self,direction_to_face):
        turns = {'N':0,'E':3,'S':2,'W':1} # Number of 90d turns anti-clockwise to make.
        direction_to_face = direction_to_face.upper()
        self.orientation = 90*turns[direction_to_face]
        self.image = pygame.transform.rotate( self.original_image, self.orientation )
        # Rotate the exits too.
        for i in range(turns[direction_to_face]):
            self.rotate_exit_list_once_anticlockwise()

    def reverse_exit_list(self):
        for i,exit in enumerate(self.exit_list):
            if exit == "N":
                self.exit_list[i]="S"
            elif exit == "E":
                self.exit_list[i]="W"
            elif exit == "S":
                self.exit_list[i]="N"
            elif exit == "W":
                self.exit_list[i]="E"
        self.exit_list.sort()
        return self.exit_list

    def rotate_exit_list_once_anticlockwise(self):
        for i,exit in enumerate(self.exit_list):
            if exit == "N":
                self.exit_list[i]="W"
            elif exit == "E":
                self.exit_list[i]="N"
            elif exit == "S":
                self.exit_list[i]="E"
            elif exit == "W":
                self.exit_list[i]="S"
        self.exit_list.sort()
        return self.exit_list

    def can_pieces_mate(self,other):
        # Returns true if this and another piece have exits that could mate (if the pieces were touching along this edge).
        reversed_exit_list = self.reverse_exit_list()
        return any((True for exit in reversed_exit_list if exit in other.exits))