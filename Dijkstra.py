from collections import defaultdict
from heapq import *

def dijkstra(edges, f, t):
    g = defaultdict(list)
    for l,r,c in edges:
        g[l].append((c,r))

    q, seen = [(0,f,())], set()
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == t: return (cost, path)

            for c, v2 in g.get(v1, ()):
                if v2 not in seen:
                    heappush(q, (cost+c, v2, path))

    return float("inf")

def shortestPathCalculator(graph, start, end):
    edges=[]
    for x in graph:
        for y in graph[x]:
            edges.append((x,y, graph[x][y]))

    out = dijkstra(edges, start, end)
    data = {}
    data['cost'] = out[0]
    aux=[]
    while len(out) > 1:
        aux.append(out[0])
        out = out[1]
    aux.remove(data['cost'])
    aux.reverse()
    data['path']=aux
    return data
