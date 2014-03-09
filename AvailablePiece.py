import RoadPiece


class AvailablePiece(RoadPiece.RoadPiece):
    def __init__(self, the_game, filename, position, orientation, exits):
        RoadPiece.RoadPiece.__init__(self, the_game, filename, position, orientation, exits)  # Call the parent class (RoadPiece) constructor
