from Index.RTree import format_mbr
import multiprocessing, psutil
from tqdm import tqdm
import statistics, os, time

def measure_memory():
    process = psutil.Process()
    current_memory = process.memory_info().data / (1024 * 1024)
    return current_memory

def generate_result_file_path(args, file_type, file_dir="./Result/TrajectoryVisualization/"):
    file_path = file_dir 
    file_path += args.dataset + "_" + args.day + "_" + args.measure + \
        "_targetShip_" + str(args.ship_target_id)
    file_path += file_type 
    return file_path

def calculate_mbr_area(positions):
    """Calculate the minimum bounding rectangle (MBR) area for a given list of positions."""
    if len(positions) == 1:
        return 0
    x_coords, y_coords = zip(*positions)
    latitudes_min, latitudes_max, longitudes_min, longitudes_max = min(x_coords), max(x_coords), min(y_coords), max(y_coords) 
    # Return the MBR boundaries
    mbr = format_mbr((latitudes_min, longitudes_min, latitudes_max, longitudes_max))
    return mbr, abs(latitudes_min-latitudes_max) * abs(longitudes_min - longitudes_max)

def baselines_candidate_process(candidate_traj):
    def merge_intervals(intervals):
        intervals.sort(key=lambda x: x[0])
        merged = []
        for interval in intervals:
            if not merged or merged[-1][1] < interval[0] - 1:
                merged.append(interval)
            else:
                merged[-1][1] = max(merged[-1][1], interval[1])
        return merged
    for ship_id in candidate_traj:
        candidate_traj[ship_id] = merge_intervals(candidate_traj[ship_id])
        # print("candidate_traj", candidate_traj[ship_id])
    return candidate_traj

#region Segment Generate Module
def SegmentGenerate(positions, minlen_seq, maxlen_seq):
    n = len(positions)
    if (minlen_seq > n):
        minlen_seq = n
    if (maxlen_seq > n):
        maxlen_seq = n
    F = [float('inf')] * (n + 1)  # DP array to store minimum MBR areas
    F[0] = 0
    segments = [[] for _ in range(n + 1)]  # To store segments that give the optimal solution

    record_pos = {}
    for i in range(1, n + 1):
        for k in range(minlen_seq, min(maxlen_seq + 1, n+1)):
            if i - k >= 0:
                # print(i-k, i, positions[i-k:i])
                mbr, mbr_area = calculate_mbr_area(positions[i-k:i])
                if F[i] > F[i-k] + mbr_area:
                    F[i] = F[i-k] + mbr_area
                    segments[i] = segments[i-k] + [[i-k, i-1, mbr]]

    return segments[n], F[n]

def process_single_trajectory(args):
    traj_id, data, minlen_seq, maxlen_seq = args
    segment_list, _ = SegmentGenerate(
        data['positions_list'], 
        minlen_seq=minlen_seq, 
        maxlen_seq=maxlen_seq
    )
    return traj_id, segment_list

def split_segment_from_traj_data(traj_data, args):
    if args.index_type in ['SVTI', 'DFT']:
        print("Generating segments for each trajectory")
        
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        
        process_args = [
            (traj_id, data, args.lm, args.ln)
            for traj_id, data in traj_data.items()
        ]
        
        results = list(tqdm(
            pool.imap(process_single_trajectory, process_args),
            total=len(process_args),
            desc="Processing ships"
        ))
        
        pool.close()
        pool.join()
        
        for traj_id, segment_list in results:
            traj_data[traj_id]['segment_list'] = segment_list
    
    return traj_data

def hyperparameter_Segment(parser):
    # Trajectory Segment Module of STSM (Strategy One Part A)
    # Setting 1: minlen_seq: 20, 25, 30, 35, 40 / maxlen_seq: 40, 45, 50, 55, 60
    # Setting 2: minlen_seq: 30, 30, 30, 30, 30 / maxlen_seq: 40, 45, 50, 55, 60
    parser.add_argument("--lm", type=int, default=30)
    parser.add_argument("--ln", type=int, default=50)
    return parser
#endregion

#region Model Wrapper
def model_wrapper(args):
    if (args.model_type == "custom"):
        return args 

    if (args.model_type == "ACTIVE"):
        args.measure_type = "OTRD"
        args.index_type = "SVTI"
        return args 

def hyperparameter_Model(parser):
    parser.add_argument("--model_type", type=str, default="ACTIVE",choices=["ACTIVE", "custom"]) 
    return parser
#endregion