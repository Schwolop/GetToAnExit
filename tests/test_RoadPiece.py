import unittest
import os

import Board
import RoadPiece
import BoardPiece


class MockSpriteGroup:
    def __init__(self):
        pass
    def add(self,_,**kwargs):
        pass


class MockGame:
    def __init__(self):
        self.objects_to_draw = MockSpriteGroup()
        self.board = Board.Board(self,[0,0,RoadPiece.RoadPiece.size*16,RoadPiece.RoadPiece.size*10])


class Test_RoadPiece(unittest.TestCase):

    def setUp(self):
        self.the_game = MockGame()
        self.board = self.the_game.board

    def test_reverse_exits(self):
        # Cell bounds are the half-interval [0,cellSize) in each dimension.
        self.assertEqual( ["E","N","S","W"], RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NEWS").reverse_exit_list() )
        self.assertEqual( ["E","N"], RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "WS").reverse_exit_list() )
        self.assertEqual( [], RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "").reverse_exit_list() )

    def test_can_pieces_mate(self):
        self.assertTrue( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NEWS").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NEWS")) )
        self.assertTrue( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "N").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "S")) )
        self.assertFalse( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NEWS")) )
        self.assertFalse( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NS").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "EW")) )

    def test_rotate_to_face_direction(self):
        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "N")
        test_piece.rotate_to_face_direction("N") # Turning by zero degrees does nothing to exit_list.
        self.assertEqual( ["N"], test_piece.exit_list )

        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "N")
        test_piece.rotate_to_face_direction("E") # Turning a piece with a North exit to face East, should yield an East exit.
        self.assertEqual( ["E"], test_piece.exit_list )

        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NEW")
        test_piece.rotate_to_face_direction("E") # Turning a piece with NEW exits to face East, should yield an ESN exits.
        self.assertEqual( ["E","N","S"], test_piece.exit_list )

        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "N")
        test_piece.rotate_to_face_direction("S") # Turning a piece with a North exit to face South, should yield a South exit.
        self.assertEqual( ["S"], test_piece.exit_list )

        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NEW")
        test_piece.rotate_to_face_direction("S") # Turning a piece with NEW exits to face South, should yield SWE exits.
        self.assertEqual( ["E","S","W"], test_piece.exit_list )

        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "N")
        test_piece.rotate_to_face_direction("W") # Turning a piece with a North exit to face West, should yield a West exit.
        self.assertEqual( ["W"], test_piece.exit_list )

        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "NEW")
        test_piece.rotate_to_face_direction("W") # Turning a piece with NEW exits to face West, should yield WNS exits.
        self.assertEqual( ["N","S","W"], test_piece.exit_list )

        test_piece = RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), "N")
        test_piece.rotate_to_face_direction("S") # Turning a piece with a North exit to face South, should yield a South exits.
        self.assertEqual( ["S"], test_piece.exit_list )
        test_piece.rotate_to_face_direction("S") # Turning it again to face South, should yield a North exit.
        self.assertEqual( ["N"], test_piece.exit_list )
        test_piece.rotate_to_face_direction("W") # Turning it again to face West, should yield a West exit.
        self.assertEqual( ["W"], test_piece.exit_list )
        test_piece.rotate_to_face_direction("E") # Turning it again to face East, should yield a North exit.
        self.assertEqual( ["N"], test_piece.exit_list )

if __name__ == '__main__':
    unittest.main()