import pygame
from pygame.locals import *
import pymunk
from pymunk import Vec2d
from block import Block
from math import cos, sin

from player import Player

class Wheel(Block):
    def __init__(self, space, pos, size, density) -> None:
        super().__init__(space, pos, size, density)

        self.color = pygame.Color(100,100,100)
        self.collision_type = 2
        self.acc = 1000
        self.max_vel = 90
        self.max_angle = 0.51

        def vel_condition(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, 0.99, dt)
            #nx = Vec2d( cos(body.angle), sin(body.angle) )
            ny = Vec2d( -sin(body.angle), cos(body.angle) )
            #vx = nx*body.velocity.dot(nx)
            vy = ny*body.velocity.dot(ny)
            body.velocity = vy
                
        self.body.velocity_func = vel_condition
        self.filter = pymunk.ShapeFilter(categories=0b10, mask=0)

    def accelerate(self, acc):
        force = acc*self.mass
        self.body.apply_force_at_local_point( (0,force), (0,0))
    
    def turn(self, ang):
        self.body.angle = ang
    
    def add_to_angle(self, ang, ref):
        self.body.angle += ang
        da = ref - self.body.angle
        if da < -self.max_angle:
            self.body.angle = ref + self.max_angle
        elif da > self.max_angle:
            self.body.angle = ref - self.max_angle
    
    def rest_mode(self, ref):
        da = ref - self.body.angle
        if da > 0:
            self.add_to_angle(0.05, ref)
        elif da < 0:
            self.add_to_angle(-0.05, ref)

    def stop(self):
        nw = Vec2d(-sin(self.body.angle), cos(self.body.angle))
        direction = self.body.velocity.dot(nw)
        if direction > 0:
            self.accelerate(-self.acc)
        elif direction < 0:
            self.accelerate(self.acc)


class Car(Block):
    def __init__(self, space:pymunk.Space, pos, size, density) -> None:
        super().__init__(space, pos, size, density)
        
        self.color = pygame.Color(0,0,250)

        self.collision_type = 3
        self.player = None
        self.acc = 1000
        self.max_vel = 90

        dy = Vec2d(0, self.size[1]/4)
        self.wheel_front = Wheel(space, self.body.position - dy , (self.size[0], 20), 1)
        self.wheel_back = Wheel(space, self.body.position + dy , (self.size[0], 20), 1)

        joint_front = pymunk.PivotJoint(self.wheel_front.body, self.body, (0,0), -dy)
        joint_front.collide_bodies = False
        joint_back = pymunk.PivotJoint(self.wheel_back.body, self.body, (0,0), dy)
        joint_back.collide_bodies = False
        space.add(joint_front, joint_back)

        def vel_fun(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, 0.99, dt)
            if body.velocity.length > self.max_vel:
                body.velocity = self.max_vel*body.velocity.normalized()
            self.wheel_front.rest_mode(self.body.angle)
            self.wheel_back.turn(self.body.angle)
        
        self.body.velocity_func = vel_fun
        self.filter = pymunk.ShapeFilter(categories=0b100)

    @property
    def speed(self):
        return self.body.velocity.length
    
    @property
    def velocity(self):
        return self.body.velocity

    def get_door_pos(self):
        ang = self.body.angle
        dx = -(self.size[0]/2 + self.player.radius)*Vec2d(cos(ang), sin(ang) )
        #dy = (self.size[1]/4)*Vec2d(-sin(ang), cos(ang) )
        pos = self.body.position + dx
        return pos
    
    def brake(self):
        self.wheel_back.stop()

    def turn(self, direction:int):
        '''Turn Left if direction < 0\n
        Turn Right if direction > 0'''
        self.wheel_front.add_to_angle(0.1*direction, self.body.angle)

    def accelerate(self):
        self.wheel_back.accelerate(-self.acc)

    def back(self):
        self.wheel_back.accelerate(self.acc/2)

    def add_player(self, player):
        self.player = player
    
    def get_player(self) -> Player|None:
        return self.player
