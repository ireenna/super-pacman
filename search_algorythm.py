import numpy as np

from settings import *

def maze_to_grid(map):
    grid = np.full_like(np.zeros((ROWS-1, COLS-1)), fill_value=1, dtype=int)
    for i in range(ROWS-1):
        for j in range(COLS-1):
            grid[i, j] = map[i][j]
    return grid

# A* - покращення Дейкстри
def AlgStar(maze, start, end, func, coins):
    openList = [] # відомі вершини: вже відомий (можливо не оптимальний) шлях до цих вершин
    closedList = [] # повністю досліджені вершини - вже відомий найкоротший шлях до цих вершин
    # (аби запобігти багаторазовому дослідженню вже досліджених вершин)

    # задаємо початкові та кінцеві вузли
    node_start = Node(None, start)
    node_finish = Node(None, end)
    # задаємо ціну = 1
    node_start.cost = maze[start]
    node_finish.cost = maze[end]
    openList.append(node_start)

    while openList:
        node_curr = openList[0]
        temp_index = 0
        # достаємо вершину із меншим значенням cost із відкритого списку
        for index, node in enumerate(openList):
            if node.cost_all < node_curr.cost_all:
                node_curr = node
                temp_index = index

        openList.pop(temp_index)
        closedList.append(node_curr)

        # якщо ми дійшли до кінця
        if node_curr == node_finish:
            path = []
            temp = node_curr
            # йдемо назад по вказівкам
            while temp is not None:
                path.append(temp.pos_xy)
                temp = temp.parent
            return list(reversed(path))

        # Якщо кінцева вершина не досягнута: додати суміжні до поточної вершини в openList
        child = []
        for direction in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            next_pos = (node_curr.pos_xy[0] + direction[0],
                        node_curr.pos_xy[1] + direction[1])

            if next_pos[0] > maze.shape[0] - 1 | next_pos[0] < 0 | next_pos[1] > maze.shape[1] - 1 | next_pos[1] < 0:
                continue

            if maze[next_pos] == 0:
                continue

            new_node = Node(node_curr, next_pos)
            child.append(new_node)

        for child in child:
            if child in closedList:
                continue
            # вказуємо ціну для дітей
            child.cost = maze[child.pos_xy]
            child.heuristic = func(child.pos_xy, node_finish.pos_xy, coins)
            child.cost_all = child.cost + child.heuristic

            for open_node in openList:
                if child == open_node and child.cost > open_node.cost:
                    continue
            openList.append(child)


def manhattan_h(a, b,c):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclid_h(a, b,c):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def greed_h(a,b,c):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

class Node:
    def __init__(self, parent=None, position=None):
        self.heuristic = 0
        self.parent = parent
        self.pos_xy = position
        self.cost = 0
        self.cost_all = 0

    def __eq__(self, other):
        return self.pos_xy == other.pos_xy


