import pygame
from pygame.locals import *
from time import perf_counter
import pymunk
import pymunk.pygame_util
from os.path import join
import json

from player import Player
from block import Block, Building
from car import Car
from ui import EventHandler
from graphics import Graphics

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
        self.event_handler = EventHandler(self.space)
    
    def load_file(self):
        path = join('assets', 'map', 'map1.json')
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    def load_map(self):
        data = self.load_file()
        
        # Make Player
        pos = data['player'][0]['position']
        self.player = Player(self.space, pos, 10, 0.001)

        # Make all the cars.
        self.cars = []
        for car_data in data['car']:
            pos = car_data['position']
            ang = car_data['angle']
            acc = car_data['acc']
            max_vel = car_data['max_vel']
            color = car_data['color']
            car = Car(self.space, pos, (45,100), 1, acc=acc, max_vel=max_vel, angle=ang, color=color)
            self.cars.append(car)
        
        # Make Boxes.
        self.boxes = []
        for block_data in data['block']:
            pos = block_data['position']
            ang = block_data['angle']
            block = Block(self.space, pos, (30,30), 1, ang)
            self.boxes.append(block)
        
        # Make Buildings.
        self.buildings = []
        for building_data in data['building']:
            pos = building_data['position']
            ang = building_data['angle']
            building = Building(self.space, pos, (100,10), ang)
            self.buildings.append(building)

    def load(self):
        self.graphics = Graphics(self.space)     
        self.load_map()

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
        self.event_handler.event_handler(self.player)
        #self.space.debug_draw(self.draw_options)
        self.graphics.draw_all(self.player.position)
        self.show_fps(self.screen, (10,10))
        self.show_velocity(self.screen, self.player.speed, (10,50))

    def run_game(self):
        run = True
        while run:
            self.screen.fill((20,20,20))
            self.update_screen()
            self.space.step(1/self.fps)
            pygame.display.flip()
            self.clock.tick(self.fps)
            
            if pygame.event.get(QUIT):
                run = False
        
        pygame.quit()
