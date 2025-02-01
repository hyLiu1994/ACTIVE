from Index.TrajIndex import TrajIndex
from Index.SVTI import SVTI
from utils.utils import measure_memory
from tqdm import tqdm
import time, sys

def build_SVTI(ship_data, args):
    Index = SVTI(M = 100)
    for i in tqdm(ship_data.keys(), desc="Insert Traj"):
        for j in range(len(ship_data[i]['segment_list'])):
            Index.insert(((i,j), ship_data[i]['segment_list'][j][-1]))
    return Index

def build_PQT(ship_data, args):
    print("Begin Build PQT! ----------------------------------------------------------------")
    start_time = time.time()
    TrajTree = TrajIndex(min_latitude=args.index_cell_size, dep=1)
    for i in tqdm(ship_data.keys(), desc="Insert Traj"):
        TrajTree.Add_TrajRange(i, [0, len(ship_data[i]['positions_list'])-1], ship_data[i]['positions_list'])
    print("Cost time:", time.time() - start_time)
    print("Finish Build PQT! ----------------------------------------------------------------")
    return TrajTree

def build_Index(traj_data, args):
    if (args.index_type == 'PQT'):
        TrajTree = build_PQT(traj_data, args)
    elif (args.index_type == 'SVTI'):
        TrajTree = build_SVTI(traj_data, args)
    return TrajTree

def search_knn_candidate_traj(TrajTree, current_point, traj_data, args):
    print("Step 0: Search KNN Candidate Traj!")
    mem_usage_before = measure_memory()
    start_time = time.time()
    knn_traj = []
    search_latitude = args.query_range
    while (len(knn_traj) <= args.topk):
        mem_usage_before_one_search = measure_memory()
        knn_traj = TrajTree.search_traj_list((current_point[0]-search_latitude, current_point[1]-search_latitude*2,
                                                current_point[0]+search_latitude, current_point[1]+search_latitude*2))
        # print("KNN: search_latitude", search_latitude, "candidate_num", len(knn_traj), "memory_usage", measure_memory() - mem_usage_before_one_search)
        search_latitude *= 2

    knn_traj_ids = [traj_id for traj_id in knn_traj.keys()]
    mem_usage_after = measure_memory()
    print("Cost time:", time.time() - start_time)
    print("Memory usage:", mem_usage_after - mem_usage_before, "Mb")
    return knn_traj_ids

def search_candidate_traj(TrajTree, current_point, args):
    print("Step 1:Search Candidate Traj!")
    mem_usage_before = measure_memory()
    memory_usage = 0
    start_time = time.time()
    candidate_traj = []
    search_latitude = args.query_range
    while (len(candidate_traj) <= args.topk * args.candidate_ratio):
        candidate_traj = TrajTree.search_traj_list((current_point[0]-search_latitude, current_point[1]-search_latitude*2,
                                                current_point[0]+search_latitude, current_point[1]+search_latitude*2))
        # print("search_latitude", search_latitude, "candidate_num", len(candidate_traj))
        memory_usage += sys.getsizeof(candidate_traj) / (1024 * 1024)
        search_latitude *= 2
    mem_usage_after = measure_memory()
    print("Cost time:", time.time() - start_time)
    print("Memory usage:", mem_usage_after - mem_usage_before, "Mb")
    return candidate_traj, memory_usage

def hyperparameter_Index(parser):
    parser.add_argument("--index_type", type=str, default="SVTI", choices=["PQT", "SVTI"])
    parser.add_argument("--index_cell_size", type=float, default=1e-3) # PQT
    return parser