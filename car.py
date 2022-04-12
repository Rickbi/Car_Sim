import pygame
from pygame.locals import *
import pymunk
from pymunk import Vec2d
from block import Block
from math import cos, sin

class Wheel(Block):
    def __init__(self, space, pos, size, density) -> None:
        super().__init__(space, pos, size, density)

        self.color = pygame.Color(255,0,0)
        self.collision_type = 2
        self.acc = 1000
        self.max_vel = 90
        self.max_angle = 0.51

        def vel_condition(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, 0.99, dt)
            nx = Vec2d( cos(body.angle), sin(body.angle) )
            ny = Vec2d( -sin(body.angle), cos(body.angle) )
            vx = nx*body.velocity.dot(nx)
            vy = ny*body.velocity.dot(ny)
            body.velocity = vy
                
        self.body.velocity_func = vel_condition

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
    def __init__(self, space, pos, size, density) -> None:
        super().__init__(space, pos, size, density)
        
        self.color = pygame.Color(200,200,200)

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
            if not self.player:
                self.wheel_front.turn(self.body.angle)
                self.wheel_back.turn(self.body.angle)
        
        self.body.velocity_func = vel_fun

    def key_release(self):
        for event in pygame.event.get(KEYUP):
            if event.key == K_f:
                ang = self.body.angle
                dx = -(self.size[0]/2 + self.player.radius)*Vec2d(cos(ang), sin(ang) )
                dy = (self.size[1]/4)*Vec2d(-sin(ang), cos(ang) )
                pos = self.body.position + dx
                self.player.add_to_space(pos, self.body.velocity)
                self.player.car = None
                self.player = None

    def update(self):
        self.key_release()
        keys = pygame.key.get_pressed()
        self.wheel_back.turn(self.body.angle)
        
        if keys[K_DOWN] or keys[K_s]:
            self.wheel_back.accelerate(self.acc/2)
        if keys[K_UP] or keys[K_w]:
            self.wheel_back.accelerate(-self.acc)
        
        if keys[K_LEFT] or keys[K_a]:
            self.wheel_front.add_to_angle(-0.1, self.body.angle)
        if keys[K_RIGHT] or keys[K_d]:
            self.wheel_front.add_to_angle(0.1, self.body.angle)
        
        if not(keys[K_RIGHT] or keys[K_d]) and not(keys[K_LEFT] or keys[K_a]):
            self.wheel_front.rest_mode(self.body.angle)
        
        if keys[K_SPACE]:
            self.wheel_back.stop()
       
    @property
    def velocity(self):
        return self.body.velocity.length
    
    def add_player(self, player):
        self.player = player
    
    def remove_player(self):
        self.player = None