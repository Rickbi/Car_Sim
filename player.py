import pygame
from pygame.locals import *
import pymunk
from pymunk import Vec2d

class Player(pymunk.Circle):
    def __init__(self, space, pos, radius, density) -> None:
        super().__init__(body=None, radius=radius)
        self.body = pymunk.Body()
        self.density = density
        self.elasticity = 0
        self.friction = 0
        self.collision_type = 4
        self.car = None
        self.enter = False
        self.direction = Vec2d(0,0)
        self.max_velocity = 90
        self.acc = 1000

        self.add_to_space(space, pos, Vec2d(0,0))

        def vel_condition(body:pymunk.Body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, 0.9, dt)
            if body.velocity.length > self.max_velocity:
                body.velocity = body.velocity.normalized()*self.max_velocity

        self.body.velocity_func = vel_condition

    @property
    def velocity(self):
        if self.car:
            return self.car.velocity
        else:
            return self.body.velocity.length

    def key_release(self):
        self.enter = False
        for event in pygame.event.get(KEYUP):
            if event.key == K_f:
                self.enter = True
            if event.key == K_F1:
                self.max_velocity = self.max_velocity*2
                self.acc = self.acc*2
    
    def event_handler(self):
        self.key_release()
        self.direction = Vec2d(0,0)
        keys = pygame.key.get_pressed()
        press = {
            'up'   : keys[K_UP]    or keys[K_w],
            'down' : keys[K_DOWN]  or keys[K_s],
            'left' : keys[K_LEFT]  or keys[K_a],
            'right': keys[K_RIGHT] or keys[K_d]
            }
        
        if press['up']:
            self.direction += Vec2d(0,-1)
        if press['down']:
            self.direction += Vec2d(0,1)
        if press['left']:
            self.direction += Vec2d(-1,0)
        if press['right']:
            self.direction += Vec2d(1,0)

    def update(self):
        if self.car:
            pass
            #self.car.update()
            #self.car.key_release()
        else:
            self.event_handler()
            #impulse = self.direction.normalized()*self.body.mass
            #self.body.apply_impulse_at_local_point(impulse)
            #self.body.velocity = self.direction.normalized()*self.max_velocity
            force = self.direction.normalized()*self.body.mass*self.acc
            self.body.apply_force_at_local_point(force)

    def add_car(self, car):
        self.car = car
    
    def remove_car(self):
        self.car = None

    def remove_from_space(self):
        self.space.remove(self.body, self)

    def add_to_space(self, space, pos, vel):
        self.body.velocity = vel
        self.body.position = pos
        space.add(self.body, self)

    def __del__(self):
        if self.space:
            self.remove_from_space()