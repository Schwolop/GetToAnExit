import RoadPiece


class BoardPiece(RoadPiece.RoadPiece):
    def __init__(self, the_game, filename, position, orientation, exits):
        RoadPiece.RoadPiece.__init__(self, the_game, filename, position, orientation, exits)  # Call the parent class (RoadPiece) constructor

        # Centre position to a cell
        self.rect.center = self.centre_of_cell(position)

        # Test if it's valid to create this piece here
        if not self.can_be_placed_here(self.centre_of_cell(position)):
            raise ValueError( "Road cannot be placed here." )

    def move(self,position,direction_to_face):
        # Do not call base-class, instead position centred within nearest cell.
        self.rect.center = self.centre_of_cell(position)
        self.rotate_to_face_direction(direction_to_face)
