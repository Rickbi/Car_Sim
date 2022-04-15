import pygame
from pymunk import Space, Vec2d
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

        ver = Car.make_vertices((50,100))
        vertices = []
        for v in ver:
            vertices.append( v + Vec2d(25, 50) )
        self.surf_car = pygame.Surface((50,100))
        self.surf_car.set_colorkey((0,0,0))
        pygame.draw.polygon(self.surf_car, (100,100,100), vertices)
        #self.surf_car.fill((100,100,100))

        self.surf_wheel = pygame.Surface((10,20)).convert_alpha()
        self.surf_wheel.fill((0,0,0))

    def draw_player(self, player:Player):
        color = (255,255,255)
        pygame.draw.circle(self.screen, color, player.position, player.radius)
    
    def draw_block(self, block:Block):
        roto_surf = pygame.transform.rotate(self.surf_block, degrees(-block.angle))
        rect = roto_surf.get_rect(center=block.position)
        self.screen.blit(roto_surf, rect)
    
    def draw_wheel(self, car:Car):
        #resi_surf = pygame.transform.scale(self.surf_car, car.size)
        pos = car.wheel_positions
        roto_surf_front = pygame.transform.rotate(self.surf_wheel, degrees(-car.wheel_angle))
        front_rect_left = roto_surf_front.get_rect(center=car.position + pos[0])
        front_rect_right = roto_surf_front.get_rect(center=car.position + pos[1])
        self.screen.blit(roto_surf_front, front_rect_left)
        self.screen.blit(roto_surf_front, front_rect_right)

        roto_surf_back = pygame.transform.rotate(self.surf_wheel, degrees(-car.angle))
        back_rect_left = roto_surf_back.get_rect(center=car.position + pos[2])
        back_rect_right = roto_surf_back.get_rect(center=car.position + pos[3])
        self.screen.blit(roto_surf_back, back_rect_left)
        self.screen.blit(roto_surf_back, back_rect_right)

    def draw_car(self, car:Car):
        self.draw_wheel(car)
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
    