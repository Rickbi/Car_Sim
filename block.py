import pymunk

class Block(pymunk.Poly):
    def __init__(self, space, pos, size, density) -> None:
        box = pymunk.Poly.create_box(None, size)
        vertices = box.get_vertices()
        super().__init__(body=None, vertices=vertices, radius=1)
        
        self.body = pymunk.Body()
        self.body.position = pos
        self.density = density
        self.elasticity = 1
        self.friction = 1
        self.collision_type = 1
        self.size = size
        
        space.add(self.body, self)

        def vel_condition(body:pymunk.Body, gravity, damping, dt):
            pymunk.Body.update_velocity(body, gravity, 0.95, dt)

        self.body.velocity_func = vel_condition

    def __del__(self):
        if self.space:
            self.space.remove(self.body, self)