import sys
sys.path.append("/nfs/srv/data2/hengyu/MobiSpace/")
import numpy as np
from Measure.utils import haversine
import math

def calculate_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def point_to_mbr_distance(point, mbr):
    lat, lon = point
    min_lat, min_lon, max_lat, max_lon = mbr

    clamped_lat = max(min_lat, min(max_lat, lat))
    clamped_lon = max(min_lon, min(max_lon, lon))

    distance = ((lat - clamped_lat) ** 2 + (lon - clamped_lon) ** 2) ** 0.5
    return distance

def point_to_line_distance(point, line_start, line_end):
    vector_line = np.array(line_end) - np.array(line_start)
    vector_point = np.array(point) - np.array(line_start)
    
    t = np.dot(vector_point, vector_line) / (np.linalg.norm(vector_line) ** 2 + 1e-9)
    
    if t < 0:
        return np.linalg.norm(vector_point)  
    elif t > 1:
        return np.linalg.norm(np.array(point) - np.array(line_end))  
    else:
        projection = vector_line * t
        return np.linalg.norm(vector_point - projection)  

def OTRD(seqPQ, seqPTInf, topKValue, traj_data, args, OTRD_knowledge):

    #region 0: Initialize Parameters
    alpha = args.alpha
    theta = args.theta
    gran = args.gran
    seqPT_idx = seqPTInf[0]
    if (seqPT_idx not in OTRD_knowledge['backup_knowledge'].keys()):
        OTRD_knowledge['backup_knowledge'][seqPT_idx] = [0, 0]
    maxValue, readySeqLen = OTRD_knowledge['backup_knowledge'][seqPT_idx]
    seqPQLen = len(seqPQ)
    #endregion

    #region 1: Calculate distance_T
    seqPQ_end = OTRD_knowledge['destination_pos']  
    current_segment_end = traj_data[seqPT_idx]['positions_list'][traj_data[seqPT_idx]['segment_list'][seqPTInf[1][1]][1]]
    seqPT_end = traj_data[seqPT_idx]['positions_list'][-1]

    endpoint_distance = point_to_line_distance(
        seqPQ_end,
        current_segment_end,
        seqPT_end
    )
    #endregion

    #region 2: Calculate distance_H
    for idx in range(readySeqLen, seqPQLen):
        current_pos = seqPQ[idx]
        seqPQ_distance = 1e9
        for seqIdx in range(seqPTInf[1][0], seqPTInf[1][1]+1):
            p_mbr_distance = point_to_mbr_distance(seqPQ[0], traj_data[seqPT_idx]['segment_list'][seqIdx][2])
            if (seqPQ_distance > p_mbr_distance):
                p_p_distance = 0
                for pIndx in range(traj_data[seqPT_idx]['segment_list'][seqIdx][1], traj_data[seqPT_idx]['segment_list'][seqIdx][0]-1, -gran):
                    p_p_distance = calculate_distance(current_pos, traj_data[seqPT_idx]['positions_list'][pIndx])
                    seqPQ_distance = min(seqPQ_distance, p_p_distance * math.pow(theta, len(seqPQ) - pIndx - 1))

        maxValue = max(maxValue * theta, seqPQ_distance)

        if (maxValue * math.pow(theta, seqPQLen - idx - 1) >= topKValue):
            OTRD_knowledge['backup_knowledge'][seqPT_idx] = [maxValue, idx + 1]
            return maxValue * math.pow(theta, seqPQLen - idx - 1)
    #endregion

    #region 3: Update maxValue and readySeqLen
    OTRD_knowledge['backup_knowledge'][seqPT_idx] = [maxValue, seqPQLen]
    maxValue = maxValue * alpha + endpoint_distance * (1 - alpha)
    #endregion

    return maxValue

if __name__ == "__main__":
    pass
