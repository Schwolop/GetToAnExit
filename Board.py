import pygame
import itertools

import BoardPiece
import RoadPiece

class PathOverlay(pygame.sprite.Sprite):
    def __init__(self, the_game, bounds):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game

        self.rect = pygame.Rect( *bounds )
        self.image = pygame.Surface(self.rect.size)
        self.image.set_colorkey((0,0,0)) # Black is transparent.

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self, layer=10) # In front of everything

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
        self.board_list = [] # Also store as a list of grid_cells.

        self.longest_path = []
        self.path_overlay = PathOverlay(the_game,bounds)

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self, layer=1) # Behind everything

    def update(self):
        # Recreate self.image given current content.
        pygame.draw.rect(self.image, (0,255,0), (0,0,self.rect.width,self.rect.height), 2)
        pygame.draw.rect(self.path_overlay.image, (0,0,0), self.path_overlay.rect) # Clear the overlay
        for grid_cell in self.longest_path:                                        # and redraw it from scratch.
            x,y=grid_cell
            x*=RoadPiece.RoadPiece.size
            y*=RoadPiece.RoadPiece.size
            pygame.draw.rect(self.path_overlay.image, (0,0,255), (x, y, RoadPiece.RoadPiece.size, RoadPiece.RoadPiece.size), 6)

    def can_piece_be_placed_here(self, filename, position, orientation, north_oriented_exits):
        grid_cell = self.pixel_position_to_grid_cell(position)
        north_oriented_exit_list = RoadPiece.RoadPiece.exit_string_to_list(north_oriented_exits) # Turn the exit string into a list.
        exit_list = RoadPiece.RoadPiece.rotate_north_oriented_exit_list(north_oriented_exit_list,orientation)
        if not grid_cell:
            return (False, "Position is outside bounds of Board.")

        # Check if placement cell is already occupied
        x,y = grid_cell
        if self.board[x][y]: # If this cell is occupied, return False
            return (False, "Board is already occupied at ("+str(x)+","+str(y)+").")

        # Now check whether this piece can mate with all neighbours.
        # For each neighbour, determine the direction in which it lies from the new piece.
        # If the new piece has an exit in that direction, does the neighbour have the opposite exit to mate?
        # Else, if the new piece has no exit in that direction, do the neighbour also have no exit in the opposite
        # direction?
        neighbours = self.get_neighbouring_pieces_locations(grid_cell)
        if not neighbours or len(neighbours)==0:
            return (True, "No neighbours, thus piece can be placed here.")
        for neighbour in neighbours:
            try:
                common_wall = self.get_common_wall(grid_cell,neighbour)
                if not common_wall:
                    return (False, "No common wall between supposed neighbours!")
                else: # As expected, there is a common wall.
                    # If this grid_cell's piece has an exit in this direction, does the neighbour have an opposing exit?
                    nx,ny = neighbour
                    if not self.board[nx][ny]:
                        return (False, "Supposed neighbour does not actually exist in board's list of pieces.")
                    reversed_neighbour_exits = self.board[nx][ny].reverse_exit_list()
                    if common_wall in exit_list:
                        if common_wall in reversed_neighbour_exits:
                            continue
                        else:
                            return (False, "A neighbouring piece does not have a mating exit with this piece.")
                    else: # common_wall not in exit_list:
                        if common_wall not in reversed_neighbour_exits:
                            continue
                        else:
                            return (False, "A neighbouring piece has an exit where this piece has a wall.")
            except ValueError as e:
                return (False, "Supposed neighbours are disconnected! Error details: " + str(e))
        return (True, "Ok to place piece here.")

    def try_to_add_new_piece(self, filename, position, orientation, north_oriented_exits, return_grid_cell=False):
        retVal, msg = self.can_piece_be_placed_here(filename, position, orientation, north_oriented_exits)
        if retVal:
            grid_cell = self.pixel_position_to_grid_cell(position)
            x,y = grid_cell
            try:
                self.board[x][y] = BoardPiece.BoardPiece(self.the_game, filename, position, orientation, north_oriented_exits, grid_cell)
                self.board_list.append( grid_cell )
                print(msg)
                if return_grid_cell: # Optional argument asks for the grid_cell to also be returned.
                    return (True, grid_cell)
                return True
            except Exception as e:
                print("Could not add board piece at ("+str(x)+",",str(y)+"), error details: "+str(e))
                return False
        else:
            print("Could not add board piece: error details: "+msg)
            return False

    def pixel_position_to_grid_cell(self, position):
        # Returns the grid cell indices of a position, or None if outside Board's bounds
        if( position[0] < self.rect.left or position[0] > self.rect.right
         or position[1] < self.rect.top or position[1] > self.rect.bottom ):
            return None

        return (int((position[0]-self.rect.left) / RoadPiece.RoadPiece.size),
                int((position[1]-self.rect.top) / RoadPiece.RoadPiece.size))

    def get_board_piece(self,grid_cell):
        x,y = grid_cell
        if self.board[x][y]: # If this cell is occupied, return the piece
            return self.board[x][y]
        return None # else return None

    def get_neighbouring_grid_cell_locations(self,grid_cell):
        # Returns the grid_cells in which neighbours *might* exist
        x,y = grid_cell
        xLim,yLim = self.bottom_right_cell()
        neighbours = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)] # Since corners don't mate, don't consider corners as neighbours.
        # Only return neighbours who lie within the board's bounds
        return [c for c in neighbours if c[0] >= 0 and c[0] <= xLim and c[1] >= 0 and c[1] <= yLim]

    def get_neighbouring_pieces_locations(self,grid_cell):
        # Filters the output of get_neighbouring_grid_cell_locations to only those neighbours who actually do exist.
        return [c for c in self.get_neighbouring_grid_cell_locations(grid_cell) if self.board[c[0]][c[1]] is not None]

    def get_connected_pieces_locations(self,grid_cell):
        # Filters the output of get_neighbouring_pieces_locations to only those that have a connected exit with this
        # cell.
        return [c for c in self.get_neighbouring_pieces_locations(grid_cell)
                if self.get_common_wall(grid_cell,c) in self.get_board_piece(grid_cell).exit_list
                and self.get_common_wall(grid_cell,c) in self.get_board_piece(c).reverse_exit_list()]
        # TODO: Work out how to cache the call to self.get_common_wall(grid_cell), and further, work out how to memoize
        # all the other calls.

    def bottom_right_cell(self):
        return (self.num_cells[0]-1, self.num_cells[1]-1)

    def get_common_wall(self,first,second):
        x1,y1 = first
        x2,y2 = second
        if x1==x2 and y1==y2:
            raise ValueError("Pieces lie in the same grid cell!")

        if second not in self.get_neighbouring_grid_cell_locations(first):
            return None

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

    def find_pieces_with_free_exits(self):
        # Returns a list of all grid cell tuples that hold pieces with unconnected exits (i.e. possible finish lines)
        grid_cells_with_free_exits = []
        for grid_cell in self.board_list:
            empty_neighbour_locations = [c for c in self.get_neighbouring_grid_cell_locations(grid_cell) if self.board[c[0]][c[1]] is None]
            for missing_neighbour in empty_neighbour_locations:
                # If the direction of the missing neighbour is an exit direction
                if self.get_board_piece(grid_cell).get_direction_to_neighbouring_grid_cell(missing_neighbour) in self.get_board_piece(grid_cell).exit_list:
                    grid_cells_with_free_exits.append(grid_cell)
                    break
        return grid_cells_with_free_exits

    def has_piece(self,grid_cell):
        # Returns true if grid_cell holds a piece
        return self.board[grid_cell[0]][grid_cell[1]] is not None

    def find_all_paths(self, start, end, path=[]):
        # Returns all acyclic paths between start and end, given the connectivity of the current board treated as a
        # graph.
        path = path + [start]
        if start == end:
            return [path]
        if not self.has_piece(start):
            return []
        paths = []
        for node in self.get_connected_pieces_locations(start):
            if node not in path:
                new_paths = self.find_all_paths(node, end, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    def recalculate_longest_path_between_exits(self):
        # Returns the longest path between pieces with free exits.
        max_length = 0
        longest_path = []
        for first,second in itertools.combinations(self.find_pieces_with_free_exits(),2):
            paths = self.find_all_paths(first,second)
            if len(paths) > 0:
                longest = max(paths, key = lambda path: len(path))
                if len(longest) > max_length:
                    longest_path = longest
                    max_length = len(longest)
        self.longest_path = longest_path

    def recalculate_longest_path_between_any_pieces(self):
        # Returns the longest path between any pieces. (This is likely to be slower than a sensible Floyd-Warshall
        # algorithm or equivalent!)
        max_length = 0
        longest_path = []
        for first,second in itertools.combinations(self.board_list,2):
            paths = self.find_all_paths(first,second)
            if len(paths) > 0:
                longest = max(paths, key = lambda path: len(path))
                if len(longest) > max_length:
                    longest_path = longest
                    max_length = len(longest)
        self.longest_path = longest_path