import numpy as np
import os, time, statistics, gc, sys
from utils.utils import measure_memory
from utils.SaveLoadModule import save_query_statistics

from utils.SaveLoadModule import save_processed_traj_data, load_processed_traj_data, save_index, load_index, save_index_statistics
from utils.SaveLoadModule import save_experiment_results
from utils.CurrentTrajectoryProcessModule import get_current_trajectory_info
from utils.utils import split_segment_from_traj_data

# Import custom modules
from utils.HyperParameterManagementModule import load_hypermater
from utils.DataProcessModule import load_ais_dataset
from utils.utils import baselines_candidate_process
from Index.IndexWrapper import build_Index, search_candidate_traj, search_knn_candidate_traj
from Measure.MeasureWrap import find_topk_traj_offline, find_topk_traj_online

def continue_similarity_traj_search(current_trajectory_info, DataIndex, traj_data, OTRD_knowledge, args):
    raw_traj_id, current_point, current_traj, current_target, next_point = current_trajectory_info
    
    #region Step 1: Measure search_knn time and memory, and initialize 
    knn_start_time = time.time()
    knn_start_memory = measure_memory()
    ground_true_traj_ids = search_knn_candidate_traj(DataIndex, next_point, traj_data, args)
    knn_time = time.time() - knn_start_time
    knn_memory = measure_memory() - knn_start_memory
    print(f"KNN Search Time: {knn_time:.2f} s")
    print(f"KNN Search Memory: {knn_memory:.2f} MB")

    hitk = 0
    query_start_time = time.time()
    query_memory = 0
    #endregion

    if args.index_type not in ['SVTI']:
        candidate_traj, memory_usage = search_candidate_traj(DataIndex, current_point, args)
        candidate_traj = baselines_candidate_process(candidate_traj)
        print(f"Number of candidate trajectories: {len(candidate_traj)}")
        
        selected_traj_ids = find_topk_traj_offline(
            current_traj, candidate_traj, traj_data, args
        )
        
    elif args.model_type == 'ACTIVE':
        candidate_traj_current, memory_usage = search_candidate_traj(DataIndex, current_point, args)
        candidate_traj_Info = {
            key: (0, end_segId)
            for key, end_segId in candidate_traj_current.items()
        }
        query_memory += memory_usage
        selected_traj_ids = find_topk_traj_online(current_traj, candidate_traj_Info, traj_data, OTRD_knowledge, args)

    query_memory += memory_usage
    if (args.model_type == 'ACTIVE'):
        query_memory += sys.getsizeof(OTRD_knowledge) / (1024 * 1024)
    
    #region Step 3: record query time and memory
    query_time = time.time() - query_start_time
    # query_memory = measure_memory() - query_start_memory 
    hitk = len([traj_id for traj_id in selected_traj_ids if traj_id in ground_true_traj_ids]) / args.topk
    print(f"Query Time: {query_time:.2f} s")
    print(f"Query Memory: {query_memory:.2f} MB")
    print(f"Hit@k: {hitk}")
    print(selected_traj_ids,'\n', ground_true_traj_ids)

    return {
        'hitk': hitk,
        'knn_time': knn_time,
        'knn_memory': knn_memory,
        'query_time': query_time,
        'query_memory': query_memory
    }
    #endregion
def run_experiment():
    #region Step 0: Prepare Data
    args = load_hypermater()
    print(args.dataset)
    (traj_data, dataset_identifier) = load_ais_dataset(args)
    print(f"Total Ship Number: {len(traj_data)}")
    #endregion

    #region Step 1: Index Building
    def load_or_build_index(args, dataset_identifier, traj_data):
        if args.index_type in ['SVTI']:
            dataset_identifier = f"{dataset_identifier}_{args.lm}_{args.ln}"
        index_identifier = f"Index_{args.index_type}_{args.index_cell_size}_{dataset_identifier}"        
        index_path = f"./Data/Index/{index_identifier}.pkl"  

        if os.path.exists(index_path):
            print(f"Loading index from {index_path}")
            start_time, start_memory = time.time(), measure_memory()
            segment_number = len(traj_data) 
            if args.index_type in ['SVTI']:
                traj_data = load_processed_traj_data(index_identifier, with_segment=True)
                segment_number = sum([len(traj_data[i]['segment_list']) for i in traj_data.keys()])
            DataIndex, IndexSize = load_index(index_identifier)

            loading_time = time.time() - start_time
            loading_memory = measure_memory() - start_memory
            
            print(f"Time Usage: {loading_time:.2f} s")
            print(f"Memory Usage: {loading_memory:.2f} MB")
            
            return DataIndex, traj_data, loading_time, loading_memory, -1, -1, IndexSize, segment_number
        
        print("Index not found, building index...")
        segment_number = len(traj_data) 
        start_time, start_memory = time.time(), measure_memory()
        
        processed_data_path = f"./Data/ProcessedData/{dataset_identifier}_with_segment.pkl"
        if os.path.exists(processed_data_path) and args.index_type in ['SVTI']:
            del traj_data
            traj_data = load_processed_traj_data(index_identifier, with_segment=True)
            split_segment_time = 0
        else:
            start_time = time.time()
            traj_data = split_segment_from_traj_data(traj_data, args)
            split_segment_time = time.time() - start_time

        if args.index_type in ['SVTI']:
            segment_number = sum([len(traj_data[i]['segment_list']) for i in traj_data.keys()])

        start_time = time.time()
        DataIndex = build_Index(traj_data=traj_data, args=args)
        build_time = time.time() - start_time
        build_memory = measure_memory() - start_memory
        
        print(f"Time Usage: {build_time:.2f} s")
        print(f"Memory Usage: {build_memory:.2f} MB")
        
        if args.index_type in ['SVTI']:
            save_processed_traj_data(index_identifier, traj_data, with_segment=True) 
        IndexSize = save_index(index_identifier, DataIndex)
        save_index_statistics(args.exp_name, index_identifier, build_time, build_memory, split_segment_time, IndexSize, segment_number)
        
        return DataIndex, traj_data, -1, -1, build_time, build_memory, IndexSize, segment_number

    DataIndex, traj_data, loading_time, loading_memory, build_time, build_memory, IndexSize, segment_number = load_or_build_index(args, dataset_identifier, traj_data)
    gc.collect()
    #endregion

    #region Step 2: Continue Query
    query_times = []
    query_memories = []
    knn_times = []
    knn_memories = []
    hitk = []
    for pos_idx in range(args.query_traj_num):
        # backup_knowledge = {'destination': [maxValue, readyLen], 'backup_knowledge': {raw_id: [maxValue, readyLen]}}
        OTRD_knowledge = {
            'current_pos': (0, 0),
            'destination_pos': (0, 0), 
            'backup_knowledge': {}
        }
        for timestamp in range(args.continuous_length):
            current_trajectory_info = get_current_trajectory_info(pos_idx, timestamp, traj_data, args)
            OTRD_knowledge['current_pos'] = current_trajectory_info[1]
            OTRD_knowledge['destination_pos'] = current_trajectory_info[3]
            metrics = continue_similarity_traj_search(current_trajectory_info, DataIndex, traj_data, OTRD_knowledge, args)
            
            query_times.append(metrics['query_time'])
            query_memories.append(metrics['query_memory'])
            knn_times.append(metrics['knn_time'])
            knn_memories.append(metrics['knn_memory'])
            hitk.append(metrics['hitk'])
    #endregion

    #region Step 3: Print and Save Metrics
    avg_query_time = statistics.mean(query_times)
    std_query_time = statistics.stdev(query_times)
    avg_query_memory = statistics.mean(query_memories)
    std_query_memory = statistics.stdev(query_memories)
    avg_knn_time = statistics.mean(knn_times)
    std_knn_time = statistics.stdev(knn_times)
    avg_knn_memory = statistics.mean(knn_memories)
    std_knn_memory = statistics.stdev(knn_memories)
    avg_hitk = statistics.mean(hitk)
    std_hitk = statistics.stdev(hitk)
    
    exp_result = {
        'build_time': build_time,
        'build_memory': build_memory,
        'loading_time': loading_time,
        'loading_memory': loading_memory,
        'IndexSize': IndexSize,
        'segment_number': segment_number,
        'avg_query_time': avg_query_time,
        'std_query_time': std_query_time,
        'avg_query_memory': avg_query_memory,
        'std_query_memory': std_query_memory,
        'avg_knn_time': avg_knn_time,
        'std_knn_time': std_knn_time,
        'avg_knn_memory': avg_knn_memory,
        'std_knn_memory': std_knn_memory,
        'hitk': avg_hitk,
        'std_hitk': std_hitk
    }
    
    print("\n" + "="*50)
    print("EXPERIMENT RESULTS SUMMARY")
    print("="*50)
    
    print("\nIndex Performance:")
    print(f"  Build Time:     {exp_result['build_time']:.2f} s")
    print(f"  Build Memory:   {exp_result['build_memory']:.2f} MB")
    print(f"  Loading Time:   {exp_result['loading_time']:.2f} s")
    print(f"  Loading Memory: {exp_result['loading_memory']:.2f} MB")
    
    print("\nKNN Search Performance:")
    print(f"  Average Time:   {exp_result['avg_knn_time']:.2f} ± {exp_result['std_knn_time']:.2f} s")
    print(f"  Average Memory: {exp_result['avg_knn_memory']:.2f} ± {exp_result['std_knn_memory']:.2f} MB")
    
    print("\nQuery Performance:")
    print(f"  Average Time:   {exp_result['avg_query_time']:.2f} ± {exp_result['std_query_time']:.2f} s")
    print(f"  Average Memory: {exp_result['avg_query_memory']:.2f} ± {exp_result['std_query_memory']:.2f} MB")
    
    print("\nAccuracy:")
    print(f"  Hit@k:         {exp_result['hitk']:.4f} ± {exp_result['std_hitk']:.4f}")
    print("\n" + "="*50 + "\n")
    
    model_name = args.model_type + "_" + str(args.query_length) + "_" + str(args.candidate_ratio) + "_" + str(args.topk) + "_" + str(args.future_length)
    if args.model_type == 'ACTIVE':
        model_name += "_" + str(args.alpha) + "_" + str(args.theta) + "_" + str(args.gran) + "_" + str(args.datascalability)
    save_query_statistics(args.exp_name, model_name, avg_query_time, avg_query_memory, avg_hitk)
    save_experiment_results(vars(args), exp_result, args.exp_name)
    #endregion

if __name__ == '__main__':
    run_experiment()
