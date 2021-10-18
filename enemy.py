import queue
import random
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
        print("START ", self.starting_pos)
        self.pix_pos = self.get_xy()
        self.radius = int(self.app.cell_width // 2.3)
        self.number = number
        self.direction = vec(1, 0)
        self.target = None
        self.speed = 2
        self.path = None

    def can_move(self):
        for wall in self.app.walls:
            if vec(self.field_xy + self.direction) == wall:
                return False
        return True

    def update(self):
        if self.path is not None:
            pass

        self.field_xy[0] = (self.pix_pos[0] - BORDER_FIELD +
                            self.app.cell_width // 2) // self.app.cell_width + 1
        self.field_xy[1] = (self.pix_pos[1] - BORDER_FIELD +
                            self.app.cell_height // 2) // self.app.cell_height + 1

    def draw(self):
        self.pacman = pygame.transform.scale(pygame.image.load('images/ghost.png'), (self.app.cell_width,
                                                                                     self.app.cell_height))
        if (self.direction == vec(-1, 0)):
            self.pacman = pygame.transform.flip(self.pacman, True, False)

        self.app.screen.blit(self.pacman, (int(self.pix_pos.x - 15), int(self.pix_pos.y - 15)))

    def get_xy(self):
        return vec((self.field_xy.x * self.app.cell_width) + BORDER_FIELD // 2 + self.app.cell_width // 2,
                   (self.field_xy.y * self.app.cell_height) + BORDER_FIELD // 2 +
                   self.app.cell_height // 2)

    def get_BFS(self, start, target):  # пошаровий пошук (в ширину)
        grid = self.load_grid()

        if not self.is_valid_target(target):
            print("Wrong target")
            return [start]

        queue = [start]  # реалізовуємо через чергу
        path = []
        visited = []
        directions = [[0, -1], [1, 0], [0, 1], [-1, 0]]  # вказуємо можливі напрямки

        while queue:  # поки в нас є черга (не пуста)
            current = queue[0]  # заходимо у перший елемент, позначаємо як теперішній і прибираємо з черги
            queue.remove(queue[0])
            visited.append(current)  # помічаємо як відвіданий
            if current == target:
                break
            else:
                for direction in directions:  # для усіх напрямків
                    step = current + direction  # робимо крок у обраному напрямку
                    if grid[int(step[1]), int(step[0])] != 1:  # перевіряємо чи це наша ціль
                        if step not in visited:  # якщо не ціль і не відвідано
                            queue.append(step)  # то додаємо крок до черги
                            path.append({"Current": current, "Next": step})  # додаємо у шлях
        # шукаємо найкоротший шлях
        shortest = [target]  # присвоюємо цільові значення змінній
        while target != start:  # поки ціль не дорівнює початку
            for step in path:  # для кожного кроку в отриманому нами раніше шляху
                if step["Next"] == target:  # якщо наступний крок -ціль
                    target = step["Current"]  # ставимо ціль нинішнім кроком
                    shortest.insert(0, step["Current"])  # зберігаємо цю коротку дорогу у списку

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
        while stack:  # поки в нас є записи в стеку
            possible_dirs = []
            for direction in directions:  # ми проходимося по всіма сторонам
                step = stack[-1] + direction  # робимо крок = останній елемент стеку + вектор напрямку
                if grid[int(step[1]), int(step[0])] != 1 and step not in visited:  # якщо на місці цього кроку немає
                    # нашого target, тоді додаємо вектор напрямку цього кроку у можливі шляхи
                    possible_dirs.append(direction)

            if len(possible_dirs) == 0:
                stack.pop()
                path = stack

            for direction in possible_dirs:  # проходимось по можливим обраним напрямкам
                step2 = stack[-1] + direction
                stack.append(step2)  # додаємо в стек новий крок для пошуку шляху вже по ньому
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
        for i in range(rows - 1):
            for j in range(cols - 1):
                if grid[i, j] != 1:
                    adj = []
                    for ele in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                        if grid[ele[0], ele[1]] == 0:
                            adj.append((ele[0], ele[1], cost))
                    graph[(i, j)] = adj
        return graph

    def draw_path(self):
        for step in self.path[1:-1]:
            pygame.draw.rect(self.app.screen, 'pink', (step[0] * self.app.cell_width + 50 // 2,
                                                       step[1] * self.app.cell_height + 50 // 2,
                                                       self.app.cell_width,
                                                       self.app.cell_height))

    def load_grid(self):
        grid = np.zeros((ROWS + 1, COLS), dtype=int)

        y = 0
        for line in self.app.map:
            y = y + 1
            x = 0
            for char in line:
                x = x + 1
                if char == 0:
                    grid[y, x] = 1
                else:
                    grid[y, x] = 0
        return grid

    def is_valid_target(self, target):
        grid = self.load_grid()
        if grid[int(target[1]), int(target[0])] == 1:
            return False
        else:
            return True


class RandomEnemy(Enemy):
    def __init__(self, app, pos, number):
        super().__init__(app, pos, number)

    def can_move_to_field(self, direction):
        for wall in self.app.walls:
            if (self.field_xy + direction) == wall:
                return False
        return True


    def to_field_xy(self):
        return [(self.pix_pos[0] - BORDER_FIELD + self.app.cell_width // 2) // self.app.cell_width + 1,
                (self.pix_pos[1] - BORDER_FIELD + self.app.cell_height // 2) // self.app.cell_height + 1]


    # random path
    def update(self):
        directions = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        can_move = self.can_move()
        if can_move:
            condit1 = self.can_move_to_field([self.direction[1], self.direction[0]])
            condit2 = self.can_move_to_field([-self.direction[1], -self.direction[0]])
            if(condit1 or condit2):
                can_move = False
            else:
                self.field_xy += vec(self.direction)
                self.pix_pos = self.get_xy()

        if not can_move:
            new_dirs = []
            for d in directions:
                if self.can_move_to_field(d):
                    new_dirs.append(d)
            print(new_dirs)

            self.direction = random.choice(new_dirs)
            self.field_xy += vec(self.direction)
            self.pix_pos = self.get_xy()


class TargetEnemy(Enemy):
    def __init__(self, app, pos, number):
        super().__init__(app, pos, number)

    def can_move_to_field(self, direction):
        for wall in self.app.walls:
            if (self.field_xy + direction) == wall:
                return False
        return True

    def to_field_xy(self):
        return [(self.pix_pos[0] - BORDER_FIELD + self.app.cell_width // 2) // self.app.cell_width + 1,
                (self.pix_pos[1] - BORDER_FIELD + self.app.cell_height // 2) // self.app.cell_height + 1]

    # path by algorithm from prev laba
    def update(self):
        self.path = self.get_BFS(self.field_xy, self.app.player.field_xy)
        if len(self.path) != 0:
            self.field_xy = self.path[1]
            self.pix_pos = self.get_xy()
