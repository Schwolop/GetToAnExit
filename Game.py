import pygame
import sys
import random
from pygame.locals import *

import RoadPiece
import AvailablePieces

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

        self.road_filenames = ["straight.png","turnLeft.png","turnRight.png","teeJunction.png"]
        self.roadPieces = pygame.sprite.Group()
        self.objects_to_draw = pygame.sprite.Group()
        self.available_pieces = AvailablePieces.AvailablePieces(self)

    def run_loop(self):
        self.process_events()
        # Game logic goes here...
        if self.mouseIsDown:
            self.roadPieces.add( RoadPiece.RoadPiece(self, self.road_filenames[random.randrange(len(self.road_filenames))], self.currentMousePos) )
            self.mouseIsDown = False
            for road in self.roadPieces.sprites():
                road.move(road.rect.center, 90*random.randrange(4))

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