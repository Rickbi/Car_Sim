import pygame
from pymunk import Space, Vec2d
from math import degrees
from os.path import join

from player import Player
from car import Car, Wheel
from block import Block

class Graphics:
    def __init__(self, space:Space) -> None:
        self.screen = pygame.display.get_surface()
        self.space = space

        self.load()
    
    def load(self):
        self.path_img = join('assets','img')

        path_block = join(self.path_img, 'block.png')
        path_car = join(self.path_img, 'car.png')
        path_wheel = join(self.path_img, 'wheel.png')
        path_player = join(self.path_img, 'player.png')

        self.surf_block = pygame.image.load(path_block).convert_alpha()
        self.surf_car = pygame.image.load(path_car).convert_alpha()
        self.surf_wheel = pygame.image.load(path_wheel).convert_alpha()
        self.surf_player = pygame.image.load(path_player).convert_alpha()

    def draw_player(self, player:Player):
        vel:Vec2d = player.velocity
        ang = vel.angle_degrees + 90
        roto_surf = pygame.transform.rotate(self.surf_player, -ang)
        rect = roto_surf.get_rect(center = player.position)
        self.screen.blit(roto_surf, rect)
    
    def draw_block(self, block:Block):
        roto_surf = pygame.transform.rotate(self.surf_block, degrees(-block.angle))
        rect = roto_surf.get_rect(center=block.position)
        self.screen.blit(roto_surf, rect)
    
    def draw_wheel(self, car:Car):
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
        roto_surf = pygame.transform.rotate(self.surf_car, degrees(-car.angle))
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
    