from collections import deque

DIMENSION = int(input())
NUM_OF_VERTICES = 2 ** DIMENSION

def getRedEdges():
    with open("red_edges.txt", "r") as file:
        red_edges = []
        for line in file:
            u, v = map(int, line.split())
            red_edges.append([u, v])
        return red_edges
    
redEdges = [[] for i in range(NUM_OF_VERTICES)]
blueEdges = [[] for i in range(NUM_OF_VERTICES)]
for u in range(NUM_OF_VERTICES):
    for d in range(DIMENSION):
        v = u ^ (1 << d)
        if [u, v] in getRedEdges() or [v, u] in getRedEdges():
            redEdges[u].append(v)
            redEdges[v].append(u)
        else:
            blueEdges[u].append(v)
            blueEdges[v].append(u)

# lets do some BFS
for start in [0, 1]:
    for color, edges in [("red", redEdges), ("blue", blueEdges)]:
        visited = [False for i in range(NUM_OF_VERTICES)]
        queue = deque()
        queue.append(start)
        visited[start] = True
        while queue:
            u = queue.popleft()
            for v in edges[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
        
        if not visited[start ^ 3]:
            print(f"Cannot reach for color {color} starting from {start}")

