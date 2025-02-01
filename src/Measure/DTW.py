import numpy as np
# from utils import haversine
from Measure.utils import haversine

def dtw(PA, PB):
    m, n = len(PA), len(PB)
    DTW = np.zeros((m+1, n+1))
    DTW[0, :] = np.inf
    DTW[:, 0] = np.inf
    DTW[0, 0] = 0

    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = haversine(PA[i-1], PB[j-1])
            DTW[i, j] = cost + min(DTW[i-1, j],    # 插入
                                   DTW[i, j-1],    # 删除
                                   DTW[i-1, j-1])  # 匹配

    return DTW[m, n]

if __name__ == "__main__":
    PA = [(1,1),(2,2),(3,3),(4,4),(5,5)]
    PB = [(2,2),(3,3),(4,4)]
    print("DTW distance:", dtw(PA, PB))
    PQ =  [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
    PT1 = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
    PT2 = [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)]
    print("DTW distance between PQ and PT1:", dtw(PQ, PT1))
    print("DTW Measure distance between PQ and PT2:", dtw(PQ, PT2))
    
'''
DTW distance: 314.2355946786747
DTW distance between PQ and PT1: 1664.1133184781454
DTW Measure distance between PQ and PT2: 1666.1459136206295
'''
