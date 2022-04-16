import pygame
from pygame.locals import *
from pymunk import Vec2d, Space, ShapeFilter

from player import Player
from car import Car

class EventHandler():
    def __init__(self, space:Space) -> None:
        self.space = space
        self.limit_speed_brake = 100

    def player_event_handler_release_key(self, player:Player):
        for event in pygame.event.get(KEYUP):
            if event.key == K_f:
                pos = player.position
                radius = player.radius*3
                mask = ShapeFilter(mask=0b100)
                point = self.space.point_query_nearest(pos, radius, mask)
                if point:
                    player.add_car(point.shape)
                    point.shape.add_player(player)
                    point.shape.quit_brake()
                    player.remove_from_space()

    def player_event_handler_hold_key(self, player:Player):
        direction = Vec2d(0,0)
        keys = pygame.key.get_pressed()
                
        if keys[K_UP] or keys[K_w]:
            direction += Vec2d(0,-1)
        if keys[K_DOWN] or keys[K_s]:
            direction += Vec2d(0,1)
        if keys[K_LEFT] or keys[K_a]:
            direction += Vec2d(-1,0)
        if keys[K_RIGHT] or keys[K_d]:
            direction += Vec2d(1,0)
        
        player.accelerate(direction)

    def player_event_handler(self, player:Player):
        self.player_event_handler_release_key(player)
        self.player_event_handler_hold_key(player)

    def car_event_handler_release_key(self, car:Car):
        for event in pygame.event.get(KEYUP):
            if event.key == K_f:
                player = car.get_player()
                pos = car.get_door_pos()
                vel = car.velocity
                player.add_to_space(self.space, pos, vel)
                if car.speed < self.limit_speed_brake:
                    car.add_brake()
                #player.turn(car.angle)
                car.add_player(None)
                player.add_car(None)

    def car_event_handler_hold_key(self, car:Car):
        keys = pygame.key.get_pressed()
                
        if keys[K_UP] or keys[K_w]:
            car.accelerate()
        if keys[K_DOWN] or keys[K_s]:
            car.back()
        
        if keys[K_LEFT] or keys[K_a]:
            car.turn(-1)
        if keys[K_RIGHT] or keys[K_d]:
            car.turn(1)

        if keys[K_SPACE]:
            car.brake()
        
    def car_event_handler(self, car:Car):
        self.car_event_handler_release_key(car)
        self.car_event_handler_hold_key(car)

    def event_handler(self, player:Player):
        car = player.get_car()
        if car:
            self.car_event_handler(car)
        else:
            self.player_event_handler(player)
