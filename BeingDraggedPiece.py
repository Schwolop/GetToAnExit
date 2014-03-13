import pygame

import RoadPiece
        

class BeingDraggedPiece(RoadPiece.RoadPiece):
    def __init__(self, the_game, filename, position, orientation_from_north, north_oriented_exits):
        # Call the parent class (RoadPiece) constructor
        RoadPiece.RoadPiece.__init__(self, the_game, filename, position, north_oriented_exits)

        if orientation_from_north%90!=0: # If the orientation is not a multiple of 90, throw an exception.
            raise ValueError("Orientation of BeingDraggedPiece in constructor is not a multiple of 90 degrees.")

        # Rotate piece.
        self.rotate_to_face_direction(["N","W","S","E"][int(orientation_from_north/90)])

    def move(self,position):
        RoadPiece.RoadPiece.move(self,position) # Call base class.
        # Update highlighted boundary.
        retVal, _ = self.the_game.board.can_piece_be_placed_here(self.filename, self.rect.center, self.orientation, self.north_oriented_exits)
        colour = (0,255,0) if retVal else (255,0,0)
        pygame.draw.rect(self.image, colour, (0,0,self.rect.width,self.rect.height), 3)