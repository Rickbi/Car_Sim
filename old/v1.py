import pygame
from pygame.locals import *
from time import perf_counter
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
from math import cos, sin, pi

class Circle():
    def __init__(self, space, pos, r = 10, mass = 10) -> None:
        self.body = pymunk.Body(mass, float('inf'))
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, r)
        self._space = space
        self.radius = r
        
        self.shape.elasticity = 0
        self.shape.friction = 0
        self.shape.collision_type = 4
        space.add(self.body, self.shape)

        self.car = None
        self.enter = False

        def vel_condition(body, gravity, damping, dt):
            #pymunk.Body.update_velocity(body, gravity, damping, dt)
            pymunk.Body.update_velocity(body, gravity, 0.9, dt)

        self.body.velocity_func = vel_condition

    @property
    def velocity(self):
        if self.car:
            return self.car.velocity
        else:
            return self.body.velocity.length

    def move_player(self):
        keys = pygame.key.get_pressed()
        direction = Vec2d(0,0)
        press = {
            'up'   : keys[K_UP]    or keys[K_w],
            'down' : keys[K_DOWN]  or keys[K_s],
            'left' : keys[K_LEFT]  or keys[K_a],
            'right': keys[K_RIGHT] or keys[K_d]
            }
        
        if press['up']:
            direction += Vec2d(0,-1)
        if press['down']:
            direction += Vec2d(0,1)
        if press['left']:
            direction += Vec2d(-1,0)
        if press['right']:
            direction += Vec2d(1,0)
        
        impulse = direction.normalized()*1000/self.body.mass
        self.body.apply_impulse_at_local_point(impulse)

        #self.enter = keys[K_f]
        #self.body.velocity = 100*direction

        #force = direction.normalized()*10000
        #self.body.apply_force_at_local_point( force, (0,0))

    def remove_from_space(self):
        self._space.remove(self.shape, self.body)

    def add_to_space(self, pos, vel):
        self.body.velocity = vel
        self.body.position = pos
        self._space.add(self.shape, self.body)

    def key_release(self):
        self.enter = False
        for event in pygame.event.get(KEYUP):
            if event.key == K_f:
                print('F pressed')
                self.enter = True

    def update(self):
        if self.car:
            self.car.update()
            self.car.key_release()
        else:
            self.key_release()
            self.move_player()

    def __del__(self):
        if not self.car:
            self.remove_from_space()

class Rectangle():
    def __init__(self, space, pos, size = (50,100), mass = 10) -> None:
        moment = pymunk.moment_for_box(mass, size)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, size)
        self._space = space
        # vertices = [
        #      (-size[0]*0.5,-size[1]*0.5),
        #      (size[0]*0.5,-size[1]*0.5),
        #      (size[0]*0.5,size[1]*0.5),
        #      (-size[0]*0.5,size[1]*0.5)
        #      ]
        # self.shape = box = pymunk.Poly(self.body, vertices)
        self.shape.elasticity = 1
        self.shape.friction = 1
        self.shape.collision_type = 1
        space.add(self.body, self.shape)

    def __del__(self):
        #print('Deleting Rectangle')
        self._space.remove(self.shape, self.body)
    
class Wheel(Rectangle):
    def __init__(self, space, pos, size=(50, 20), mass=10, static=False, force=10000, max_vel=100) -> None:
        super().__init__(space, pos, size, mass)
        self.shape.collision_type = 2
        self.force = force
        self.max_vel = max_vel

        def new_velocity(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, damping, dt)
            nx = Vec2d( cos(body.angle), sin(body.angle) )
            ny = Vec2d( -sin(body.angle), cos(body.angle) )
            vx = nx*body.velocity.dot(nx)
            vy = ny*body.velocity.dot(ny)
            body.velocity = vy
        
        def new_velocity_static(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, damping, dt)
            body.velocity = Vec2d(0, 0)
        
        self.velocity_func_acc = new_velocity
        self.velocity_func_stc = new_velocity_static

        if static:
            self.body.velocity_func = self.velocity_func_stc
        else:
            self.body.velocity_func = self.velocity_func_acc

    def apply_force(self, force):
        self.body.apply_force_at_local_point( (0,force), (0,0))

    def apply_torque(self, torque):
        self.body.torque = torque
    
    def turn(self, ang):
        self.body.angle = ang
    
    def apply_angle(self, ang, ref):
        self.body.angle += ang
        da = ref - self.body.angle
        if -0.51 > da:
            self.body.angle = ref + 0.51
        elif 0.51 < da:
            self.body.angle = ref - 0.51
    
    def default_angle(self, ref):
        da = ref - self.body.angle
        if da > 0:
            self.apply_angle(0.05, ref)
        elif da < 0:
            self.apply_angle(-0.05, ref)

    def stop(self):
        nw = Vec2d(-sin(self.body.angle), cos(self.body.angle))
        nv, v = self.body.velocity.normalized_and_length()
        f = nw.dot(nv)
        if f < 0 and v > 5:
            self.apply_force(self.force)
        elif f > 0 and v > 5:
            self.apply_force(-self.force)

    def wheel_break(self, status):
        if status:
            self.body.velocity_func = self.velocity_func_stc
        else:
            self.body.velocity_func = self.velocity_func_acc

class Car(Rectangle):
    def __init__(self, space, pos, size=(50, 100), mass=10, static=False, force=10000, max_vel=100) -> None:
        super().__init__(space, pos, size, mass)
        self.shape.collision_type = 3
        self.wheel = Wheel(space, (pos[0], pos[1] + 40) , mass = 10, static=static, force=force, max_vel=max_vel)
        self.wheel2 = Wheel(space, (pos[0], pos[1] - 40) , mass = 10, static=static, force=force, max_vel=max_vel)
        self.player = None
        self.size = size
        self.force = force
        self.breaks = static
        self.max_vel = max_vel

        joint = pymunk.PivotJoint(self.wheel.body, self.body, (0,0), (0,40))
        joint.collide_bodies = False
        joint2 = pymunk.PivotJoint(self.wheel2.body, self.body, (0,0), (0,-40))
        joint2.collide_bodies = False
        space.add(joint, joint2)

        def vel_fun(body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, damping, dt)
            if body.velocity.length > self.max_vel:
                body.velocity = self.max_vel*body.velocity.normalized()
            if not self.player:
                #print('sdsd')
                self.wheel.turn(self.body.angle)
                self.wheel2.turn(self.body.angle)
        
        self.body.velocity_func = vel_fun

    def key_release(self):
        for event in pygame.event.get(KEYUP):
            if event.key == K_f:
                print('F pressed in the car!!!')
                ang = self.body.angle
                dx = -(self.size[0]/2 + self.player.radius)*Vec2d(cos(ang), sin(ang) )
                dy = (self.size[1]/4)*Vec2d(cos(ang - pi/2), sin(ang - pi/2) )
                pos = self.body.position + dx
                self.player.add_to_space(pos, self.body.velocity)
                self.player.car = None
                self.player = None
            
            elif event.key == K_x:
                if self.velocity < 10:
                    self.breaks = not self.breaks
                    self.car_breaks(self.breaks)

    def update(self):
        keys = pygame.key.get_pressed()
        self.wheel.turn(self.body.angle)
        
        if keys[K_DOWN] or keys[K_s]:
            self.wheel.apply_force(self.force/2)
        if keys[K_UP] or keys[K_w]:
            self.wheel.apply_force(-self.force)
        
        if keys[K_LEFT] or keys[K_a]:
            self.wheel2.apply_angle(-0.1, self.body.angle)
        if keys[K_RIGHT] or keys[K_d]:
            self.wheel2.apply_angle(0.1, self.body.angle)
        
        if not(keys[K_RIGHT] or keys[K_d]) and not(keys[K_LEFT] or keys[K_a]):
            self.wheel2.default_angle(self.body.angle)
        
        if keys[K_SPACE]:
            self.wheel.stop()
    
    def car_breaks(self, status):
        self.wheel.wheel_break(status)
        self.wheel2.wheel_break(status)
    
    @property
    def velocity(self):
        return self.body.velocity.length

class Game():
    def __init__(self, width, height, fps = 60) -> None:
        self.window_size = width, height
        self.fps = fps
        self.t0 = 0

        pygame.init()

        self.screen = pygame.display.set_mode(self.window_size)
        self.clock = pygame.time.Clock()
        font_type = pygame.font.match_font('consolas')
        self.font = pygame.font.Font(font_type, 30)
    
        self.space = pymunk.Space()
        self.space.sleep_time_threshold = 0.5
        self.space.idle_speed_threshold = 1
        
        def begin_col(arbiter, space, data):
            for a in arbiter.shapes:
                a.color = pygame.Color('red')
            #print('Begin')
            #print(self.shapes[arbiter.shapes[0]])
            # v1 = arbiter.shapes[0].body.velocity
            # v2 = arbiter.shapes[1].body.velocity
            # vr = (v2-v1).length
            # match vr:
            #     case vr if 10 <= vr < 50:
            #         print(f'Vr : {vr}')
            #         for a in arbiter.shapes:
            #             a.color = pygame.Color('green')
            #     case vr if 50 <= vr < 150:
            #         print(f'Vr : {vr}')
            #         for a in arbiter.shapes:
            #             a.color = pygame.Color('yellow')
            #     case vr if 150 <= vr:
            #         print(f'Vr : {vr}')
            #         for a in arbiter.shapes:
            #             a.color = pygame.Color('red')
            return True
        
        def begin_col_2(arbiter, space, data):
            for a in arbiter.shapes:
                a.color = pygame.Color('green')
            return True
        
        def begin_col_3(arbiter, space, data):
            for a in arbiter.shapes:
                a.color = pygame.Color('blue')
            return True

        def begin_col_4(arbiter, space, data):
            player, car = [self.shapes[a] for a in arbiter.shapes]
            player.shape.color = pygame.Color('white')
            car.shape.color = pygame.Color('yellow')
            if player.enter:
                print(f'Enter : {player.enter}')
                player.enter = False
                player.car = car
                car.player = player
                player.remove_from_space()
                #car.car_breaks(False)
                #player.body.position = Vec2d(600,250)
            
            return True
        
        coll = self.space.add_collision_handler(3, 3)
        coll.begin = begin_col

        coll2 = self.space.add_collision_handler(3, 1)
        coll2.begin = begin_col_2

        coll3 = self.space.add_collision_handler(1, 1)
        coll3.begin = begin_col_3

        coll4 = self.space.add_collision_handler(4, 3)
        #coll4.begin = begin_col_4
        coll4.pre_solve = begin_col_4

        coll_wheel = self.space.add_wildcard_collision_handler(2)
        coll_wheel.begin = lambda arbiter, space, data : False



        self.space.gravity = (0, 0)
        self.space.damping = 0.2
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.load()
    
    def load(self):
        self.wheel = Wheel(self.space, (400,100))
        self.car = Car(self.space, (100,100), mass=10, force=2*10000, max_vel=200)
        self.car2 = Car(self.space, (200,100), static=False)

        self.shapes = {
            self.car.shape : self.car,
            self.car2.shape : self.car2
            }

        self.rects = []
        for i in range(25):
            r = Rectangle(self.space, (500,50 + i*22), (20,20), 1)
            self.rects.append( r )
            self.shapes[r.shape] = r
        
        self.player = Circle(self.space, (200,200))
        self.shapes[self.player.shape] = self.player

    def show_fps(self, surface):
        if dt := perf_counter() - self.t0:
            current_fps = round(1/dt)
        else:
            current_fps = -1
        self.t0 = perf_counter()
        text_surf = self.font.render(f'fps = {current_fps}', True, (255,255,255))
        surface.blit(text_surf, (5, 5))
    
    def show_velocity(self, surface, velocity):
        v = round(velocity)
        text_surf = self.font.render(f'v = {v}', True, (255,255,255))
        surface.blit(text_surf, (5, 200))

    def update(self):
        self.screen.fill((0,0,50))
        self.show_velocity(self.screen, self.player.velocity)
        #self.car.update()
        self.player.update()
        self.space.step(1/self.fps)
        self.space.debug_draw(self.draw_options)
    
    def run_game(self):
        run = True
        
        while run:
            for event in pygame.event.get(QUIT):
                run = False
            
            self.update()
            self.show_fps(self.screen)
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()


if __name__ == '__main__':
    game = Game(1500,900)
    game.run_game()