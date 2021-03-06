import csv
import sys
import time
import traceback
from datetime import datetime
from threading import Timer

import numpy as np
import pygame

import player
from dqn_pacman import PacmanDQN
from enemy import Enemy, RandomEnemy, TargetEnemy
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
        self.timeinfo = None
        self.game_points = 0
        self.muteAgents = False
        self.quiet = False
        self.catchExceptions = False
        self.moveHistory = []


        # position for enemies & players
        self.enemies_xy = []
        self.player_xy = None
        self.background = pygame.transform.scale(pygame.image.load('images/Background.png'), (MAP_WIDTH, MAP_HEIGHT))
        self.map = []
        # self.map = self.randomMaze(ROWS - 1, COLS - 1)
        self.map = self.loadConstMap()
        self.target = {}
        self.set_all_coins()
        # self.generate_coins_enemies(5,1)
        self.load_rand_map()

        self.player = Player(self, vec(self.player_xy))
        self.pacmanDqn = {}
        # self.pacmanDqn.modelTrain()
        self.enemies_xy = [(5,5)]
        self.set_enemies()
        import io
        agents = [self.player]
        self.agentOutput = [io.StringIO() for agent in agents]

        # self.algorythm = self.player.minimax

    def loadGrid(self):
        grid = np.zeros((ROWS+3, COLS + 2), dtype=int)
        file = open("smallmap.txt", "r")  # open the file for reading (thus the "r")
        content = file.read()  # read the entire file contents into a variable
        file.close()  # close the file
        y = 0
        content= content.split('\n')
        for line in self.map:
            x = 0
            y = y + 1
            for char in line:
                x = x + 1
                if char == 0:
                    grid[y, x] = 1
                else:
                    grid[y, x] = 0
        # print(grid)
        return grid

    def run(self):
        # while self.running:
        if self.state == 'start':
                # self.start()
            self.state = 'playing'
        elif self.state == 'playing':
            self.play()
            self.play_update()
            self.play_draw()
        elif self.state == 'lost':
            self.running = False
                # self.reset()
                # pygame.display.update()
                # self.state = 'playing'
                # self.game_over()
        elif self.state == 'win':
            self.running = False

                # self.reset()
                # pygame.display.update()
                # self.state = 'playing'
                # self.game_win()
        else:
            self.running = False
        # self.clock.tick(FPS)
        # pygame.quit()
        # sys.exit()




    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    def loadConstMap(self):
        self.player_xy = [2,2]
        self.map = [[0 for col in range(ROWS+1)] for row in range(COLS+1)]
        with open("smallmap.txt", 'r') as file:
            for y, line in enumerate(file):
                for x, char in enumerate(line):
                    if char == "1":
                        self.map[y][x] = 1
        return self.map

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

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.screen, white, (int(wall.x * self.cell_width)+self.cell_width,
                                                  int(wall.y * self.cell_height)+self.cell_height,
                                 self.cell_width, self.cell_height))


    def set_enemies(self):
        for idx, pos in enumerate(self.enemies_xy):
            self.enemies.append(TargetEnemy(self, vec(pos), idx))

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
                self.timeinfo = datetime.now()

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
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         self.running = False
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_LEFT:
        #             self.player.move(vec(-1, 0))
        #         if event.key == pygame.K_RIGHT:
        #             self.player.move(vec(1, 0))
        #         if event.key == pygame.K_UP:
        #             self.player.move(vec(0, -1))
        #         if event.key == pygame.K_DOWN:
        #             self.player.move(vec(0, 1))
        self.player.move(vec(self.player.direction))

    def play_update(self):
        # temp = self.algorythm()
        # if temp:
        #     self.player.path=temp.pos_xy
        #     total_seconds = (datetime.now() - self.timeinfo).total_seconds()
        #     self.game_points += (temp.value-total_seconds)
        #     print(self.game_points)

        # self.runnn()
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

        # self.player.draw_path()
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
                               (int(coin[0]*self.cell_width)+self.cell_width//2+BORDER_FIELD//2,
                                int(coin[1]*self.cell_height)+self.cell_height//2+BORDER_FIELD//2), 3)
        if len(self.coins) == 0:
            self.state = "win"

# GAME WIN

    def game_win(self):
        if self.timeinfo:
            # self.writeGameResults()
            self.timeinfo = None
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
        if self.timeinfo:
            # self.writeGameResults()
            self.timeinfo = None
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

    def writeGameResults(self):
        self.timeinfo = datetime.now() - self.timeinfo
        data = [self.algorythm.__name__, self.state, str(self.timeinfo), self.player.current_score, self.game_points]
        # print(data)
        with open('result.csv', 'a', encoding='UTF8') as file:
            writer = csv.writer(file)
            writer.writerow(data)


    def randomMaze(self, width,height):
        # ?????????????????? ?????????? ?????????? ?? ???????????? - ??????????????
        maze = [[0 for col in range(width)] for row in range(height)]
        # ?????????????????? ???????????????? ?????????? ?????????????????? ?????????? ?????? ??????????????????, ??????????????????, ???? ?????????? - ???????????????? ?????????? ???????????? ??????????????
        self.DFS_maze(1,1,1,1,maze,[])
        self.player_xy = [2,2]
        return maze


    def set_all_coins(self):
        # empty_fields = []
        self.coins.append((6,6))
        self.coins.append((6,2))
        self.coins.append((2,6))
        self.high_coins.append((6, 6))
        self.high_coins.append((6, 2))
        self.high_coins.append((2, 6))

        # self.target = empty_fields.pop()

    def generate_coins_enemies(self, c = 4, e=1):
        empty_fields = []
        y = 0
        for line in self.map:
            y = y + 1
            x = 0
            for char in line:
                x = x + 1
                if char == 1:
                    empty_fields.append(vec(x, y))

        for _ in range(c):
            coin = random.choice(empty_fields)
            empty_fields.remove(coin)
            self.coins.append((coin[0],coin[1]))
            self.high_coins.append((coin[0],coin[1]))

        for _ in range(e):
            enemy = random.choice(empty_fields)
            self.enemies_xy.append((enemy[0],enemy[1]))
            empty_fields.remove(enemy)

        self.target = empty_fields.pop()

    # ?????????? ?????????? ?????? ??????????????????
    # ?????? 2 ?????????????????? - ???????? ???? ?????????? - ?????? ????????, ?????? ???????????? ???????????????????? ?????????? ?????????? ????????????
    def DFS_maze(self, betwX, betwY, startX, startY, maze, queue):
        # ?????????????????? ???? ???????? ????????
        if startX < 0 or startY < 0 or startX > len(maze)-1 or startY > len(maze[0])-1:
            return maze
        # ?????????????????? ???? ????, ???? ???????????????? ???????? ????????, ?????????? ?????????????????? 1 - ?????????????????? ?????????? ?????? ??????????????
        if maze[startX][startY] == 1:
            return maze
        # ?????????????? ?? ???????? ??????????
        queue.append((startX, startY))
        # ?????????????????????? ?????????????? ?????????????? ????????. ???????????????????? ??????????????????
        maze[startX][startY] = maze[betwX][betwY] = 1
        # ???????????? ???? ?? ?????? ?????? ???????? ???????????? ???????????? ?????? ???? ????????????????
        randomWays = [[-1,0],[1,0],[0,1],[0,-1]]
        np.random.shuffle(randomWays)

        for item in randomWays:
            self.DFS_maze(startX + item[0], startY+item[1],startX + item[0]*2, startY+item[1]*2,maze,queue)
        # ???????????????????? ?????????????????? ?????? ?????????????? ?? ??????????
        queue.pop()
        return maze


    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex):
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self):
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def replay(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAP_WIDTH // COLS
        self.cell_height = MAP_HEIGHT // ROWS
        self.walls = []
        self.loops = []
        self.coins = []
        self.high_coins = []
        self.enemies = []
        self.timeinfo = None
        self.game_points = 0
        self.muteAgents = False
        self.quiet = False
        self.catchExceptions = False
        self.moveHistory = []
        self.enemies_xy = []
        self.player_xy = None
        self.background = pygame.transform.scale(pygame.image.load('images/Background.png'), (MAP_WIDTH, MAP_HEIGHT))
        self.map = []
        self.map = self.loadConstMap()
        self.target = {}
        self.set_all_coins()
        self.load_rand_map()

        self.player = Player(self, vec(self.player_xy))
        self.enemies_xy = [(6, 6)]
        self.set_enemies()


    def runGames(self, numGames, numTraining=0):
        games = []
        self.pacmanDqn = PacmanDQN()
        for i in range(numGames):
            self.state = 'playing'
            self.runnn()
            self.replay()
            # self.run()

        if (numGames - numTraining) > 0:
            scores = [game.state.getScore() for game in games]
            wins = [game.state.isWin() for game in games]
            winRate = wins.count(True) / float(len(wins))
            print(('Average Score:', sum(scores) / float(len(scores))))
            print(('Scores:       ', ', '.join([str(score) for score in scores])))
            print(('Win Rate:      %d/%d (%.2f)' %
                   (wins.count(True), len(wins), winRate)))
            print(('Record:       ', ', '.join(
                [['Loss', 'Win'][int(w)] for w in wins])))

        return games

    def _agentCrash(self, agentIndex, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet:
            traceback.print_exc()
        self.state = 'lost'
        self.agentCrashed = True



    def deepCopy(self):
        return self.copy()

    def runnn(self):
        global observation, start_time

        self.numMoves = 0
        agents = []
        pacm = self.pacmanDqn
        agents.append(pacm)


        for i in range(len(agents)):
            agent = agents[i]
            if not agent:
                self.mute(i)
                self.unmute()
                self._agentCrash(i, quiet=True)
                return
            if ("initialStateRegister" in dir(agent)):
                self.mute(i)

                agent.initialStateRegister(self)
                self.unmute()

        agentIndex = 0
        numAgents = len(agents)

        while not (self.state == 'lost' or self.state == 'won'):

            self.clock.tick(FPS)
            agent = agents[agentIndex]


            if 'observationFunction' in dir(agent):
                self.mute(agentIndex)

                observation = agent.observationFunction(
                    self)
                self.unmute()
            else:
                observation = self

            action = None
            self.mute(agentIndex)

            action = agent.getAction(observation)

            self.player.direction = action
            if action == 'Stop':
                self.player.direction = (0,0)

            self.run()


            self.unmute()

            self.moveHistory.append((agentIndex, action))

            for enemy in self.enemies:
                if enemy.field_xy == self.player.field_xy:
                    self.player.current_score = -100
                    self.state = "lost"
            if len(self.coins) == 0:
                self.player.current_score = 100
                self.state = "won"


            self.process(self.state, self)
            if agentIndex == numAgents + 1:
                self.numMoves += 1
            agentIndex = (agentIndex + 1) % numAgents

        for agentIndex, agent in enumerate(agents):
            if "end" in dir(agent):
                try:
                    self.mute(agentIndex)
                    agent.end(self)
                    self.unmute()
                except:
                    if not self.catchExceptions:
                        raise
                    self._agentCrash(agentIndex)
                    self.unmute()
                    return



    def process(self, state, game):
        if state == 'won':
            self.win(state, game)
        if state == 'lose':
            self.lose(state, game)

    def win(self, state, game):
        print(("Pacman emerges victorious! Score: %d" % self.player.current_score))

    def lose(self, state, game):
        print(("Pacman died! Score: %d" % self.player.current_score))