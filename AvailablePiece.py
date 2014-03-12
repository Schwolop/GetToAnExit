import RoadPiece


class AvailablePiece(RoadPiece.RoadPiece):
    def __init__(self, the_game, filename, position, orientation_from_north, north_oriented_exits):
        RoadPiece.RoadPiece.__init__(self, the_game, filename, position, north_oriented_exits)  # Call the parent class (RoadPiece) constructor

        if orientation_from_north%90!=0: # If the orientation is not a multiple of 90, throw an exception.
            raise ValueError("Orientation of AvailablePiece in constructor is not a multiple of 90 degrees.")

        # Rotate piece.
        self.rotate_to_face_direction(["N","W","S","E"][int(orientation_from_north/90)])
