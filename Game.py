import pygame
import sys
import random
from pygame.locals import *
import collections

import RoadPiece
import AvailablePieces
import BeingDraggedPiece
import BoardPiece
import Board

class Game:
    TIMER_TICK = USEREVENT+1
    GAME_EVENT = USEREVENT+2
    GENERATE_NEW_PIECE = 1
    EXCESS_PIECES_CREATED = 2
    def __init__(self):
        pygame.init()
        self.resolution = (640,480)
        self.fps_clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF)
        self.title = "Get To An Exit!"
        self.desired_frame_rate = 60
        self.currentMousePos = None
        self.mouseIsDown = False
        self.mouseJustWentDown = False
        self.mouseJustWentUp = False
        pygame.display.set_caption(self.title)

        self.spawn_new_piece_time = 500 # Time (ms) before a new piece is spawned.
        self.last_spawn_new_piece_time = pygame.time.get_ticks()

        self.road = collections.namedtuple('road','filename exits')
        self.roads = [
            self.road("straight.png", 'NS'),
            self.road("turnLeft.png", 'SW'),
            self.road("turnRight.png", 'SE'),
            self.road("teeJunction.png", 'SEW'),
            self.road("crossJunction.png", 'NEWS')
        ]
        self.roadPieces = []

        self.objects_to_draw = pygame.sprite.LayeredUpdates()
        self.beingDraggedPiece = None
        self.available_pieces = AvailablePieces.AvailablePieces(self)
        board_ypos = ( int(self.available_pieces.rect.height / RoadPiece.RoadPiece.size)+1 ) * RoadPiece.RoadPiece.size # Ensure is a multiple of 32, and further down than available pieces.
        self.board = Board.Board(self, [ # Bounds of the board are everything but the available pieces area.
            0, # Left
            board_ypos, # Top
            self.resolution[0], # Width
            self.resolution[1]-board_ypos]) # Height

        # Create timer tick.
        pygame.time.set_timer(Game.TIMER_TICK, 10)

    def run_loop(self):
        self.process_events()
        # Game logic goes here...
        if self.mouseJustWentDown:
            (result,pieceToBeDragged) = self.available_pieces.mouse_click_can_start_dragging(self.currentMousePos)
            if result:
                # Create a BeingDraggedPiece that follows the mouse, and takes other parameters from the 'pieceToBeDragged'.
                self.beingDraggedPiece = BeingDraggedPiece.BeingDraggedPiece(
                    self,
                    pieceToBeDragged.filename,
                    self.currentMousePos,
                    pieceToBeDragged.orientation,
                    pieceToBeDragged.exits)
                self.objects_to_draw.add(self.beingDraggedPiece)
        if self.mouseJustWentUp:
            if self.beingDraggedPiece:
                self.beingDraggedPiece.kill()
        if self.mouseIsDown:
            if self.beingDraggedPiece:
                self.beingDraggedPiece.move(self.currentMousePos)

        # Clear all one-iteration flags.
        self.mouseJustWentDown = False
        self.mouseJustWentUp = False

        # Render the scene (This draws the background, updates all objects_to_draw, then draws them all to the screen
        # and flips the display.)
        self.render()

    def process_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
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
                elif event.subtype == Game.EXCESS_PIECES_CREATED:
                    self.end_game(event.subtype)

    def render(self):
        self.screen.fill((0,0,0))
        self.objects_to_draw.update()
        self.objects_to_draw.draw(self.screen)
        pygame.display.flip()
        self.fps_clock.tick(self.desired_frame_rate)

    def do_timer_tick(self):
        if pygame.time.get_ticks() - self.last_spawn_new_piece_time > self.spawn_new_piece_time:
            try:
                pygame.event.post( pygame.event.Event( Game.GAME_EVENT, {'subtype':Game.GENERATE_NEW_PIECE} ) )
            except Exception as e:
                print(e)
            self.last_spawn_new_piece_time = pygame.time.get_ticks()

    def end_game(self,cause):
        # Disable timer tick
        pygame.time.set_timer(Game.TIMER_TICK, 0)

        print("End of game, cause = "+str(cause))