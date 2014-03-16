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


class Test_Board(unittest.TestCase):
    testPieceFilename = os.path.join("tests","test_piece.png")
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
        self.assertTrue(self.board.try_to_add_new_piece(self.testPieceFilename, self.board.rect.topleft, 0, ""))
        self.assertTrue(self.board.try_to_add_new_piece(self.testPieceFilename,
                        (self.board.rect.right-0.0001,self.board.rect.bottom-0.0001), 0, "")) # Absolute bottom-right
                        # is not in bounds, but infinitesimally up-left-wards of it is.

        # Adding a piece over another piece should not work.
        self.assertFalse(self.board.try_to_add_new_piece(self.testPieceFilename, self.board.rect.topleft, 0, ""))

    def test_get_piece_in_grid_cell(self):
        # Getting a non-existant piece returns None.
        self.assertIsNone(self.board.get_board_piece((0,0)))

        # Add and fetch a piece returns the piece.
        self.assertTrue(self.board.try_to_add_new_piece(self.testPieceFilename, self.board.rect.topleft, 0, ""))
        self.assertIsNotNone(self.board.get_board_piece((0,0)))
        self.assertTrue( self.board.get_board_piece((0,0)).filename, self.testPieceFilename ) # Check filename matches.

    def test_get_neighbouring_grid_cell_locations(self):
        # NB: Don't care about order, hence convert all lists to set first.
        self.assertEqual( set(self.board.get_neighbouring_grid_cell_locations((2,2))), set([(3,2),(1,2),(2,1),(2,3)]) ) # All 4
        self.assertEqual( set(self.board.get_neighbouring_grid_cell_locations((0,0))), set([(0,1),(1,0)]) ) # Not N or W.
        xLim,yLim = self.board.bottom_right_cell()
        self.assertEqual( set(self.board.get_neighbouring_grid_cell_locations((xLim,yLim))), set([(xLim-1,yLim),(xLim,yLim-1)]) )
            # Not E or S

    def test_get_common_wall(self):
        self.assertEqual( "E", self.board.get_common_wall( (1,1), (2,1) ) ) # Second should be east of first.
        self.assertEqual( "N", self.board.get_common_wall( (1,1), (1,0) ) ) # Second should be north of first.
        self.assertRaises( ValueError, self.board.get_common_wall, (1,1), (1,1) ) # Same grid cell should throw exception.
        self.assertIsNone(     self.board.get_common_wall( (1,1), (1,3) ) ) # Unconnected grid cells should return none.

    def test_get_neighbouring_pieces_locations(self):
        # NB: Don't care about order, hence convert all lists to set first.

        # With only (2,2) in the board, should return empty list.
        _, n22 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*2), 0, "", return_grid_cell=True)
        self.assertEqual( set(self.board.get_neighbouring_pieces_locations((2,2))), set([]) )

        _, n11 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*1), 0, "", return_grid_cell=True)
        _, n12 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*2), 0, "", return_grid_cell=True)
        _, n13 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*3), 0, "", return_grid_cell=True)
        self.assertEqual( set(self.board.get_neighbouring_pieces_locations((2,2))), set([(1,2)]) )

        _, n21 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*1), 0, "", return_grid_cell=True)
        _, n23 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*3), 0, "", return_grid_cell=True)
        _, n31 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*1), 0, "", return_grid_cell=True)
        _, n32 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*2), 0, "", return_grid_cell=True)
        _, n33 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*3), 0, "", return_grid_cell=True)
        self.assertEqual( set(self.board.get_neighbouring_pieces_locations((2,2))), set([(3,2),(1,2),(2,1),(2,3)]) ) # All 4

    def test_get_connected_pieces_locations(self):
        # NB: Don't care about order, hence convert all lists to set first.

        # With only (2,2) in the board, should return empty list.
        _, n22 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*2), 0, "NS", return_grid_cell=True)
        self.assertEqual( set(self.board.get_connected_pieces_locations((2,2))), set([]) )

        _, n11 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*1), 0, "SE", return_grid_cell=True)
        _, n21 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*1), 0, "ESW", return_grid_cell=True)
        _, n31 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*1), 0, "SW", return_grid_cell=True)
        self.assertEqual( set(self.board.get_connected_pieces_locations((2,2))), set([(2,1)]) ) # Only N

        _, n12 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*2), 0, "NS", return_grid_cell=True)
        _, n13 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*3), 0, "NE", return_grid_cell=True)
        _, n23 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*3), 0, "NEW", return_grid_cell=True)
        _, n32 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*2), 0, "NS", return_grid_cell=True)
        _, n33 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*3), 0, "NW", return_grid_cell=True)
        self.assertEqual( set(self.board.get_connected_pieces_locations((2,2))), set([(2,1),(2,3)]) ) # Only N and S

    def test_find_pieces_with_free_exits(self):
        # Piece in the middle of nowhere with a north exit should be regarded as unclosed.
        _, grid_cell = self.board.try_to_add_new_piece(self.testPieceFilename, (128,128), 0, "N", return_grid_cell=True)
        self.assertIn( grid_cell, self.board.find_pieces_with_free_exits() )

        # Add a piece above it that connects and there should be no free exits any more.
        _, grid_cell = self.board.try_to_add_new_piece(self.testPieceFilename, (128,64), 0, "S", return_grid_cell=True)
        self.assertEqual( [], self.board.find_pieces_with_free_exits() )

    def test_find_all_paths__simple(self):
        _, start = self.board.try_to_add_new_piece(self.testPieceFilename, (128,64), 0, "S", return_grid_cell=True)
        _, mid = self.board.try_to_add_new_piece(self.testPieceFilename, (128,64*2), 0, "NS", return_grid_cell=True)
        _, end = self.board.try_to_add_new_piece(self.testPieceFilename, (128,64*3), 0, "N", return_grid_cell=True)
        self.assertEqual( 1, len(self.board.find_all_paths(start,end,[])) ) # Should only return one path
        self.assertIn( [start,mid,end], self.board.find_all_paths(start,end,[]) ) # And it should be start->mid->end

    def test_find_all_paths__complex(self):
        _, start = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*1), 0, "ESW", return_grid_cell=True)
        _, n2 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*2), 0, "NS", return_grid_cell=True)
        _, end = self.board.try_to_add_new_piece(self.testPieceFilename, (64*2,64*3), 0, "ENW", return_grid_cell=True)
        _, n3 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*1), 0, "WS", return_grid_cell=True)
        _, n4 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*2), 0, "NS", return_grid_cell=True)
        _, n5 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*3,64*3), 0, "WN", return_grid_cell=True)
        _, n6 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*1), 0, "ES", return_grid_cell=True)
        _, n7 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*2), 0, "NS", return_grid_cell=True)
        _, n8 = self.board.try_to_add_new_piece(self.testPieceFilename, (64*1,64*3), 0, "EN", return_grid_cell=True)

        self.assertEqual( 3, len(self.board.find_all_paths(start,end,[])) ) # Should return three paths
        self.assertIn( [start,n2,end], self.board.find_all_paths(start,end,[]) ) # One should be start->mid->end

if __name__ == '__main__':
    unittest.main()