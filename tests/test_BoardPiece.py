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


class Test_BoardPiece(unittest.TestCase):
    testPieceFilename = os.path.join("tests","test_piece.png")
    def setUp(self):
        self.the_game = MockGame()
        self.board = self.the_game.board

    def test_get_direction_to_neighbouring_grid_cell(self):
        piece = BoardPiece.BoardPiece(self.the_game,self.testPieceFilename,(0,0),0,"",(2,2))
        self.assertEqual( "N", piece.get_direction_to_neighbouring_grid_cell((2,1)) )  # (2,1) is North of (2,2)
        self.assertEqual( "E", piece.get_direction_to_neighbouring_grid_cell((3,2)) )  # (3,2) is East of (2,2)
        self.assertEqual( "S", piece.get_direction_to_neighbouring_grid_cell((2,3)) )  # (2,3) is South of (2,2)
        self.assertEqual( "W", piece.get_direction_to_neighbouring_grid_cell((1,2)) )  # (1,2) is West of (2,2)
        self.assertRaises( ValueError, piece.get_direction_to_neighbouring_grid_cell, (8,6) )  # Non-neighbour throws.

if __name__ == '__main__':
    unittest.main()