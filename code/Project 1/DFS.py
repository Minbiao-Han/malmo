from collections import deque


def search(maze, start, end):

    queue = deque([start])
    visited = set()

    while len(queue) != 0:
        if queue[0] == start:
            path = [queue.pop()]  # Required due to a quirk with tuples in Python
        else:
            path = queue.pop()
        front = path[-1]
        if front == end:
            return path
        elif front not in visited:
            for adjacentSpace in getAdjacentSpaces(maze, front, visited):
                newPath = list(path)
                newPath.append(adjacentSpace)
                queue.append(newPath)
            visited.add(front)
    return None


def getAdjacentSpaces(maze, space, visited):
    spaces = list()
    spaces.append((space[0]-1, space[1]))  # Up
    spaces.append((space[0]+1, space[1]))  # Down
    spaces.append((space[0], space[1]-1))  # Left
    spaces.append((space[0], space[1]+1))  # Right

    final = list()
    for i in spaces:
        if maze[i[0]][i[1]] != '%' and i not in visited:
            final.append(i)
    return final