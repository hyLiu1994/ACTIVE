import numpy as np
from Measure.utils import haversine

def frechet_distance(seq1, seq2):
    if (len(seq1)==0 or len(seq2) == 0):
        return 1e9

    len_seq1, len_seq2 = len(seq1), len(seq2)
    dp = np.full((len_seq1, len_seq2), float('inf'))

    dp[0, 0] = haversine(seq1[0], seq2[0])

    for i in range(1, len_seq1):
        dp[i, 0] = max(dp[i - 1, 0], haversine(seq1[i], seq2[0]))

    for j in range(1, len_seq2):
        dp[0, j] = max(dp[0, j - 1], haversine(seq1[0], seq2[j]))

    for i in range(1, len_seq1):
        for j in range(1, len_seq2):
            min_previous = min(dp[i - 1, j], dp[i, j - 1], dp[i - 1, j - 1])
            dp[i, j] = max(min_previous, haversine(seq1[i], seq2[j]))

    return dp[len_seq1 - 1, len_seq2 - 1]


if __name__ == "__main__":
    A = np.array([(1,1), (2,2)])
    B = np.array([(1,2), (2,3), (3,4)])
    print("Fréchet distance:", frechet_distance(A, B))
