import heapq
import math
import queue
import random
import sys
import time
from datetime import datetime

import pygame

import search_algorythm
from search_algorythm import *
from settings import *


vec = pygame.math.Vector2

class Player:
    def __init__(self, app, pos):
        self.app = app
        self.starting_pos = [pos.x, pos.y]
        print("START ", self.starting_pos)
        self.field_xy = pos
        self.pix_pos = self.get_xy()
        self.direction = vec(0, 0)
        self.stored_direction = None
        self.able_to_move = True
        self.current_score = 0
        self.speed = 2
        # self.path = []
        self.maze = search_algorythm.maze_to_grid(self.app.map)
        self.path = []
        # self.path = self.collect_coins()

        # self.path = AlgStar(self.maze, (int(self.field_xy[1])-1, int(self.field_xy[0])-1),
        #                     (int(self.app.target[0]-1),int(self.app.target[1]-1)),
        #                     search_algorythm.take_all_coins_heuristic, self.app.coins)

    def draw_path(self):
        for step in self.path[1:-1]:
            pygame.draw.rect(self.app.screen, 'pink', (step[1] * self.app.cell_width+BORDER_FIELD-10,
                                                             step[0] * self.app.cell_height+BORDER_FIELD-10,
                                                             self.app.cell_width,
                                                             self.app.cell_height))
    def update(self):
        if self.path:
            self.field_xy = vec(self.path[0], self.path[1])
            self.pix_pos = self.get_xy()
        else:
            if self.can_move():
                if self.stored_direction: self.field_xy += vec(self.stored_direction)
                self.pix_pos = self.get_xy()

        if self.time_to_move():
            if self.stored_direction != None:
                 self.direction = self.stored_direction
            self.able_to_move = self.can_move()

        # self.field_xy[0] = (self.pix_pos[0]-BORDER_FIELD +
        #                     self.app.cell_width//2)//self.app.cell_width+1
        # self.field_xy[1] = (self.pix_pos[1]-BORDER_FIELD +
        #                     self.app.cell_height//2)//self.app.cell_height+1
        if self.on_coin():
            self.eat_coin()

        if self.on_loop():
            self.transfer_by_loop()

    def getCostOfActions(self, actions):
        x, y = self.starting_pos
        for action in actions:
            dx, dy = action.x * self.speed, action.y * self.speed
            x, y = int(x + dx), int(y + dy)
        return len(actions)

    def draw(self):
        self.pacman = pygame.transform.scale(pygame.image.load('images/pacman.png'), (self.app.cell_width,
                                                                                      self.app.cell_height))
        if(self.direction == vec(-1,0)):
            self.pacman = pygame.transform.flip(self.pacman, True, False)
        elif(self.direction == vec(0, 1)): #doesn't work :(
            self.pacman = pygame.transform.flip(self.pacman, False, True)
        elif (self.direction == vec(0, -1)):
            self.pacman = pygame.transform.flip(self.pacman, False, False)

        self.app.screen.blit(self.pacman, (int(self.pix_pos.x - 15),int(self.pix_pos.y - 15)))




    def on_coin(self):
        if (self.field_xy[0], self.field_xy[1]) in self.app.coins:
            return True
            # if int(self.pix_pos.x+BORDER_FIELD//2) % self.app.cell_width == 0:
            #     if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
            #         return True
            # if int(self.pix_pos.y+BORDER_FIELD//2) % self.app.cell_height == 0:
            #     if self.direction == vec(0, 1) or self.direction == vec(0, -1):
            #         return True
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
        # if self.path:
        #     self.field_xy = self.path[0]
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
            if self.stored_direction is None:
                self.stored_direction = [0,0]
            if vec(self.field_xy+self.stored_direction) == wall:
                return False
        return True


    def collect_coins(self):
        hero = (self.field_xy[1], self.field_xy[0])
        if hero in self.app.coins:
            self.app.coins.remove(hero)
        newcoins = []
        for coin in self.app.coins:
            newcoins.append((coin[1], coin[0]))

        points = [hero] + newcoins
        # points.append(self.app.target)

        routes = []
        start_time = time.time()
        for j in range(len(points) - 1):
            temp_routs = []

            for i in range(j + 1, len(points)):
                point1 = (int(points[j][0]-1), int(points[j][1]-1))
                point2 = (int(points[i][0]-1), int(points[i][1]-1))

                a = AlgStar(self.maze, point1, point2, search_algorythm.greed_h, 0)

                temp_routs.append(a)

            routes += min(temp_routs, key=len)
        print("M: %s seconds" % (time.time() - start_time))
        return routes

    def can_move_to_field(self, direction):
        for wall in self.app.walls:
            if (self.field_xy + direction) == wall:
                return False
        return True

    def can_move_to_field_from_field(self, direction, field):
        if vec(field[0]+direction[0],field[1]+direction[1]) in self.app.walls:
            return False
        return True

    def pos_dirs(self):
        directions = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        new_dirs = []
        for d in directions:
            if self.can_move_to_field(d):
                new_dirs.append(d)
        return new_dirs

    def pos_dirs_for_field(self, field):
        directions = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        new_dirs = []
        for d in directions:
            if self.can_move_to_field_from_field(d, field):
                new_dirs.append(d)
        return new_dirs

    def minimax(self):
        pacman_possible_pos = [(i + self.field_xy) for i in self.pos_dirs()]

        enemies_pos = [en.field_xy for en in self.app.enemies]
        enemies_possible_pos = [(i+item) for i in enemies_pos for item in self.pos_dirs_for_field(i)]

        # min path to coin
        old_val = MAX
        nearest_food = None
        for item in self.app.coins:
            new_val = manhattan_h(self.field_xy, item)
            # or bfs
            if new_val <= old_val:
                old_val = new_val
                nearest_food = item

        mainNode_max = Node(None, None, True, None)
        for item in pacman_possible_pos:
            mainNode_max.children.append(Node(mainNode_max, item, False, None))

        for secondNode_min in mainNode_max.children:
            for ghostMoves in enemies_possible_pos:
                dist_to_ghost = euclid_h(secondNode_min.pos_xy, ghostMoves)
                dist_to_food = euclid_h(secondNode_min.pos_xy, nearest_food)
                # если враг близко и мы к нему приблизимся, то добавляем этот вариант как самый неоптимальный
                if dist_to_ghost <= 1:
                    secondNode_min.children.append(Node(secondNode_min, ghostMoves, True, MIN)) #добавляем как child child-a
                else:
                    secondNode_min.children.append(Node(secondNode_min, ghostMoves, True, (dist_to_ghost - dist_to_food)+10))

        # минимайзер
        for secondNode_min in mainNode_max.children:
            oldValue = MAX
            for lowlvlMAX in secondNode_min.children:
                if lowlvlMAX.value < oldValue:
                    oldValue = lowlvlMAX.value
                    secondNode_min.value = oldValue

        # максимайзер
        finishNode = MIN
        finishCords = None
        for secondNode_min in mainNode_max.children:
            if secondNode_min.value > finishNode:
                finishNode = secondNode_min.value
                finishCords = secondNode_min

        return finishCords

    def expectimax(self):
        pacman_possible_pos = [(i + self.field_xy) for i in self.pos_dirs()]

        enemies_pos = [en.field_xy for en in self.app.enemies]
        enemies_possible_pos = [(i + item) for i in enemies_pos for item in self.pos_dirs_for_field(i)]

        # min path to coin
        old_val = MAX
        nearest_food = None
        for item in self.app.coins:
            new_val = manhattan_h(self.field_xy, item)
            # or bfs
            if new_val <= old_val:
                old_val = new_val
                nearest_food = item

        mainNode_max = Node(None, None, True, None)
        for item in pacman_possible_pos:
            mainNode_max.children.append(Node(mainNode_max, item, False, None))

        for secondNode_min in mainNode_max.children:
            for ghostMoves in enemies_possible_pos:
                dist_to_ghost = euclid_h(secondNode_min.pos_xy, ghostMoves)
                dist_to_food = euclid_h(secondNode_min.pos_xy, nearest_food)
                # если враг близко и мы к нему приблизимся, то добавляем этот вариант как самый неоптимальный
                if dist_to_ghost <= 1:
                    secondNode_min.children.append(
                        Node(secondNode_min, ghostMoves, True, MIN))  # добавляем как child child-a
                else:
                    secondNode_min.children.append(
                        Node(secondNode_min, ghostMoves, True, (dist_to_ghost - dist_to_food)+10))

        # среднее значение
        for playerMoves in mainNode_max.children:
            child_value_list = [secondNode_min.value for secondNode_min in playerMoves.children]
            playerMoves.value = np.mean(child_value_list)

        # максимизатор
        finishNode = -sys.maxsize
        finishCords = None
        for playerMoves in mainNode_max.children:
            if playerMoves.value > finishNode:
                finishNode = playerMoves.value
                finishCords = playerMoves

        return finishCords
