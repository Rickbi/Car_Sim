import pygame
from pygame.locals import *
import os
import cv2

def main():
    size = (1000,500)
    fps = 60

    pygame.init()
    
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    path = os.path.join('assets','img','car.png')
    img = pygame.image.load(path).convert_alpha()
    rect = img.get_rect(center = (250,250))

    img_np = pygame.surfarray.array3d(img)
    img_np = img_np.transpose([1, 0, 2])
    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    _, img_np = cv2.threshold(img_np,240,255,cv2.THRESH_BINARY_INV)
    contours,_ = cv2.findContours(img_np,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    peri = cv2.arcLength(contours[0],True)
    vertices = cv2.approxPolyDP(contours[0], 0.01 * peri, True)
    
    new_ver = []
    img_np = img_np*0
    for v in vertices:
        cv2.circle(img_np, v[0], 1, (255,255,255), -1)
        new_ver.append(v[0])

    cv2.imwrite(os.path.join('assets','img','car_2.png'), img_np)


    ver = img.copy()
    pygame.draw.polygon(ver, (0,255,0), new_ver, 1)
    rect2 = ver.get_rect(center = (750,250))

    run = True
    while run:
        screen.fill((100,100,100))

        screen.blit(img, rect)
        screen.blit(ver, rect2)

        pygame.display.flip()
        clock.tick(fps)
        if pygame.event.get(QUIT):
            run = False

if __name__ == '__main__':
    main()