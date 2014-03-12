import RoadPiece


class BoardPiece(RoadPiece.RoadPiece):
    def __init__(self, the_game, filename, position, orientation_from_north, north_oriented_exits, grid_cell):
        RoadPiece.RoadPiece.__init__(self, the_game, filename, position, north_oriented_exits)  # Call the parent class (RoadPiece) constructor
        self.grid_cell = grid_cell

        # Centre position to a cell
        self.rect.center = self.centre_of_cell(position)

        if orientation_from_north%90!=0: # If the orientation is not a multiple of 90, throw an exception.
            raise ValueError("Orientation of BoardPiece in constructor is not a multiple of 90 degrees.")

        # Rotate piece.
        self.rotate_to_face_direction(["N","W","S","E"][int(orientation_from_north/90)])

    def move(self,position):
        # Do not call base-class, instead position centred within nearest cell.
        self.rect.center = self.centre_of_cell(position)
