import pygame
from pymunk import Space
from math import degrees

from player import Player
from car import Car, Wheel
from block import Block

class Graphics:
    def __init__(self, space:Space, block_size) -> None:
        self.screen = pygame.display.get_surface()
        self.space = space
        self.block_size = block_size

        self.load()
    
    def load(self):
        self.surf_block = pygame.Surface(self.block_size).convert_alpha()
        self.surf_block.fill((255,255,0))

        self.surf_car = pygame.Surface((50,100)).convert_alpha()
        self.surf_car.fill((100,100,100))

    def draw_player(self, player:Player):
        color = (255,255,255)
        pygame.draw.circle(self.screen, color, player.position, player.radius)
    
    def draw_block(self, block:Block):
        roto_surf = pygame.transform.rotate(self.surf_block, degrees(-block.angle))
        rect = roto_surf.get_rect(center=block.position)
        self.screen.blit(roto_surf, rect)
    
    def draw_car(self, car:Car):
        resi_surf = pygame.transform.scale(self.surf_car, car.size)
        roto_surf = pygame.transform.rotate(resi_surf, degrees(-car.angle))
        rect = roto_surf.get_rect(center=car.position)
        self.screen.blit(roto_surf, rect)

    def draw_bb(self, shape, color):
        y = shape.bb.bottom
        x = shape.bb.left
        w = shape.bb.right - shape.bb.left
        h = shape.bb.top - shape.bb.bottom
        pygame.draw.rect(self.screen, color, (x,y,w,h), 2)
    
    def draw_all(self):
        for shape in self.space.shapes:
            if type(shape) == Player:
                self.draw_player(shape)
            elif type(shape) == Car:
                self.draw_car(shape)
            elif type(shape) == Block:
                self.draw_block(shape)
    