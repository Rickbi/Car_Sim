import pygame
from pymunk import Space, Vec2d
from math import degrees
from os.path import join

from player import Player
from car import Car, Wheel
from block import Block, Building

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
        path_building = join(self.path_img, 'building.png')
        path_bg = join(self.path_img, 'bg.png')

        self.surf_block = pygame.image.load(path_block).convert_alpha()
        self.surf_car = pygame.image.load(path_car).convert_alpha()
        self.surf_wheel = pygame.image.load(path_wheel).convert_alpha()
        self.surf_player = pygame.image.load(path_player).convert_alpha()
        self.surf_building = pygame.image.load(path_building).convert_alpha()
        self.surf_bg = pygame.image.load(path_bg).convert_alpha()

    def draw_player(self, player:Player, offset:Vec2d):
        vel:Vec2d = player.velocity
        ang = vel.angle_degrees + 90
        roto_surf = pygame.transform.rotate(self.surf_player, -ang)
        rect = roto_surf.get_rect(center = player.position)
        rect.move_ip(offset)
        self.screen.blit(roto_surf, rect)
    
    def draw_block(self, block:Block, offset:Vec2d):
        roto_surf = pygame.transform.rotate(self.surf_block, degrees(-block.angle))
        rect = roto_surf.get_rect(center=block.position)
        rect.move_ip(offset)
        self.screen.blit(roto_surf, rect)
    
    def draw_building(self, building:Building, offset:Vec2d):
        scale_surf = pygame.transform.scale(self.surf_building, building.size)
        roto_surf = pygame.transform.rotate(scale_surf, degrees(-building.angle))
        rect = roto_surf.get_rect(center=building.position)
        rect.move_ip(offset)
        self.screen.blit(roto_surf, rect)
    
    def draw_wheel(self, car:Car, offset:Vec2d):
        pos = car.wheel_positions
        roto_surf_front = pygame.transform.rotate(self.surf_wheel, degrees(-car.wheel_angle))
        front_rect_left = roto_surf_front.get_rect(center=car.position + pos[0])
        front_rect_right = roto_surf_front.get_rect(center=car.position + pos[1])
        front_rect_left.move_ip(offset)
        front_rect_right.move_ip(offset)
        self.screen.blit(roto_surf_front, front_rect_left)
        self.screen.blit(roto_surf_front, front_rect_right)

        roto_surf_back = pygame.transform.rotate(self.surf_wheel, degrees(-car.angle))
        back_rect_left = roto_surf_back.get_rect(center=car.position + pos[2])
        back_rect_right = roto_surf_back.get_rect(center=car.position + pos[3])
        back_rect_left.move_ip(offset)
        back_rect_right.move_ip(offset)
        self.screen.blit(roto_surf_back, back_rect_left)
        self.screen.blit(roto_surf_back, back_rect_right)

    def draw_wheel_rift(self, car:Car, offset:Vec2d):
        pos = car.wheel_positions
        roto_surf_front = pygame.transform.rotate(self.surf_wheel, degrees(-car.wheel_angle))
        front_rect_left = roto_surf_front.get_rect(center=car.position + pos[0])
        front_rect_right = roto_surf_front.get_rect(center=car.position + pos[1])
        self.surf_bg.blit(roto_surf_front, front_rect_left)
        self.surf_bg.blit(roto_surf_front, front_rect_right)

        roto_surf_back = pygame.transform.rotate(self.surf_wheel, degrees(-car.angle))
        back_rect_left = roto_surf_back.get_rect(center=car.position + pos[2])
        back_rect_right = roto_surf_back.get_rect(center=car.position + pos[3])
        self.surf_bg.blit(roto_surf_back, back_rect_left)
        self.surf_bg.blit(roto_surf_back, back_rect_right)

    def draw_car(self, car:Car, offset:Vec2d):
        # if car.speed > 290:
        #     self.draw_wheel_rift(car, offset)
        # else:
        #     self.draw_wheel(car, offset)
        self.draw_wheel(car, offset)
        roto_surf = pygame.transform.rotate(self.surf_car, degrees(-car.angle))
        rect = roto_surf.get_rect(center=car.position)
        rect.move_ip(offset)
        self.screen.blit(roto_surf, rect)
    
    def draw_all(self, center:Vec2d):
        offset = 0.5*Vec2d(*self.screen.get_size()) - center

        self.screen.blit(self.surf_bg, offset)
        for shape in self.space.shapes:
            if type(shape) == Player:
                self.draw_player(shape, offset)
            elif type(shape) == Car:
                self.draw_car(shape, offset)
            elif type(shape) == Block:
                self.draw_block(shape, offset)
            elif type(shape) == Building:
                self.draw_building(shape, offset)
    