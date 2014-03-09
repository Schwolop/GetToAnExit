import pygame
import random

import Game
import RoadPiece
import AvailablePiece


class AvailablePieces(pygame.sprite.Sprite):
    def __init__(self,the_game):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game
        self.maximum_pieces = 10
        self.border = 4
        self.spacing = 2
        self.center = ( int(self.the_game.resolution[0]/2), int(0 + self.border + RoadPiece.RoadPiece.size/2) )
        self.top_left = ( int(self.center[0] - (RoadPiece.RoadPiece.size * self.maximum_pieces/2) - self.spacing/2 - ((self.maximum_pieces/2-1) * self.spacing)), self.border)
        self.progress_bar_height = 10
        self.progress_count_towards_new_piece = 0
        self.progress_bar_increments = self.the_game.spawn_new_piece_time / self.the_game.timer_tick_period

        # Sprite atributes
        self.rect = pygame.Rect( *self.calculate_rect_bounds() )
        self.image = pygame.Surface(self.rect.size)

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self)

        self.pieces = []

    def update(self):
        # Recreate self.image and self.rect given current content.
        self.rect = pygame.Rect( *self.calculate_rect_bounds() )
        pygame.draw.rect(self.image, (255,0,0), (0,0,self.rect.width,self.rect.height - self.progress_bar_height), 1)

        # Draw progress bar (left in blue, right in black)
        pygame.draw.rect(self.image, (0,0,255) if len(self.pieces)<self.maximum_pieces else (255,0,0), (0,self.rect.height - self.progress_bar_height,self.rect.width*(self.progress_count_towards_new_piece/self.progress_bar_increments),self.progress_bar_height), 0)
        pygame.draw.rect(self.image, (0,0,0), (self.rect.width*(self.progress_count_towards_new_piece/self.progress_bar_increments),self.rect.height - self.progress_bar_height,self.rect.width*(1.0-(self.progress_count_towards_new_piece/self.progress_bar_increments)),self.progress_bar_height), 0)

    def calculate_rect_bounds(self):
        return [ self.top_left[0] - self.spacing,
                 self.top_left[1] - self.spacing,
                 (self.center[0]-self.top_left[0])*2 + self.spacing*2,
                 (self.center[1]-self.top_left[1])*2 + self.spacing*2 + self.progress_bar_height]

    def try_generate_new_piece(self):
        num_pieces = len(self.pieces)
        if num_pieces >= self.maximum_pieces:
            print("excess pieces created")
            pygame.event.post( pygame.event.Event( Game.Game.GAME_EVENT, {'subtype':Game.Game.EXCESS_PIECES_CREATED} ) )
        else:
            print("creating available piece #"+str(num_pieces+1))
            randIndex = random.randrange(len(self.the_game.roads))
            self.pieces.append(
                AvailablePiece.AvailablePiece(
                    self.the_game,
                    self.the_game.roads[randIndex].filename,
                    (   self.top_left[0] + (AvailablePiece.AvailablePiece.size * (num_pieces+0.5)) + (self.spacing * num_pieces),
                        self.center[1] ),
                    0,
                    self.the_game.roads[randIndex].exits) )
            self.progress_count_towards_new_piece = 0

    def mouse_click_can_start_dragging(self,position):
        # Returns True if a mouse position is over an available piece.

        # If click is outside the available pieces area entirely, return False. (Quicker than next loop's failure mode.)
        if not self.rect.collidepoint( position ):
            return (False, None)

        for index, piece in enumerate(self.pieces):
            if piece.rect.collidepoint( position ):
                self.remove_piece_and_bubble_down_remaining(index,piece)
                return (True, piece)
        return (False,None)

    def remove_piece_and_bubble_down_remaining(self,index,piece):
        for i in range(index+1,len(self.pieces)):
            self.pieces[i].rect[0] -= (AvailablePiece.AvailablePiece.size + self.spacing) # Shift each other piece leftwards by one piece width and one spacing interval.
        self.pieces.remove(piece) # Finally, remove the dragged piece from the list entirely.
        piece.kill() # and kill its sprite.

    def increment_progess_bar(self,amount):
        self.progress_count_towards_new_piece += amount