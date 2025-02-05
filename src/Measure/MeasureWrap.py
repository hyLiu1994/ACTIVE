from Measure.OTRD import OTRD
import time, heapq

#region Measure Wrapper
def distance_wrapper(shipA, shipB, distance_type = 'OTRD', currentTopKValue = 1e9, traj_data = {}, OTRD_knowledge = [], args = None):

    if (distance_type == 'OTRD'):
        return OTRD(shipA, shipB, currentTopKValue, traj_data, args, OTRD_knowledge) 
#endregion

#region Topk Traj Selection
def find_topk_traj_online(current_traj, candidate_traj_Info, traj_data, backup_knowledge, args):
    print("Measure: Find top Traj based on current position! (Online Version)")
    start_time = time.time()
    # Calculate similarity scores for each candidate trajectory
    topk_heap = []
    for traj_id, traj_info in candidate_traj_Info.items():
        if (args.model_type == 'ACTIVE'):
            traj_info = [traj_id, traj_info]
        else:
            traj_info = traj_data[traj_id]['positions_list']

        if len(topk_heap) >= args.topk:
            distance_score = distance_wrapper(current_traj, traj_info, args.measure_type, -topk_heap[0][0], traj_data, backup_knowledge, args)
        else:
            distance_score = distance_wrapper(current_traj, traj_info, args.measure_type, 1e9, traj_data, backup_knowledge, args)

        if len(topk_heap) < args.topk:
            heapq.heappush(topk_heap, (-distance_score, traj_id))
        else:
            if distance_score < -topk_heap[0][0]:
                heapq.heapreplace(topk_heap, (-distance_score, traj_id))
    
    selected_traj_ids = [traj_id for _, traj_id in sorted(topk_heap, key=lambda x: x[0])]
    print("Time taken to find topk candidate trajectories:", time.time() - start_time)
    return selected_traj_ids


def hyperparameter_Measure(parser):
    # Measure Candidates: FrechetDistance, Hausdorff, OTRD
    parser.add_argument("--measure_type", type=str, default="OTRD",choices=["FrechetDistance", "Hausdorff", "OTRD"]) 
    parser.add_argument("--alpha", type=float, default=0.95)
    parser.add_argument("--theta", type=float, default=0.95)
    parser.add_argument("--gran", type=int, default=1)
    return parser
#endregion
