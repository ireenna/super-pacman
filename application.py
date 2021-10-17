import sys
import time

import numpy as np
import pygame

import player
from enemy import Enemy
from player import Player
from settings import *
import random



pygame.init()
# providing the game with 2 dimensions
vec = pygame.math.Vector2

class App:
    # setting local parameters for the app
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAP_WIDTH//COLS
        self.cell_height = MAP_HEIGHT//ROWS
        self.walls = []
        self.loops = []
        self.coins = []
        self.high_coins = []
        self.enemies = []

        # position for enemies & players
        self.enemies_xy = []
        self.player_xy = None
        self.background = pygame.transform.scale(pygame.image.load('images/Background.png'), (MAP_WIDTH, MAP_HEIGHT))
        self.map = []
        self.map = self.randomMaze(ROWS - 1, COLS - 1)
        self.target = {}
        # self.set_all_coins()
        self.generate_coins(1)
        self.load_rand_map()

        self.player = Player(self, vec(self.player_xy))
        self.set_enemies()



    def run(self):
        while self.running:
            if self.state == 'start':
                self.start()
            elif self.state == 'playing':
                self.play()
                self.play_update()
                self.play_draw()
            elif self.state == 'lost':
                self.game_over()
            elif self.state == 'win':
                self.game_win()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()




    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    # def load(self):
    #     self.background = pygame.transform.scale(pygame.image.load('images/Background.png'), (MAP_WIDTH, MAP_HEIGHT))
    #
    #     with open("map.txt", 'r') as file:
    #         for y, line in enumerate(file):
    #             for x, char in enumerate(line):
    #                 if char == "1":
    #                     self.walls.append(vec(x, y))
    #                 elif char == "C":
    #                     self.coins.append(vec(x, y))
    #                     self.high_coins.append(vec(x,y))
    #                 elif char == "L":
    #                     self.loops.append(vec(x, y))
    #                 elif char == "P":
    #                     self.player_xy = [x, y]
    #                 elif char in ["2", "3", "4", "5"]:
    #                     self.enemies_xy.append([x, y])
    #                 elif char == "B":
    #                     pygame.draw.rect(self.background, black, (x*self.cell_width, y*self.cell_height,
    #                                                               self.cell_width, self.cell_height))

    def load_rand_map(self):
        y = 0
        for line in self.map:
            y = y+1
            x = 0
            for char in line:
                x = x+1
                if char == 0:
                    self.walls.append(vec(x, y))
                    pygame.draw.rect(self.screen, white, (x * self.cell_width, y * self.cell_height,
                                                          self.cell_width, self.cell_height))
                # elif char == 1 & ((x,y) in self.coins):
                #     self.coins.append(vec(x, y))
                #     self.high_coins.append(vec(x, y))
                    # pygame.draw.rect(self.screen, white, (x * self.cell_width, y * self.cell_height,
                    #                                           self.cell_width, self.cell_height))
                # elif char == "L":
                #     self.loops.append(vec(x, y))
                # elif char == "P":
                #     self.player_xy = [x, y]
                # elif char in ["2", "3", "4", "5"]:
                #     self.enemies_xy.append([x, y])
                # elif char == "B":
                #     pygame.draw.rect(self.background, black, (x * self.cell_width, y * self.cell_height,
                #                                               self.cell_width, self.cell_height))

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.screen, white, (int(wall.x * self.cell_width)+self.cell_width,
                                                  int(wall.y * self.cell_height)+self.cell_height,
                                 self.cell_width, self.cell_height))


    def set_enemies(self):
        for idx, pos in enumerate(self.enemies_xy):
            self.enemies.append(Enemy(self, vec(pos), idx))

    def draw_field(self):
        for x in range(WIDTH//self.cell_width):
            pygame.draw.line(self.screen, yellow, (x*self.cell_width, 0),
                             (x*self.cell_width, HEIGHT))
        for x in range(HEIGHT//self.cell_height):
            pygame.draw.line(self.screen, yellow, (0, x*self.cell_height),
                             (WIDTH, x*self.cell_height))

    def reset(self):
        self.__init__()


# START

    def start(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'playing'
        self.start_draw()

    def start_draw(self):
        self.screen.fill(black)
        self.draw_text('WELCOME TO', self.screen, [
                       WIDTH//2, HEIGHT//2-150], 45, orange, START_FONT, centered=True)
        self.draw_text('THE PACMAN GAME', self.screen, [
            WIDTH // 2, HEIGHT // 2 - 115], 45, orange, START_FONT, centered=True)
        self.pacman = pygame.transform.scale(pygame.image.load('images/pacman.png'), (200, 200))
        self.screen.blit(self.pacman, (MAP_WIDTH//2 - 75, MAP_HEIGHT//2 - 50))

        self.draw_text('PRESS SPACE TO START', self.screen, [
                       WIDTH//2, HEIGHT//2+150], START_TEXT_SIZE, white, START_FONT, centered=True)
        pygame.display.update()

# PLAYING

    def play(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))

    def play_update(self):
        self.player.update()
        for enemy in self.enemies:
            enemy.update()

        for enemy in self.enemies:
            if enemy.field_xy == self.player.field_xy:
                self.state = "lost"

    def play_draw(self):
        self.screen.fill(black)
        self.draw_text('SCORE: {} / {}'.format(self.player.current_score,len(self.high_coins)),
                       self.screen, [60, 0], 18, white, START_FONT)

        self.player.draw_path()
        self.player.draw()
        self.draw_walls()
        self.draw_coins()
        # self.draw_field()
        for enemy in self.enemies:
            enemy.draw()
            enemy.path = []
            # enemy.path = enemy.aStarSearch(vec(enemy.field_xy), self.player.field_xy)
            # enemy.path = enemy.get_DFS(vec(enemy.field_xy), self.player.field_xy)
            # enemy.path = enemy.get_UCS(vec(enemy.field_xy), vec(self.player.field_xy))
            enemy.draw_path()
        pygame.display.update()


    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, orange,
                               (int(coin[0]*self.cell_width)+self.cell_width//2+BORDER_FIELD//2-5,
                                int(coin[1]*self.cell_height)+self.cell_height//2+BORDER_FIELD//2-5), 3)
        if len(self.coins) == 0:
            self.state = "win"

# GAME WIN

    def game_win(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
        self.game_win_draw()

    def game_win_draw(self):
        self.screen.fill(black)
        self.draw_text('YOU WON!', self.screen, [
            WIDTH // 2, HEIGHT // 2 - 150], 45, green, START_FONT, centered=True)
        self.pacman = pygame.transform.scale(pygame.image.load('images/pacman.png'), (200, 200))
        self.screen.blit(self.pacman, (MAP_WIDTH // 2 - 75, MAP_HEIGHT // 2 - 60))
        self.draw_text('PRESS SPACE TO PLAY AGAIN', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 150], START_TEXT_SIZE, white, START_FONT, centered=True)
        self.draw_text('PRESS ESC TO QUIT', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 200], START_TEXT_SIZE, white, START_FONT, centered=True)
        pygame.display.update()

# GAME OVER

    def game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
        self.game_over_draw()


    def game_over_draw(self):
        self.screen.fill(black)
        self.draw_text('YOU LOST', self.screen, [
            WIDTH // 2, HEIGHT // 2 - 150], 45, red, START_FONT, centered=True)
        self.ghost = pygame.transform.scale(pygame.image.load('images/ghost.png'), (150, 150))
        self.screen.blit(self.ghost, (MAP_WIDTH // 2 - 50, MAP_HEIGHT // 2 - 50))
        self.draw_text('PRESS SPACE TO PLAY AGAIN', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 150], START_TEXT_SIZE, white, START_FONT, centered=True)
        self.draw_text('PRESS ESC TO QUIT', self.screen, [
            WIDTH // 2, HEIGHT // 2 + 200], START_TEXT_SIZE, white, START_FONT, centered=True)
        pygame.display.update()


    def randomMaze(self, width,height):
        # створюємо пусту карту з нулями - стінами
        maze = [[0 for col in range(width)] for row in range(height)]
        # передаємо стартову точку генерації карти для алгоритма, генеруємо, та після - вказуємо місце нашого пакмена
        self.DFS_maze(1,1,1,1,maze,[])
        self.player_xy = [2,2]
        return maze

    def set_all_coins(self):
        empty_fields = []
        y = 0
        for line in self.map:
            y = y + 1
            x = 0
            for char in line:
                x = x + 1
                if char == 1:
                    empty_fields.append(vec(x, y))

        for coin in empty_fields:
            self.coins.append((coin[0],coin[1]))
            self.high_coins.append((coin[0],coin[1]))

        self.target = empty_fields.pop()

    def generate_coins(self, num = 4):
        empty_fields = []
        y = 0
        for line in self.map:
            y = y + 1
            x = 0
            for char in line:
                x = x + 1
                if char == 1:
                    empty_fields.append(vec(x, y))

        for _ in range(num):
            coin = random.choice(empty_fields)
            self.coins.append((coin[0],coin[1]))
            self.high_coins.append((coin[0],coin[1]))

        self.target = empty_fields.pop()
        print("COINS ", self.coins)

    # пошук вглиб для лабіринта
    # тут 2 параметри - бетв та старт - для того, щоб одразу проглядати карту двома шагами
    def DFS_maze(self, betwX, betwY, startX, startY, maze, queue):
        # перевірка на краї мапи
        if startX < 0 or startY < 0 or startX > len(maze)-1 or startY > len(maze[0])-1:
            return maze
        # перевірка на те, чи пройдена наша мапа, тобто позначена 1 - свободним полем для проходу
        if maze[startX][startY] == 1:
            return maze
        # додаємо в нашу чергу
        queue.append((startX, startY))
        # призначаємо обидвом змінним знач. пройденної території
        maze[startX][startY] = maze[betwX][betwY] = 1
        # робимо ці ж дії для усіх сторін допоки все не пройдемо
        randomWays = [[-1,0],[1,0],[0,1],[0,-1]]
        np.random.shuffle(randomWays)

        for item in randomWays:
            self.DFS_maze(startX + item[0], startY+item[1],startX + item[0]*2, startY+item[1]*2,maze,queue)
        # прибираємо оглянутий вже елемент з черги
        queue.pop()
        return maze