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
        self.filter = pymunk.ShapeFilter(categories=0b1000)

    @property
    def speed(self):
        if self.car:
            return self.car.speed
        else:
            return self.body.velocity.length

    @property
    def position(self):
        return self.body.position

    def get_car(self):
        return self.car
    
    def accelerate(self, direction:Vec2d):
        force = direction.normalized()*self.body.mass*self.acc
        self.body.apply_force_at_local_point(force)

    def add_car(self, car):
        self.car = car
    
    def remove_from_space(self):
        self.space.remove(self.body, self)

    def add_to_space(self, space, pos, vel):
        self.body.velocity = vel
        self.body.position = pos
        space.add(self.body, self)

    def __del__(self):
        if self.space:
            self.remove_from_space()
