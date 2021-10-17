import queue
import time
import numpy as np
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
        self.path = None


    def can_move(self):
        for wall in self.app.walls:
            if vec(self.field_xy+self.direction) == wall:
                return False
        return True

    def update(self):
        if self.path is not None:
            pass

        self.field_xy[0] = (self.pix_pos[0]-BORDER_FIELD +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.field_xy[1] = (self.pix_pos[1]-BORDER_FIELD +
                            self.app.cell_height//2)//self.app.cell_height+1

        print(self.field_xy)

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


    def get_BFS(self, start, target): # пошаровий пошук (в ширину)
        grid = self.load_grid()

        if not self.is_valid_target(target):
            print("Wrong target")
            return [start]

        queue = [start] # реалізовуємо через чергу
        path = []
        visited = []
        directions = [[0, -1], [1, 0], [0, 1], [-1, 0]] # вказуємо можливі напрямки

        while queue: # поки в нас є черга (не пуста)
            current = queue[0] # заходимо у перший елемент, позначаємо як теперішній і прибираємо з черги
            queue.remove(queue[0])
            visited.append(current) # помічаємо як відвіданий
            if current == target:
                break
            else:
                for direction in directions: # для усіх напрямків
                    step = current + direction # робимо крок у обраному напрямку
                    if grid[int(step[1]), int(step[0])] != 1: # перевіряємо чи це наша ціль
                        if step not in visited: # якщо не ціль і не відвідано
                            queue.append(step) # то додаємо крок до черги
                            path.append({"Current": current, "Next": step}) # додаємо у шлях
        # шукаємо найкоротший шлях
        shortest = [target] # присвоюємо цільові значення змінній
        while target != start: # поки ціль не дорівнює початку
            for step in path: # для кожного кроку в отриманому нами раніше шляху
                if step["Next"] == target: # якщо наступний крок -ціль
                    target = step["Current"] # ставимо ціль нинішнім кроком
                    shortest.insert(0, step["Current"]) # зберігаємо цю коротку дорогу у списку

        return shortest


    def get_DFS(self, start, target):
        grid = self.load_grid()
        if not self.is_valid_target(target):
            print("Wrong target")
            return [start]

        stack = [start]
        visited = []
        path = []
        directions = [[1, 0], [0, -1], [-1, 0], [0, 1]]
        while stack: # поки в нас є записи в стеку
            possible_dirs = []
            for direction in directions: # ми проходимося по всіма сторонам
                step = stack[-1] + direction # робимо крок = останній елемент стеку + вектор напрямку
                if grid[int(step[1]), int(step[0])] != 1 and step not in visited: # якщо на місці цього кроку немає
                    # нашого target, тоді додаємо вектор напрямку цього кроку у можливі шляхи
                    possible_dirs.append(direction)

            if len(possible_dirs) == 0:
                stack.pop()
                path = stack

            for direction in possible_dirs: # проходимось по можливим обраним напрямкам
                step2 = stack[-1] + direction
                stack.append(step2) # додаємо в стек новий крок для пошуку шляху вже по ньому
                visited.append(stack[-1])
                path.append(stack[-1])
                break

            if stack[-1] == target:
                return path


    def get_UCS(self, start, target):
        grid = self.load_grid()
        if not self.is_valid_target(target):
            print("Wrong target")
            return [start]
        graph = self.grid_to_graph(grid)
        visited = set()
        start = (int(start.y), int(start.x))
        target = (int(target.y), int(target.x))
        path = []
        q = queue.PriorityQueue()
        q.put((0, start))

        while not q.empty():
            cost, node = q.get()
            if node == target:
                path.append(node)
                return path

            for edge in graph[node]:
                if edge not in visited:
                    visited.add(edge)
                    next_node = edge[:2]
                    step_cost = edge[-1]
                    q.put((step_cost + cost, next_node))
            path.append(q.queue[0][1][::-1])




    def grid_to_graph(self, grid):
        cost = 1
        rows, cols = grid.shape
        graph = {}
        for i in range(rows-1):
            for j in range(cols-1):
                if grid[i, j] != 1:
                    adj = []
                    for ele in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                        if grid[ele[0], ele[1]] == 0:
                            adj.append((ele[0], ele[1], cost))
                    graph[(i, j)] = adj
        return graph

    def draw_path(self):
        for step in self.path[1:-1]:
            pygame.draw.rect(self.app.screen, 'pink', (step[0] * self.app.cell_width + 50//2,
                                                             step[1] * self.app.cell_height + 50//2,
                                                             self.app.cell_width,
                                                             self.app.cell_height))


    def load_grid(self):
        grid = np.zeros((ROWS+1, COLS), dtype=int)
        with open("map.txt", "r") as file:
            for y, line in enumerate(file):
                for x, char in enumerate(line[:-1]):
                    if char == "1":
                        grid[y, x] = 1
                    else:
                        grid[y, x] = 0
        return grid

    def is_valid_target(self, target):
        grid = self.load_grid()
        if grid[int(target.y), int(target.x)] == 1:
            return False
        else:
            return True

class RandomEnemy(Enemy):
    def __init__(self, app, pos, number):
        super().__init__(app,pos,number)
    # random path
    def go(self):
        directions = [[0, -1], [1, 0], [0, 1], [-1, 0]]