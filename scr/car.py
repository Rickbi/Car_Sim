import pygame
from pygame.locals import *
import pymunk
from pymunk import Vec2d
from block import Block
from math import cos, sin, radians

from player import Player

class Wheel(Block):
    def __init__(self, space, pos, size, density) -> None:
        super().__init__(space, pos, size, density)

        self.color = pygame.Color(100,100,100)
        self.collision_type = 2
        self.acc = 1000
        self.max_vel = 90
        self.max_angle = 0.51

        def vel_condition(body:pymunk.Body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, 1, dt)
            ny = Vec2d( -sin(body.angle), cos(body.angle) )
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
    def __init__(self, space:pymunk.Space, pos, size, density, acc=100, max_vel=110, angle=0, color='BLUE') -> None:
        super().__init__(space, pos, size, density)
        
        self.car_color = color

        self.collision_type = 3
        self.player = None
        self.acc = acc
        self.max_vel = max_vel
        self.braking = False
        self.brake_ui = True

        self.body.angle = radians(-angle)

        self.wheel_pos = self.size[1]/4
        dy_body = Vec2d(0, self.wheel_pos)
        dy_world = self.wheel_position
        self.wheel_front = Wheel(space, self.body.position - dy_world, (self.size[0], 20), 1)
        self.wheel_back = Wheel(space, self.body.position + dy_world, (self.size[0], 20), 1)
        self.wheel_front.turn(self.angle)
        self.wheel_back.turn(self.angle)

        joint_front = pymunk.PivotJoint(self.wheel_front.body, self.body, (0,0), -dy_body)
        joint_front.collide_bodies = False
        joint_back = pymunk.PivotJoint(self.wheel_back.body, self.body, (0,0), dy_body)
        joint_back.collide_bodies = False
        space.add(joint_front, joint_back)

        def vel_fun(body, gravity, damping, dt):
            if self.braking or self.brake_ui:
                dam = 0.8
                self.braking = False
            else:
                dam = 0.99
            pymunk.Body.update_velocity(body, gravity, dam, dt)
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

    @property
    def wheel_angle(self):
        return self.wheel_front.angle

    @property
    def wheel_position(self):
        direction = Vec2d(-sin(self.angle), cos(self.angle))
        return self.wheel_pos*direction
    
    @property
    def wheel_positions(self):
        dy = Vec2d(-sin(self.angle), cos(self.angle))
        dx = Vec2d(cos(self.angle), sin(self.angle))
        ddx = self.size[0]/2 - 3
        front_left = -self.wheel_pos*dy - ddx*dx
        front_right = -self.wheel_pos*dy + ddx*dx
        back_left = self.wheel_pos*dy - ddx*dx
        back_right = self.wheel_pos*dy + ddx*dx
        return front_left, front_right, back_left, back_right

    @staticmethod
    def make_vertices(size):
        w, h = size
        p1 = Vec2d(-w*17/45, -h/2)
        p2 = Vec2d(w*17/45, -h/2)
        p3 = Vec2d(w/2, -h*0.23)
        p4 = Vec2d(w/2, h*0.39)
        p5 = Vec2d(w/3, h/2)
        p6 = Vec2d(-w/3, h/2)
        p7 = Vec2d(-w/2, h*0.39)
        p8 = Vec2d(-w/2, -h*0.23)
        return p1, p2, p3, p4, p5, p6, p7, p8

    def get_door_pos(self):
        ang = self.body.angle
        dx = -(self.size[0]/2 + self.player.radius)*Vec2d(cos(ang), sin(ang) )
        pos = self.body.position + dx
        return pos
    
    def brake(self):
        self.braking = True

    def turn(self, direction:int):
        '''Turn Left if direction < 0\n
        Turn Right if direction > 0'''
        self.wheel_front.add_to_angle(0.1*direction, self.body.angle)

    def accelerate(self):
        force = self.acc*self.mass
        self.body.apply_force_at_local_point( (0,-force), (0,0))

    def back(self):
        force = self.acc*self.mass
        self.body.apply_force_at_local_point( (0,force), (0,0))

    def add_player(self, player):
        self.player = player
    
    def get_player(self) -> Player|None:
        return self.player

    def quit_brake(self):
        self.brake_ui = False

    def add_brake(self):
        self.brake_ui = True