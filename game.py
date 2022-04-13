import pygame
from pygame.locals import *
from time import perf_counter
import pymunk
import pymunk.pygame_util

from player import Player
from block import Block
from car import Car
from ui import EventHandler

class Game():
    def __init__(self, width, height, fps) -> None:
        self.window_size = width, height
        self.fps = fps
        self.t0 = 0

        self.init_game()
        self.load()

    def init_game(self):
        pygame.init()

        self.screen = pygame.display.set_mode(self.window_size)
        self.clock = pygame.time.Clock()
        font_type = pygame.font.match_font('consolas')
        self.font = pygame.font.Font(font_type, 30)
    
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        #self.space.sleep_time_threshold = 0.5
        #self.space.idle_speed_threshold = 1
    
    def load(self):
        self.event_handler = EventHandler(self.space)
        self.player = Player(self.space, (100,100), 10, 1)
        self.cars = [
            Car(self.space, (100,200), (50,100), 1),
            Car(self.space, (200,200), (25,75), 1)
        ]
        self.boxes = []
        for i in range(10):
            box = Block(self.space, (300,200 + i*35), (30,30), 1)
            self.boxes.append(box)

    def show_fps(self, surface, pos):
        if dt := perf_counter() - self.t0:
            current_fps = round(1/dt)
        else:
            current_fps = -1
        self.t0 = perf_counter()
        text_surf = self.font.render(f'fps = {current_fps}', True, (255,255,255))
        surface.blit(text_surf, pos)
    
    def show_velocity(self, surface, velocity, pos):
        v = round(velocity)
        text_surf = self.font.render(f'v = {v}', True, (255,255,255))
        surface.blit(text_surf, pos)

    def update_screen(self):
        self.show_fps(self.screen, (10,10))
        self.show_velocity(self.screen, self.player.speed, (10,50))
        self.event_handler.event_handler(self.player)
        self.space.debug_draw(self.draw_options)
    
    def run_game(self):
        run = True
        while run:
            self.screen.fill((200,200,200))
            self.space.step(1/self.fps)
            self.update_screen()
            pygame.display.flip()
            self.clock.tick(self.fps)
            
            if pygame.event.get(QUIT):
                run = False
        
        pygame.quit()
