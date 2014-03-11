import unittest
import os

import Board
import RoadPiece
import BoardPiece


class MockSpriteGroup:
    def __init__(self):
        pass
    def add(self,_):
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
        self.assertEqual( ["E","N","S","W"], RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "NEWS").reverse_exit_list() )
        self.assertEqual( ["E","N"], RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "WS").reverse_exit_list() )
        self.assertEqual( [], RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "").reverse_exit_list() )

    def test_can_pieces_mate(self):
        self.assertTrue( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "NEWS").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "NEWS")) )
        self.assertTrue( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "N").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "S")) )
        self.assertFalse( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "NEWS")) )
        self.assertFalse( RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "NS").can_pieces_mate(RoadPiece.RoadPiece( self.the_game, os.path.join("tests","test_piece.png"), (0,0), 0, "EW")) )

if __name__ == '__main__':
    unittest.main()