import pygame
from pygame.locals import *
from pygame import Vector2

class Square(pygame.sprite.Sprite):
    def __init__(self, color, size, pos) -> None:
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.vel = Vector2(0, 0)
    
    def event_handler(self):
        for event in pygame.event.get(KEYDOWN):
            if event.key == K_w or event.key == K_UP:
                self.vel += Vector2(0,-1)
            if event.key == K_s or event.key == K_DOWN:
                self.vel += Vector2(0,1)
            if event.key == K_a or event.key == K_LEFT:
                self.vel += Vector2(-1,0)
            if event.key == K_d or event.key == K_RIGHT:
                self.vel += Vector2(1,0)
        for event in pygame.event.get(KEYUP):
            if event.key == K_w or event.key == K_UP:
                self.vel += Vector2(0,1)
            if event.key == K_s or event.key == K_DOWN:
                self.vel += Vector2(0,-1)
            if event.key == K_a or event.key == K_LEFT:
                self.vel += Vector2(1,0)
            if event.key == K_d or event.key == K_RIGHT:
                self.vel += Vector2(-1,0)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

def main():
    size = (500, 500)
    fps = 60

    pygame.init()
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    s1 = Square((255,0,0), (100,100), (0,0))
    s2 = Square((0,255,0), (100,100), (200,200))
    squares = pygame.sprite.Group(s1, s2)

    run = True
    while run:
        if pygame.event.get(QUIT):
            run = False
        
        screen.fill((100,100,100))

        squares.sprites()[0].event_handler()
        squares.update()
        squares.draw(screen)

        clock.tick(fps)
        pygame.display.flip()
    
    pygame.quit()

if __name__ == '__main__':
    main()