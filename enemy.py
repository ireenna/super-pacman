import pygame
from settings import *

vec = pygame.math.Vector2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.field_xy = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_xy()
        self.radius = int(self.app.cell_width//2.3)
        self.number = number
        self.direction = vec(1, 0)
        self.target = None
        self.speed = 2


    def can_move(self):
        for wall in self.app.walls:
            if vec(self.field_xy+self.direction) == wall:
                return False
        return True

    def update(self):
        if self.can_move():
            self.pix_pos += self.direction
        elif self.direction == vec(-1, 0):
            self.direction = vec(1,0)
        elif self.direction == vec(1,0):
            self.direction = vec(-1,0)

        self.field_xy[0] = (self.pix_pos[0]-BORDER_FIELD +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.field_xy[1] = (self.pix_pos[1]-BORDER_FIELD +
                            self.app.cell_height//2)//self.app.cell_height+1

    def draw(self):
        self.pacman = pygame.transform.scale(pygame.image.load('images/ghost.png'), (self.app.cell_width,
                                                                                     self.app.cell_height))
        if (self.direction == vec(-1, 0)):
            self.pacman = pygame.transform.flip(self.pacman, True, False)

        self.app.screen.blit(self.pacman, (int(self.pix_pos.x - 10), int(self.pix_pos.y - 10)))




    def get_xy(self):
        return vec((self.field_xy.x*self.app.cell_width)+BORDER_FIELD//2+self.app.cell_width//2,
                   (self.field_xy.y*self.app.cell_height)+BORDER_FIELD//2 +
                   self.app.cell_height//2)


