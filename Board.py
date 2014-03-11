import pygame

import BoardPiece
import RoadPiece


class Board(pygame.sprite.Sprite):
    def __init__(self, the_game, bounds):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game

        self.rect = pygame.Rect( *bounds )
        self.image = pygame.Surface(self.rect.size)

        # Calculate size of board, by getting cell for bottom-right co-ordinate.
        self.num_cells = self.pixel_position_to_grid_cell(self.rect.bottomright)
        # Create board as 2d-list, x then y and zero-indexed
        self.board = [[None for y in range(self.num_cells[1])] for x in range(self.num_cells[0])]

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

    def update(self):
        # Recreate self.image given current content.
        pygame.draw.rect(self.image, (0,255,0), (0,0,self.rect.width,self.rect.height), 2)

    def try_to_add_new_piece(self, filename, position, orientation, exits):
        grid_cell = self.pixel_position_to_grid_cell(position)
        if not grid_cell:
            print("Position is outside bounds of Board.")
            return False

        # Check if placement cell is already occupied
        x,y = grid_cell
        if self.board[x][y]: # If this cell is occupied, return False
            print("Board is already occupied at ("+str(x)+",",str(y)+").")
            return False

        # Now check whether this piece can mate with all neighbours.
        # For each neighbour, determine the direction in which it lies from the new piece.
        # If the new piece has an exit in that direction, does the neighbour have the opposite exit to mate?
        # Else, if the new piece has no exit in that direction, do the neighbour also have no exit in the opposite
        # direction?
        for neighbour in self.get_neighbouring_grid_cells(grid_cell):
            pass

        try:
            self.board[x][y] = BoardPiece.BoardPiece(self.the_game, filename, position, orientation, exits, grid_cell)
            return True
        except Exception as e:
            print("Could not add board piece at ("+str(x)+",",str(y)+"), error details: "+str(e))
            return False

    def pixel_position_to_grid_cell(self, position):
        # Returns the grid cell indices of a position, or None if outside Board's bounds
        if( position[0] < self.rect.left or position[0] > self.rect.right
         or position[1] < self.rect.top or position[1] > self.rect.bottom ):
            return None

        return (int((position[0]-self.rect.left) / RoadPiece.RoadPiece.size),
                int((position[1]-self.rect.top) / RoadPiece.RoadPiece.size))

    def get_piece_in_grid_cell(self,grid_cell):
        x,y = grid_cell
        if self.board[x][y]: # If this cell is occupied, return the piece
            return self.board[x][y]
        return None # else return None

    def get_neighbouring_grid_cells(self,grid_cell):
        x,y = grid_cell
        xLim,yLim = self.bottom_right_cell()
        neighbours = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)] # Since corners don't mate, don't consider corners as neighbours.
        # Only return neighbours who lie within the board's bounds
        return [c for c in neighbours if c[0] >= 0 and c[0] <= xLim and c[1] >= 0 and c[1] <= yLim]

    def bottom_right_cell(self):
        return (self.num_cells[0]-1, self.num_cells[1]-1)

    def get_common_wall(self,first,second):
        if second.grid_cell not in self.get_neighbouring_grid_cells(first.grid_cell):
            return None

        x1,y1 = first.grid_cell
        x2,y2 = second.grid_cell
        if x1==x2 and y1==y2:
            raise ValueError("Pieces lie in the same grid cell!")
        if y1 == y2:
            if x2 > x1:
                return "E" # Second is Eastwards of First.
            if x2 < x1:
                return "W" # Second is Westwards of First.
        if x1 == x2:
            if y2 < y1:
                return "N" # Second is Northwards of First.
            if y2 > y1:
                return "S" # Second is Southwards of First.