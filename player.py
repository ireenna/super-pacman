import pygame
from settings import *


vec = pygame.math.Vector2

class Player:
    def __init__(self, app, pos):
        self.app = app
        self.starting_pos = [pos.x, pos.y]
        self.field_xy = pos
        self.pix_pos = self.get_xy()
        self.direction = vec(1, 0)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = 2

    def update(self):
        if self.able_to_move:
            self.pix_pos += self.direction*self.speed
        if self.time_to_move():
            if self.stored_direction != None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()

        self.field_xy[0] = (self.pix_pos[0]-BORDER_FIELD +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.field_xy[1] = (self.pix_pos[1]-BORDER_FIELD +
                            self.app.cell_height//2)//self.app.cell_height+1
        if self.on_coin():
            self.eat_coin()

        if self.on_loop():
            self.transfer_by_loop()

    def draw(self):
        self.pacman = pygame.transform.scale(pygame.image.load('images/pacman.png'), (self.app.cell_width,
                                                                                      self.app.cell_height))
        if(self.direction == vec(-1,0)):
            self.pacman = pygame.transform.flip(self.pacman, True, False)
        elif(self.direction == vec(0, 1)): #doesn't work :(
            self.pacman = pygame.transform.flip(self.pacman, False, True)
        elif (self.direction == vec(0, -1)):
            self.pacman = pygame.transform.flip(self.pacman, False, False)

        self.app.screen.blit(self.pacman, (int(self.pix_pos.x - 10),int(self.pix_pos.y - 10)))




    def on_coin(self):
        if self.field_xy in self.app.coins:
            if int(self.pix_pos.x+BORDER_FIELD//2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+BORDER_FIELD//2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def on_loop(self):
        if self.field_xy in self.app.loops:
            if int(self.pix_pos.x + BORDER_FIELD // 2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y + BORDER_FIELD // 2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def eat_coin(self):
        self.app.coins.remove(self.field_xy)
        self.current_score += 1

    def transfer_by_loop(self):
        if(self.direction == vec(1, 0)):
            self.field_xy = vec(self.app.loops[0])
        elif(self.direction == vec(-1, 0)):
            self.field_xy = vec(self.app.loops[1])

        self.pix_pos = self.get_xy()
        self.app.player.draw()
        self.update()

    def move(self, direction):
        self.stored_direction = direction

    def get_xy(self):
        return vec((self.field_xy[0]*self.app.cell_width)+BORDER_FIELD//2+self.app.cell_width//2,
                   (self.field_xy[1]*self.app.cell_height) +
                   BORDER_FIELD//2+self.app.cell_height//2)

    def time_to_move(self):
        if int(self.pix_pos.x+BORDER_FIELD//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+BORDER_FIELD//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def can_move(self):
        for wall in self.app.walls:
            if vec(self.field_xy+self.direction) == wall:
                return False
        return True