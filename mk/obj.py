from __future__ import annotations
import pygame
from os.path import join
from typing import Any

class Obj(pygame.sprite.Sprite):
    def __init__(self, position:tuple[int, int], name:str, ang:float=0, zoom:float=1) -> None:
        super().__init__()
        path = join('assets', 'img', f'{name}.png')
        self.org_img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.rotate(self.org_img, ang)
        self.rect = self.image.get_rect(center=position)
        self.name = name
        self.ang = ang
        self.zoom_k = 1.1
        self.zoom = zoom
        self.update_img()
    
    @classmethod
    def copy(cls, obj:Obj, pos:tuple[int, int]) -> Obj:
        re = Obj(pos, obj.name, ang=obj.ang)
        return re

    def update_img(self) -> None:
        org_size = self.org_img.get_size()
        size = (
            org_size[0]*self.zoom,
            org_size[1]*self.zoom
        )
        scaled = pygame.transform.scale(self.org_img, size)
        rot = pygame.transform.rotate(scaled, self.ang)
        rect = rot.get_rect(center=self.rect.center)
        self.image = rot
        self.rect = rect

    def rotate(self, ang:float) -> None:
        self.ang += ang
        self.update_img()

    def scale(self, zoom_in:bool) -> None:
        if zoom_in:
            self.zoom *= self.zoom_k
        else:
            self.zoom /= self.zoom_k
        self.update_img()

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.rect.center = pygame.mouse.get_pos()
        return super().update(*args, **kwargs)

    def get_data_to_save(self):
        dic = {
            'position' : self.rect.center,
            'angle' : self.ang
        }
        return dic
