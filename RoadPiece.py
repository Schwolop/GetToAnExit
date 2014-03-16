import pygame


class RoadPiece(pygame.sprite.Sprite):
    size = 64
    def __init__(self, the_game, filename, position, north_oriented_exits):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor

        self.the_game = the_game

        self.filename = filename
        self.original_image = pygame.transform.scale2x( pygame.image.load(self.filename) )
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.north_oriented_exits = north_oriented_exits # Like original image, these are the exits when the piece is north-oriented.
        self.exit_list = RoadPiece.exit_string_to_list(self.north_oriented_exits) # This exit_list is always the "current" list, given the "current" orientation.
        self.orientation = 0 # Set to a default value. Subsequent rotations will adjust this.

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self, layer=5)

    @staticmethod
    def exit_string_to_list(exits):
        exit_list = list(exits.upper())# The list of directions out from (or into) which another tile can come (or go).
        exit_list.sort()
        return exit_list

    @staticmethod
    def rotate_north_oriented_exit_list(north_oriented_exit_list, orientation_from_north):
        if orientation_from_north%90!=0: # If the orientation is not a multiple of 90, throw an exception.
            raise ValueError("Orientation is not a multiple of 90 degrees.")
        exit_list = north_oriented_exit_list
        for j in range(int(orientation_from_north/90)):
            for i,exit in enumerate(exit_list):
                if exit == "N":
                    exit_list[i]="W"
                elif exit == "E":
                    exit_list[i]="N"
                elif exit == "S":
                    exit_list[i]="E"
                elif exit == "W":
                    exit_list[i]="S"
        exit_list.sort()
        return exit_list

    def move(self,position):
        self.rect.center = position

    def centre_of_cell(self, position):
        return (int(position[0] / self.size) * self.size + self.size/2, int(position[1] / self.size) * self.size + self.size/2)

    def rotate_to_face_direction(self,direction_to_face):
        turns = {'N':0,'E':3,'S':2,'W':1} # Number of 90d turns anti-clockwise to make.
        direction_to_face = direction_to_face.upper()
        self.orientation = 90*turns[direction_to_face]
        self.image = pygame.transform.rotate( self.original_image, self.orientation )
        # Rotate the exits too.
        for i in range(turns[direction_to_face]):
            self.exit_list = self.rotate_exit_list_once_anticlockwise()

    def reverse_exit_list(self):
        reversed_exit_list = self.exit_list[:] # Copy it.
        for i,exit in enumerate(reversed_exit_list):
            if exit == "N":
                reversed_exit_list[i]="S"
            elif exit == "E":
                reversed_exit_list[i]="W"
            elif exit == "S":
                reversed_exit_list[i]="N"
            elif exit == "W":
                reversed_exit_list[i]="E"
        reversed_exit_list.sort()
        return reversed_exit_list

    def rotate_exit_list_once_anticlockwise(self):
        rotated_exit_list = self.exit_list[:] # Copy it.
        for i,exit in enumerate(rotated_exit_list):
            if exit == "N":
                rotated_exit_list[i]="W"
            elif exit == "E":
                rotated_exit_list[i]="N"
            elif exit == "S":
                rotated_exit_list[i]="E"
            elif exit == "W":
                rotated_exit_list[i]="S"
        rotated_exit_list.sort()
        return rotated_exit_list

    def can_pieces_mate(self,other):
        # Returns true if this and another piece have exits that could mate (if the pieces happened to be touching
        # along this edge). This function uses each piece's _current_ rotation (hence 'exits', not
        # 'north_oriented_exits', but doesn't look at their current positions.
        reversed_exit_list = self.reverse_exit_list()
        return any((True for exit in reversed_exit_list if exit in other.exit_list))
