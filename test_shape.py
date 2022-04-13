import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
from random import randint
from math import cos, sin

from player import Player
from block import Block
from car import Wheel, Car
from ui import EventHandler

class Box(pymunk.Poly):
    def __init__(self, size, space, pos) -> None:
        box = pymunk.Poly.create_box(None, size)
        vertices = pymunk.Poly.get_vertices(box)
        super().__init__(body=None, vertices=vertices, radius=1)
        self.size = size
        self.body = pymunk.Body()
        self.body.position = Vec2d(*pos)
        self.density = 1
        self.elasticity = 0.8
        self.friction = 1
        self.collision_type = 2
        space.add(self.body, self)
        self.test = 'Hola Poly'
        
        self.body.center_of_gravity = Vec2d(0,size[1]/2)

        def new_mov(body:pymunk.Body, gravity, damping, dt):
            body.update_velocity(body, gravity, damping, dt)
            n = Vec2d(-sin(body.angle), cos(body.angle))
            vn = body.velocity.dot(n)
            body.velocity = n*vn

        self.body.velocity_func = new_mov
    
    def apply_force(self, acc, point = (0,0)):
        self.body.apply_force_at_local_point(acc*self.mass, point)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_s]:
            self.apply_force(Vec2d(0,100))
        if keys[K_w]:
            self.apply_force(Vec2d(0,-100))
        
        if keys[K_d]:
            f = Vec2d(0,-100)
            self.apply_force(f, (0,self.size[1]/2))
            self.apply_force(f.rotated_degrees(10), (0,-self.size[1]/2))
            #self.apply_force(Vec2d(-10,0), (0,-self.size[1]))
            #self.apply_force(Vec2d(10,0), (0,-self.size[1]/2))

        if keys[K_a]:
            f = Vec2d(0,-100)
            self.apply_force(f, (0,self.size[1]/2))
            self.apply_force(f.rotated_degrees(-10), (0,-self.size[1]/2))
            #self.apply_force(Vec2d(-100,0))
            #self.apply_force(Vec2d(10,0), (0,self.size[1]/2))
            #self.apply_force(Vec2d(-10,0), (0,-self.size[1]/2))
        
        if keys[K_SPACE]:
            self.body.velocity = Vec2d(0,0)
            self.body.angular_velocity = 0

class Circle(pymunk.Circle):
    def __init__(self, radius, space, pos) -> None:
        super().__init__(body=None, radius=radius)
        self.body = pymunk.Body()
        self.body.position = Vec2d(*pos)
        self.density = 1
        self.elasticity = 0.8
        self.friction = 1
        self.collision_type = 2
        space.add(self.body, self)

        self.test = 'Hola Circle'

def add_shapes(space: pymunk.Space) -> None:
    print('Adding Shapes...')
    seg_b = pymunk.Body(body_type=pymunk.Body.STATIC)
    seg = pymunk.Segment(seg_b, (0,900), (1000,900), 5)
    seg.elasticity = 1
    seg.friction = 1
    seg.collision_type = 1
    space.add(seg_b, seg)

    #c = Circle(20, space, (100,0))
    p = Box((50,100), space, (600,200))


    def coll(arbiter : pymunk.Arbiter, space, data):
        if arbiter.is_first_contact:
            color = pygame.Color(randint(0,255), randint(0,255), randint(0,255))
            for a in arbiter.shapes:
                a.color = color
                if isinstance(a, Circle|Box):
                    print(f'Test: {a.test}')

    coll_h = space.add_collision_handler(1,2)
    coll_h.post_solve = coll
    return p

def main():
    size = (1000, 900)
    fps = 60

    pygame.init()
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = Vec2d(0, 0)
    space.damping = 0.2
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    car = add_shapes(space)

    run = True
    while run:
        if pygame.event.get(QUIT):
            run = False
        
        #screen.fill((100,100,100))
        car.update()
        space.debug_draw(draw_options)
        space.step(1/fps)

        clock.tick(fps)
        pygame.display.flip()
    
    pygame.quit()

def main_2():
    size = (1000, 900)
    fps = 60

    pygame.init()
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = Vec2d(0, 0)
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    
    ui = EventHandler(space)

    player = Player(space, (100,100), 10, 1)
    wheel = Wheel(space, (500, 100), (50, 20), 1)
    car = Car(space, (400,500), (50,100), 1)
    car.add_player(player)

    boxes = []
    for i in range(10):
        b = Block(space, (200, 100 + i*33), (100,25), 1)
        boxes.append(b)
    add_shapes(space)

    run = True
    while run:
        if pygame.event.get(QUIT):
            run = False
        
        screen.fill((100,100,100))

        point = space.point_query_nearest((100,100), 50, pymunk.ShapeFilter(mask=0b100))
        if point:
            pygame.draw.circle(screen, (255,0,0), (100,100), 50, 5)
        else:
            pygame.draw.circle(screen, (0,0,255), (100,100), 50, 5)

        #ui.player_event_handler(player)
        #ui.car_event_handler(car)
        ui.event_handler(player)
        #car.update()
        #print(player.velocity)
        
        space.debug_draw(draw_options)
        space.step(1/fps)

        clock.tick(fps)
        pygame.display.flip()
    
    pygame.quit()

if __name__ == '__main__':
    main_2()