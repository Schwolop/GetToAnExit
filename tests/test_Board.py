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


class Test_Board(unittest.TestCase):

    def setUp(self):
        self.the_game = MockGame()
        self.board = self.the_game.board

    def test_pixel_position_to_grid_cell(self):
        # Cell bounds are the half-interval [0,cellSize) in each dimension.
        self.assertEqual( (0,0), self.board.pixel_position_to_grid_cell((0,0)) )
        self.assertEqual( (0,0), self.board.pixel_position_to_grid_cell((1,1)) )
        self.assertEqual( (0,0), self.board.pixel_position_to_grid_cell((RoadPiece.RoadPiece.size-1,RoadPiece.RoadPiece.size-1)) )
        self.assertEqual( (0,0), self.board.pixel_position_to_grid_cell((RoadPiece.RoadPiece.size-1+0.9999,RoadPiece.RoadPiece.size-1+0.9999)) )
        self.assertEqual( (0,0), self.board.pixel_position_to_grid_cell((RoadPiece.RoadPiece.size-0.0001,RoadPiece.RoadPiece.size-0.0001)) )
        self.assertEqual( (1,1), self.board.pixel_position_to_grid_cell((RoadPiece.RoadPiece.size,RoadPiece.RoadPiece.size)) )

    def test_try_to_add_new_piece(self):
        # Adding pieces in each corner should work.
        self.assertTrue(self.board.try_to_add_new_piece(os.path.join("tests","test_piece.png"), self.board.rect.topleft, 0, ""))
        self.assertTrue(self.board.try_to_add_new_piece(os.path.join("tests","test_piece.png"),
                        (self.board.rect.right-0.0001,self.board.rect.bottom-0.0001), 0, "")) # Absolute bottom-right
                        # is not in bounds, but infinitesimally up-left-wards of it is.

        # Adding a piece over another piece should not work.
        self.assertFalse(self.board.try_to_add_new_piece(os.path.join("tests","test_piece.png"), self.board.rect.topleft, 0, ""))

    def test_get_piece_in_grid_cell(self):
        # Getting a non-existant piece returns None.
        self.assertIsNone(self.board.get_piece_in_grid_cell((0,0)))

        # Add and fetch a piece returns the piece.
        self.assertTrue(self.board.try_to_add_new_piece(os.path.join("tests","test_piece.png"), self.board.rect.topleft, 0, ""))
        self.assertIsNotNone(self.board.get_piece_in_grid_cell((0,0)))
        self.assertTrue( self.board.get_piece_in_grid_cell((0,0)).filename, os.path.join("tests","test_piece.png") ) # Check filename matches.

    def test_get_neighbouring_grid_cells(self):
        # NB: Don't care about order, hence convert all lists to set first.
        self.assertEqual( set(self.board.get_neighbouring_grid_cells((2,2))), set([(3,2),(1,2),(2,1),(2,3)]) ) # All 4
        self.assertEqual( set(self.board.get_neighbouring_grid_cells((0,0))), set([(0,1),(1,0)]) ) # Not N or W.
        xLim,yLim = self.board.bottom_right_cell()
        self.assertEqual( set(self.board.get_neighbouring_grid_cells((xLim,yLim))), set([(xLim-1,yLim),(xLim,yLim-1)]) )
            # Not E or S

if __name__ == '__main__':
    unittest.main()