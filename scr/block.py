import pymunk

class Block(pymunk.Poly):
    def __init__(self, space, pos, size, density) -> None:
        vertices = self.make_vertices(size)
        super().__init__(body=None, vertices=vertices, radius=0)
        
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
        self.filter = pymunk.ShapeFilter(categories=0b1)

    @property
    def position(self):
        return self.body.position

    @property
    def angle(self):
        return self.body.angle

    def make_vertices(self, size):
        box = pymunk.Poly.create_box(None, size)
        return box.get_vertices()

    def __del__(self):
        if self.space:
            self.space.remove(self.body, self)
    