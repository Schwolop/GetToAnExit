import pygame
import sys
import random
from pygame.locals import *
import collections

import RoadPiece
import AvailablePieces
import Board

class Game:
    def __init__(self):
        pygame.init()
        self.resolution = (640,480)
        self.fps_clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.resolution, pygame.DOUBLEBUF)
        self.title = "Get To An Exit!"
        self.desired_frame_rate = 60
        self.currentMousePos = None
        self.mouseIsDown = False
        pygame.display.set_caption(self.title)

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
        self.available_pieces = AvailablePieces.AvailablePieces(self)
        board_ypos = ( int(self.available_pieces.rect.height / RoadPiece.RoadPiece.size)+1 ) * RoadPiece.RoadPiece.size # Ensure is a multiple of 32, and further down than available pieces.
        self.board = Board.Board(self, [ # Bounds of the board are everything but the available pieces area.
            0, # Left
            board_ypos, # Top
            self.resolution[0], # Width
            self.resolution[1]-board_ypos]) # Height

    def run_loop(self):
        self.process_events()
        # Game logic goes here...
        if self.mouseIsDown:
            randIndex = random.randrange(len(self.roads))
            try:
                self.roadPieces.append( RoadPiece.RoadPiece(self, self.roads[randIndex].filename, self.currentMousePos, 30, self.roads[randIndex].exits) )
            except ValueError as e:
                print(e)
            self.mouseIsDown = False
            for road in self.roadPieces:
                road.move(road.rect.center, random.choice('NEWS'))

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

    def render(self):
        self.screen.fill((0,0,0))
        self.objects_to_draw.update()
        self.objects_to_draw.draw(self.screen)
        pygame.display.flip()
        self.fps_clock.tick(self.desired_frame_rate)