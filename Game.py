import pygame
import sys
from pygame.locals import *
import collections
import os
import threading

import RoadPiece
import AvailablePieces
import BeingDraggedPiece
import Board


class Game:
    # Event types
    TIMER_TICK = USEREVENT+1
    GAME_EVENT = USEREVENT+2

    # Game event sub-types
    GENERATE_NEW_PIECE = 1
    EXCESS_PIECES_CREATED = 2
    FAILED_TO_RETURN_PIECE = 3
    FINAL_COUNTDOWN_ELAPSED = 4

    # Game states
    INTRODUCTION = 1
    MAIN_GAMEPLAY = 2
    FINAL_COUNTDOWN = 3
    SCORE_DISPLAY = 4

    def __init__(self):
        pygame.init()
        self.resolution = (1280,960)
        self.fps_clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF)
        self.title = "Get To An Exit!"
        self.desired_frame_rate = 60
        self.currentMousePos = None
        self.mouseIsDown = False
        self.mouseJustWentDown = False
        self.mouseJustWentUp = False
        pygame.display.set_caption(self.title)

        self.timer_tick_period = 10
        self.spawn_new_piece_time = 2000 # Time (ms) before a new piece is spawned.
        self.last_spawn_new_piece_time = pygame.time.get_ticks()
        self.final_countdown_time = 10000 # Time (ms) allowed at end of game to place final pieces.
        self.score_display_start_time = pygame.time.get_ticks()

        self.longest_path_calculator = None # A future that calculates the longest path asynchronously.
        self.longest_path_calculator_needs_to_run = False

        self.road = collections.namedtuple('road','filename exits')
        self.roads = [
            self.road(os.path.join("resources","straight.png"), 'NS'),
            self.road(os.path.join("resources","turnLeft.png"), 'SW'),
            self.road(os.path.join("resources","turnRight.png"), 'SE'),
            self.road(os.path.join("resources","teeJunction.png"), 'SEW'),
            self.road(os.path.join("resources","crossJunction.png"), 'NEWS'),
            self.road(os.path.join("resources","culDeSac.png"), 'S')
        ]

        self.restart()
        self.game_state = Game.INTRODUCTION
        self.intro_overlay.show()

        # Create timer tick.
        pygame.time.set_timer(Game.TIMER_TICK, self.timer_tick_period)

    def run_loop(self):
        self.process_events()
        # Game logic goes here...
        if self.game_state == Game.MAIN_GAMEPLAY or self.game_state == Game.FINAL_COUNTDOWN:
            if self.mouseJustWentDown:
                (result,pieceToBeDragged,index) = self.available_pieces.mouse_click_can_start_dragging(self.currentMousePos)
                if result:
                    # Create a BeingDraggedPiece that follows the mouse, and takes other parameters from the 'pieceToBeDragged'.
                    self.beingDraggedIndex = index
                    self.beingDraggedPiece = BeingDraggedPiece.BeingDraggedPiece(
                        self,
                        pieceToBeDragged.filename,
                        self.currentMousePos,
                        pieceToBeDragged.orientation,
                        pieceToBeDragged.north_oriented_exits)
                    self.objects_to_draw.add(self.beingDraggedPiece)
            if self.mouseJustWentUp:
                if self.beingDraggedPiece:
                    retval = self.board.try_to_add_new_piece( self.beingDraggedPiece.filename,self.currentMousePos,self.beingDraggedPiece.orientation,self.beingDraggedPiece.north_oriented_exits )
                    self.beingDraggedPiece.kill()
                    if retval:
                        print("Piece added successfully.")
                        self.longest_path_calculator_needs_to_run = True
                    else:
                        print("Piece could not be added here. Attempting to return it to the available pieces.")
                        self.available_pieces.try_to_return_piece( self.beingDraggedPiece, self.beingDraggedIndex )
                    # Finally, destroy the Game's cache of the dragged piece and its index.
                    self.beingDraggedPiece = None
                    self.beingDraggedIndex = -1
            if self.mouseIsDown:
                if self.beingDraggedPiece:
                    self.beingDraggedPiece.move(self.currentMousePos)
        elif self.game_state == Game.SCORE_DISPLAY and pygame.time.get_ticks() - self.score_display_start_time > 2000: # Ensure user sees score screen for at least 2 seconds.
            if self.mouseJustWentDown:
                self.game_state = Game.INTRODUCTION
                self.score_overlay.hide()
                self.intro_overlay.show()
        elif self.game_state == Game.INTRODUCTION:
            if self.mouseJustWentDown:
                self.game_state = Game.MAIN_GAMEPLAY
                self.restart()

        # If thread isn't running to calculate path, and a piece was added since last run, spawn it and start.
        if not self.longest_path_calculator and self.longest_path_calculator_needs_to_run:
            self.longest_path_calculator_needs_to_run = False
            self.longest_path_calculator = threading.Thread(target=self.board.recalculate_longest_path_between_exits_or_dead_ends)
            self.longest_path_calculator.start()

        # If path calculator was running but now has finished, join and delete it.
        if self.longest_path_calculator and not self.longest_path_calculator.is_alive():
            self.longest_path_calculator.join()
            del(self.longest_path_calculator)
            self.longest_path_calculator = None

        # Clear all one-iteration flags.
        self.mouseJustWentDown = False
        self.mouseJustWentUp = False

        # Render the scene (This draws the background, updates all objects_to_draw, then draws them all to the screen
        # and flips the display.)
        self.render()

    def restart(self):
        # Recreate state objects.
        self.objects_to_draw = pygame.sprite.LayeredUpdates()
        self.beingDraggedPiece = None
        self.beingDraggedIndex = -1
        self.available_pieces = AvailablePieces.AvailablePieces(self)
        board_ypos = ( int(self.available_pieces.rect.height / RoadPiece.RoadPiece.size)+1 ) * RoadPiece.RoadPiece.size # Ensure is a multiple of 32, and further down than available pieces.
        self.board = Board.Board(self, [ # Bounds of the board are everything but the available pieces area.
            0, # Left
            board_ypos, # Top
            self.resolution[0], # Width
            self.resolution[1]-board_ypos]) # Height
        self.score_overlay = ScoreOverlay(self,[self.resolution[0]/5,self.resolution[1]/3,self.resolution[0]*3/5,self.resolution[1]/3])
        self.intro_overlay = IntroOverlay(self,[100,self.resolution[1]/4,self.resolution[0]-200,self.resolution[1]/2])
        self.intro_overlay.hide()
        self.score_overlay.hide()
        self.last_spawn_new_piece_time = pygame.time.get_ticks()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.time.set_timer(Game.TIMER_TICK, 0) # Disable timer tick
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                self.currentMousePos = event.pos
            elif event.type == MOUSEBUTTONDOWN:
                self.mouseIsDown = True
                self.mouseJustWentDown = True
            elif event.type == MOUSEBUTTONUP:
                self.mouseIsDown = False
                self.mouseJustWentUp = True
            elif event.type == Game.TIMER_TICK:
                self.do_timer_tick()
            elif event.type == Game.GAME_EVENT:
                if event.subtype == Game.GENERATE_NEW_PIECE:
                    self.available_pieces.try_generate_new_piece()
                elif event.subtype == Game.EXCESS_PIECES_CREATED or event.subtype == Game.FAILED_TO_RETURN_PIECE:
                    self.game_state = Game.FINAL_COUNTDOWN
                    self.available_pieces.adjust_progress_bar( self.final_countdown_time / self.timer_tick_period, self.final_countdown_time / self.timer_tick_period, (255,0,0) ) # Reset progress bar increments and position.
                elif event.subtype == Game.FINAL_COUNTDOWN_ELAPSED:
                    self.game_state = Game.SCORE_DISPLAY
                    # If path calculator is still running block until joined then delete it.
                    if self.longest_path_calculator and self.longest_path_calculator.is_alive():
                        print( "waiting for path calculator...")
                        self.score_overlay.show_waiting_for_path_calculator()
                        while self.longest_path_calculator_needs_to_run or (self.longest_path_calculator and self.longest_path_calculator.is_alive()):
                            self.render()
                            pygame.time.wait(10) # Wait 10ms and look again.
                        print("done")
                        del(self.longest_path_calculator)
                        self.longest_path_calculator = None
                    self.score_overlay.set_score(
                        len(self.board.longest_path),                               # length of longest path
                        len(self.board.find_pieces_with_free_exits()),              # open exits
                        len(self.board.board_list)-len(self.board.longest_path) )   # num pieces not on path (wasted)
                    self.score_display_start_time = pygame.time.get_ticks()
                    print("Score display")

    def render(self):
        self.screen.fill((0,0,0))
        self.objects_to_draw.update()
        self.objects_to_draw.draw(self.screen)
        pygame.display.flip()
        self.fps_clock.tick(self.desired_frame_rate)

    def do_timer_tick(self):
        # On every tick, if in state X...
        if self.game_state == Game.MAIN_GAMEPLAY:
            self.available_pieces.add_to_progess_bar(1)
        elif self.game_state == Game.FINAL_COUNTDOWN:
            self.available_pieces.add_to_progess_bar(-1)
            if self.available_pieces.progress_count_towards_new_piece == 0: # If it's decremented to zero again, time's up, go to scoring phase.
                try:
                    pygame.event.post( pygame.event.Event( Game.GAME_EVENT, {'subtype':Game.FINAL_COUNTDOWN_ELAPSED} ) )
                except Exception as e:
                    print(e)
                self.game_state = Game.SCORE_DISPLAY
        # If in state X and Y seconds since the last specific event...
        if self.game_state == Game.MAIN_GAMEPLAY and \
                                pygame.time.get_ticks() - self.last_spawn_new_piece_time > self.spawn_new_piece_time:
            try:
                pygame.event.post( pygame.event.Event( Game.GAME_EVENT, {'subtype':Game.GENERATE_NEW_PIECE} ) )
            except Exception as e:
                print(e)
            self.last_spawn_new_piece_time = pygame.time.get_ticks()

    def end_game(self,cause):
        print("End of game, cause = "+str(cause))

class ScoreOverlay(pygame.sprite.Sprite):
    def __init__(self, the_game, bounds):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game

        # Sprite atributes
        self.rect = pygame.Rect( *bounds )
        self.image = pygame.Surface(self.rect.size)
        self.image.set_colorkey((0,0,0)) # Black is transparent.

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self, layer=10) # In front of everything

        self.is_shown = False
        if 'verdana' in pygame.font.get_fonts():
            self.font = pygame.font.SysFont('verdana',32)
        else:
            self.font = pygame.font.Font(None,32) # Otherwise use default.
        self.score_text = ["","","","",""] # five lines.

    def show(self):
        self.is_shown = True

    def hide(self):
        self.is_shown = False

    def show_waiting_for_path_calculator(self):
        self.score_text[0] = ""
        self.score_text[1] = "Waiting for"
        self.score_text[2] = "path planner..."
        self.score_text[3] = ""
        self.score_text[4] = "(You must have done well!)"
        self.is_shown = True

    def set_score(self, longest_path_length, num_pieces_with_open_exits, num_wasted_pieces):
        wastage = 0 if num_wasted_pieces+longest_path_length == 0 else num_wasted_pieces/(num_wasted_pieces+longest_path_length) # Prevent divide by zero.
        total_score = (longest_path_length*10) * (1-wastage) - 20*num_pieces_with_open_exits
        self.score_text[0] = "Path Length of " + str(longest_path_length) + " = " + str(longest_path_length*10)
        self.score_text[1] = "Wastage of {:.1%}".format(wastage) + " = " + str(round( (longest_path_length*10) * -wastage ))
        self.score_text[2] = str(num_pieces_with_open_exits) + " Unclosed Exit" + ("" if num_pieces_with_open_exits==1 else "s") + " = " + str(-20*num_pieces_with_open_exits)
        self.score_text[3] = ""
        self.score_text[4] = "Total Score = " + str(round(total_score))
        self.is_shown = True

    def update(self):
        # Recreate self.image given current content.
        self.image.set_colorkey((0,0,0)) # Black is transparent.
        pygame.draw.rect(self.image, (0,0,0), self.rect) # Clear the overlay
        if self.is_shown: # and redraw it only if the overlay is supposed to be shown.
            self.image.set_colorkey(None) # Remove transparency
            pygame.draw.rect(self.image, (0,0,0), (0,0,self.rect.width,self.rect.height) )
            pygame.draw.rect(self.image, (255,255,255), (0,0,self.rect.width,self.rect.height), 2 )
            spacing = 2
            initial_height = self.rect.height/2 - 3*32 - 5/2*spacing
            for i in range(len(self.score_text)):
                text_size = self.font.size(self.score_text[i])
                text = self.font.render(self.score_text[i], True, (255,255,255))
                self.image.blit(text, (self.rect.width/2-(text_size[0]/2), initial_height+i*32+i*spacing) )

class IntroOverlay(pygame.sprite.Sprite):
    def __init__(self, the_game, bounds):
        pygame.sprite.Sprite.__init__(self)  # Call the parent class (Sprite) constructor
        self.the_game = the_game

        # Sprite atributes
        self.rect = pygame.Rect( *bounds )
        self.image = pygame.Surface(self.rect.size)
        self.image.set_colorkey((0,0,0)) # Black is transparent.

        # Add this object to the objects to draw
        self.the_game.objects_to_draw.add(self, layer=11) # In front of everything

        self.is_shown = False
        if 'verdana' in pygame.font.get_fonts():
            self.font = pygame.font.SysFont('verdana',24)
        else:
            self.font = pygame.font.Font(None,24) # Otherwise use default.

        self.intro_text = ["",
                           "--------------------",
                           "The Longest Road",
                           "--------------------",
                           "",
                           "Drag pieces from the stack at the top, to the board below.",
                           "You earn points for the length of your longest non-looping road,",
                           "but lose them for leaving intersections open, and for tiles that",
                           "aren't part of this longest road.",
                           "",
                           "Pieces that can't be placed properly go back into the stack. (This",
                           "includes the area next to the stack itself, and can be very useful!)",
                           "But when the stack overflows - that's it! - and you have just",
                           "10 seconds to get your road in order with whatever is left.",
                           "",
                           "Click anywhere to start!"]

    def show(self):
        self.is_shown = True

    def hide(self):
        self.is_shown = False

    def update(self):
        # Recreate self.image given current content.
        self.image.set_colorkey((0,0,0)) # Black is transparent.
        pygame.draw.rect(self.image, (0,0,0), self.rect) # Clear the overlay
        if self.is_shown: # and redraw it only if the overlay is supposed to be shown.
            self.image.set_colorkey(None) # Remove transparency
            pygame.draw.rect(self.image, (0,0,0), (0,0,self.rect.width,self.rect.height) )
            pygame.draw.rect(self.image, (255,255,255), (0,0,self.rect.width,self.rect.height), 2 )
            spacing = 2
            initial_height = 2*spacing
            for i, words in enumerate(self.intro_text):
                text_size = self.font.size(words)
                text = self.font.render(words, True, (255,255,255))
                self.image.blit(text, (self.rect.width/2-(text_size[0]/2), initial_height+i*(24+spacing)) )