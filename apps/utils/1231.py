from collections import defaultdict
from heapq import *

# 2
# 4
# 5 9 4 7
# 8
# 9 13 18 10 12 4 18 3


def myfun(alist):
    wei = [0]+alist
    bag = sum(alist)//2+2
    mylist= [[0 for y in range(bag)] for x in range(len(wei))]
    for i in range(1,len(wei)):
        for j in range(1,bag):
            if wei[i]<=j:
                mylist[i][j]=max(mylist[i-1][j],wei[i]+mylist[i-1][j-wei[i]])
            else:
                mylist[i][j]=mylist[i-1][j]
    anslist =  sorted([mylist[-1][-1],sum(alist)-mylist[-1][-1]])
    return ' '.join([str(item) for item in anslist])

import sys
test_time = int(input())
input_list=[]
for line in sys.stdin:
    if line !='\n':
        input_list.append([int(item) for item in line.strip().split(' ')])
    else:
        break
# print(input_list)
ans_result=[]
for i in range(1,len(input_list),2):
    test_list = input_list[i]
    res = myfun(test_list)
    print(res)



# first = input().split(' ')
# alist = [int(item) for item in input().split(' ')]
# n = int(first[0])
# k = int(first[1])
# mylist = []
# for item in alist:
#     if item !=0:
#         mylist.append(item)
#
# for i in range(k):
#     minnum = min(mylist)
#     print(minnum)
#     mylist=list(map(lambda x:x-minnum,mylist))
#     while 0 in mylist:
#         mylist.remove(0)

# mylist = [0,0,0,1]
# while 0 in mylist:
#     mylist.remove(0)
# print(mylist)
# print(myfun([9,13,18,10,12,4,18,3]))


# def dijkstra_raw(edges, from_node, to_node):
#     g = defaultdict(list)
#     for l, r, c in edges:
#         g[l].append((c, r))
#     q, seen = [(0, from_node, ())], set()
#     while q:
#         (cost, v1, path) = heappop(q)
#         if v1 not in seen:
#             seen.add(v1)
#             path = (v1, path)
#             if v1 == to_node:
#                 return cost, path
#             for c, v2 in g.get(v1, ()):
#                 if v2 not in seen:
#                     heappush(q, (cost + c, v2, path))
#     return float("inf"), []
#
#
# def dijkstra(edges, from_node, to_node):
#     len_shortest_path = -1
#     ret_path = []
#     length, path_queue = dijkstra_raw(edges, from_node, to_node)
#     if len(path_queue) > 0:
#         len_shortest_path = length  ## 1. Get the length firstly;
#         ## 2. Decompose the path_queue, to get the passing nodes in the shortest path.
#         left = path_queue[0]
#         ret_path.append(left)  ## 2.1 Record the destination node firstly;
#         right = path_queue[1]
#         while len(right) > 0:
#             left = right[0]
#             ret_path.append(left)  ## 2.2 Record other nodes, till the source-node.
#             right = right[1]
#         ret_path.reverse()  ## 3. Reverse the list finally, to make it be normal sequence.
#     return len_shortest_path, ret_path
#
#
# ### ==================== Given a list of nodes in the topology shown in Fig. 1.
# list_nodes_id = [0, 1, 2, 3, 4, 5];
# ### ==================== Given constants matrix of topology.
# M = 99999  # This represents a large distance. It means that there is no link.
# ### M_topo is the 2-dimensional adjacent matrix used to represent a topology.
# M_topo = [
#     [M, 12, M, M, M, M],
#     [M, M, 10, M, M, 7],
#     [M, M, M, 3, 5, 6],
#     [M, M, M, M, 4, M],
#     [M, M, M, M, M, 2],
#     [16, M, M, M, M, M],
#
# ]
#
# ### --- Read the topology, and generate all edges in the given topology.
# edges = []
# for i in range(len(M_topo)):
#     for j in range(len(M_topo[0])):
#         if i != j and M_topo[i][j] != M:
#             edges.append((i, j, M_topo[i][j]))  ### (i,j) is a link; M_topo[i][j] here is 1, the length of link (i,j).
# #print ("=== Dijkstra ===")
# #print ("Let's find the shortest-path from 0 to 9:")
#
# i=input()
# j=input()
# r={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5}
# u = r[i]
# v = r[j]
# length,Shortest_path = dijkstra(edges,u,v)
# print ('length = ',length)
# print ('The shortest path is ',Shortest_path)

# # Hello World program in Python
# # coding=utf-8
# import random
# def test_input():
#     arr = [-3000]
#     for i in range(1000):
#         n = random.randint(-10, 20)
#         if n < 0:
#             n -= 100
#         elif n > 0:
#             n += 100
#         else:
#             continue
#         arr.append(n)
#     return arr
# arr = test_input()
# # 求和
# def sum(a):
#     s = 0
#     for i in a:
#         s += i
#     return s
# # 分离数组
# def split_array(arr):
#     # 获取数组并排序
#     a = list(arr)
#     #a.sort()
#     # 另一个数组
#     b = list()
#     # 以上a,b作为待返回的数组
#     # 计算数组大小
#     n = len(a)#1000
#     #求和
#     smr = sum(a)
#     # 和的一半,简称半和
#     hs = smr / 2
#     # 临时和
#     s = 0
#    # 从最大的数字开始遍历数组
#     for i in range(-1,0-n,-1):
#         # 预判该数字加和结果
#
#         ns = s + a[i]
#         if ns > hs:
#             # 如果超出半和则跳过
#             continue
#         else:
#             # 如果未超过半和,则:
#             # 1, 取该元素加和
#             s += a[i]
#             # 2, 从 a 中将元素转移到 b
#             b.append(a[i])
#             a.pop(i)
#             # 如果最终和与半和之差,不够最小元素,则完成
#             if abs(s - hs) <= a[-1]:
#                 break
#     return a, b
#
# split_array


