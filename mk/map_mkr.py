import pygame
from pygame.locals import *
from pygame import Vector2
from os.path import join
from obj import *

class Screen:
    def __init__(self, size:tuple[int, int], fps:int=60) -> None:
        self.fps : int = fps
        self.zoom_k : float = 1.1
        self.zoom = 1
        self.size = size
        self.pos_0 :tuple[int, int] = (0,0)

        pygame.init()
        self.screen : pygame.Surface = pygame.display.set_mode(size)
        self.screen_rect : pygame.Rect = pygame.Rect((0,0), size)
        self.clock : pygame.time.Clock = pygame.time.Clock()
        consolas = pygame.font.match_font('consolas')
        self.font : pygame.font.Font = pygame.font.Font(consolas, 50)
        
        self.load()
    
    def get_rect_pos(self) -> Vector2:
        pos = pygame.mouse.get_pos()
        org_size = self.screen.get_size()
        new_pos = (
            pos[0]*self.screen_rect.w/org_size[0],
            pos[1]*self.screen_rect.h/org_size[1]
        )
        return Vector2(new_pos)
    
    def mouse_hold(self) -> None:
        keys = pygame.mouse.get_pressed(5)
        if keys[2]:
            self.screen_rect.center = self.pos_0 - self.get_rect_pos()
        if keys[4]:
            self.scale(True)
        if keys[3]:
            self.scale(False)

    def scale(self, zoom_in:bool) -> None:
        self.scale_rect(zoom_in)
        self.selected.sprite.scale(zoom_in)

    def scale_rect(self, zoom_in:bool) -> None:
        if zoom_in:
            self.zoom /= self.zoom_k
        else:
            self.zoom *= self.zoom_k

        new_size = (
            self.size[0]*self.zoom,
            self.size[1]*self.zoom
        )

        center = self.screen_rect.center
        self.screen_rect.size = new_size
        self.screen_rect.center = center

    def mouse_press(self) -> None:
        for event in pygame.event.get(MOUSEBUTTONDOWN):
            if event.button == 3:
                self.pos_0 = self.get_rect_pos() + self.screen_rect.center
            elif event.button in {4, 7}:
                self.scale(True)
            elif event.button in {5, 6}:
                self.scale(False)
        
        for event in pygame.event.get(MOUSEBUTTONUP):
            if event.button == 1:
                pos = self.get_rect_pos() + self.screen_rect.topleft
                obj:Obj = self.selected.sprite.copy(self.selected.sprite, pos)
                self.objs.add( obj )
    
    def key_hold(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.selected.sprite.rotate(1)
        elif keys[K_RIGHT]:
            self.selected.sprite.rotate(-1)

    def key_press(self) -> None:
        for event in pygame.event.get(KEYUP):
            if event.key in {K_1, K_KP_1}:
                pos = pygame.mouse.get_pos()
                zoom = self.selected.sprite.zoom
                self.selected.add( Obj(pos, 'block', zoom=zoom) )
            elif event.key in {K_2, K_KP_2}:
                pos = pygame.mouse.get_pos()
                zoom = self.selected.sprite.zoom
                self.selected.add( Obj(pos, 'building', zoom=zoom) )
            elif event.key in {K_3, K_KP_3}:
                pos = pygame.mouse.get_pos()
                zoom = self.selected.sprite.zoom
                self.selected.add( Obj(pos, 'car', zoom=zoom) )
            elif event.key in {K_4, K_KP_4}:
                pos = pygame.mouse.get_pos()
                zoom = self.selected.sprite.zoom
                self.selected.add( Obj(pos, 'player', zoom=zoom) )

    def load(self) -> None:
        path_bg = join('assets', 'img', 'bg.png')
        self.surf_bg : pygame.Surface = pygame.image.load(path_bg).convert_alpha()

        self.objs = pygame.sprite.Group()
        self.selected = pygame.sprite.GroupSingle()
        
        self.selected.add( Obj((100,100), 'car') )

    def write(self, text:str, position:tuple[int, int]) -> None:
        text_surf = self.font.render(text, True, (255,255,255))
        rect = text_surf.get_rect(topleft=position)
        self.screen.blit(text_surf, rect)
    
    def update(self) -> None:
        #self.screen_rect.clamp_ip(self.surf_bg.get_rect())
        rect_crop = self.screen_rect.clip(self.surf_bg.get_rect())
        sub_surf = self.surf_bg.subsurface(rect_crop)
        
        if self.screen_rect.size != rect_crop.size:
            pos = [0,0]
            if self.screen_rect.x < 0:
                pos[0] = self.screen_rect.w - rect_crop.w
        
            if self.screen_rect.y < 0:
                pos[1] = self.screen_rect.h - rect_crop.h

            new_surf = pygame.Surface(self.screen_rect.size)
            new_surf.blit(sub_surf, pos)
            sub_surf = new_surf

        re_surf = pygame.transform.scale(sub_surf, self.screen.get_size())
        self.screen.blit(re_surf, (0,0))

    def run(self) -> None:
        run = True
        while run:
            self.screen.fill((100,100,100))
            self.update()
            self.mouse_press()
            self.mouse_hold()
            self.key_press()
            self.key_hold()
            self.write(f'fps: {self.clock.get_fps()//1}', (0,0))
            self.objs.draw(self.surf_bg)
            self.selected.draw(self.screen)
            self.selected.update()
            pygame.display.flip()
            self.clock.tick(self.fps)
            if pygame.event.get(QUIT):
                run = False