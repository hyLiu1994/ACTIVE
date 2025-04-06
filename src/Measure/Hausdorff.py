import numpy as np
from Measure.utils import haversine

def hausdorff_distance(A, B, topKValue = 1e9):
    if (len(A) == 0 or len(B) == 0):
        return 1e9 

    hausdorff_AB = 0
    for a in A:
        min_dist = float('inf')
        for b in B:
            dist = haversine(a, b)
            min_dist = min(min_dist, dist)
        hausdorff_AB = max(hausdorff_AB, min_dist)
        if hausdorff_AB >= topKValue: 
            return hausdorff_AB
    
    hausdorff_BA = 0
    for b in B:
        min_dist = float('inf')
        for a in A:
            dist = haversine(b, a)
            min_dist = min(min_dist, dist)
        hausdorff_BA = max(hausdorff_BA, min_dist)
        if hausdorff_BA >= topKValue:  
            return hausdorff_BA
    
    return max(hausdorff_AB, hausdorff_BA)

if __name__ == "__main__":
    A = np.array([(1, 1), (2, 2), (3, 3)])
    B = np.array([(2, 1), (3, 2), (4, 4)])
    print("Hausdorff distance:", hausdorff_distance(A, B))
