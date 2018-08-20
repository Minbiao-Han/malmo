import sys
import search

my_BFS_blocks = 60
my_BFS_path = [(3, 11), (3, 12), (3, 13), (4, 13), (5, 13), (5, 12), (6, 12), (7, 12), (7, 11), (7, 10), (8, 10), (8, 9), (8, 8), (8, 7), (8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1)]

my_DFS_blocks = 60
my_DFS_path = [(3, 11), (3, 12), (3, 13), (4, 13), (5, 13), (5, 12), (6, 12), (7, 12), (7, 11), (7, 10), (8, 10), (8, 9), (8, 8), (8, 7), (8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1)]

my_aStar_blocks = 60
my_aStar_path = [(3, 11), (3, 12), (3, 13), (4, 13), (5, 13), (5, 12), (6, 12), (7, 12), (7, 11), (7, 10), (8, 10), (8, 9), (8, 8), (8, 7), (8, 6), (8, 5), (8, 4), (8, 3), (8, 2), (8, 1)]

score = 0

print(search.pathA, search.blocksA)

if search.pathB == my_BFS_path and search.blocksB == my_BFS_blocks:
    score += 30
if search.pathD == my_DFS_path and search.blocksD == my_DFS_blocks:
    score += 30
if search.pathA == my_aStar_path and search.blocksA == my_aStar_blocks:
    score += 40

print('The final score of this student is:', score)