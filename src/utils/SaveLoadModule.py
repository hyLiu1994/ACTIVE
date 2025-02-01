import pickle, os, os.path, csv, json
from datetime import datetime

def get_index_size_mb(index_path):
    if not os.path.exists(index_path):
        return 0
    size_bytes = os.path.getsize(index_path)
    size_mb = size_bytes / (1024 * 1024)  # 转换为 MB
    return size_mb

def validate_trajectory_mbrs(traj_data):
    validation_errors = []
    
    for traj_id, traj in traj_data.items():
        if 'traj_mbr' not in traj or 'segment_list' not in traj:
            continue
            
        traj_mbr = traj['traj_mbr']  # [min_lat, min_lon, max_lat, max_lon]
        
        for seg_idx, segment in enumerate(traj['segment_list']):
            seg_mbr = segment[2]  # segment[2] contains the MBR
            
            # Check if segment MBR is contained within trajectory MBR
            if not (traj_mbr[0] <= seg_mbr[0] and  # min_lat
                   traj_mbr[1] <= seg_mbr[1] and  # min_lon
                   traj_mbr[2] >= seg_mbr[2] and  # max_lat
                   traj_mbr[3] >= seg_mbr[3]):    # max_lon
                validation_errors.append({
                    'traj_id': traj_id,
                    'segment_idx': seg_idx,
                    'traj_mbr': traj_mbr,
                    'segment_mbr': seg_mbr
                })
    
    if validation_errors:
        print(f"Found {len(validation_errors)} validation errors:")
        for error in validation_errors:
            print(f"\nTrajectory {error['traj_id']}, Segment {error['segment_idx']}:")
            print(f"Trajectory MBR: {error['traj_mbr']}")
            print(f"Segment MBR: {error['segment_mbr']}")
        return False
    
    print("All trajectory MBRs correctly contain their segment MBRs")
    return True

def save_processed_traj_data(dataset_identifier, traj_data, with_segment=False):
    if with_segment:
        processed_data_path = f"./Data/ProcessedData/{dataset_identifier}_with_segment.pkl"
    else:
        processed_data_path = f"./Data/ProcessedData/{dataset_identifier}.pkl"
    print(f"Saving processed trajectory data to {processed_data_path}")
    with open(processed_data_path, 'wb') as f:
        pickle.dump(traj_data, f)
    print("Processed trajectory data saved successfully.")

def load_processed_traj_data(dataset_identifier, with_segment=False):
    if with_segment:
        processed_data_path = f"./Data/ProcessedData/{dataset_identifier}_with_segment.pkl"
    else:
        processed_data_path = f"./Data/ProcessedData/{dataset_identifier}.pkl"
    print(f"Loading processed trajectory data from {processed_data_path}")
    with open(processed_data_path, 'rb') as f:
        traj_data = pickle.load(f)
        validate_trajectory_mbrs(traj_data)
        return traj_data

def save_index(index_identifier, index_data):
    index_path = f"./Data/Index/{index_identifier}.pkl"
    if not os.path.exists(f'./Data/Index/'):
        os.makedirs(f'./Data/Index/')
    with open(index_path, 'wb') as f:
        pickle.dump(index_data, f)
    print(f"Index saved to {index_path}")
    return get_index_size_mb(index_path)

def load_index(index_identifier):
    index_path = f"./Data/Index/{index_identifier}.pkl"
    with open(index_path, 'rb') as f:
        return pickle.load(f), get_index_size_mb(index_path)

def save_index_statistics(exp_name, index_identifier, build_time, build_memory, split_segment_time, IndexSize, segment_number):
    output_csv = "./Result/" + exp_name + "/IndexStatistics.csv"
    file_exists = os.path.isfile(output_csv)
    if not os.path.exists(f'./Result/{exp_name}/'):
        os.makedirs(f'./Result/{exp_name}/')
    with open(output_csv, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not file_exists:
            csv_writer.writerow(["Index Identifier", "Build Time (s)", "Build Memory (MB)", "Split Segment Time (s)", "Index Size (MB)", "Segment Number"])
        csv_writer.writerow([index_identifier, build_time, build_memory, split_segment_time, IndexSize, segment_number])

def save_dataset_statistics(dataset_identifier, output_csv, data_size_mb, trajectory_number, recordNum, avg_time_interval, selected_interval, max_segment_length):
    file_exists = os.path.isfile(output_csv)
    with open(output_csv, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not file_exists:
            csv_writer.writerow(["Dataset Identifier", "Data Size (Mb)", "Trajectory Number", "Record Number", "Avg Record Number per Trajectory", "Avg Time Interval", "Selected Interval", "Max Trajectory Length"])
        csv_writer.writerow([dataset_identifier, f"{data_size_mb:.2f}", trajectory_number, recordNum, f"{recordNum / trajectory_number:.2f}",  f"{avg_time_interval:.2f}", f"{selected_interval:.2f}", max_segment_length])

def save_query_statistics(exp_name, model_name, query_time, query_memory, hit_k):
    output_csv = "./Result/" + exp_name + "/query_statistics.csv"
    file_exists = os.path.isfile(output_csv)
    if not os.path.exists(f'./Result/{exp_name}/'):
        os.makedirs(f'./Result/{exp_name}/')
    with open(output_csv, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        if not file_exists:
            csv_writer.writerow(["Model Name", "Query Time (s)", "Query Memory (MB)", "Hit@k"])
        csv_writer.writerow([model_name, query_time, query_memory, hit_k])


def save_experiment_results(args_dict, exp_result, exp_name = "Default"):
    # Generate a unique filename using timestamp and key parameters
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"experiment_{timestamp}.json" 
    # Combine args_dict and exp_result
    result = {
        "args": args_dict,
        "results": exp_result
    }
    if not os.path.exists(f"Result/{exp_name}"):
        os.makedirs(f"Result/{exp_name}")

    with open(f"Result/{exp_name}/{filename}", "w") as f:
        json.dump(result, f, indent=4)    
    print(f"Results saved to Result/{exp_name}/{filename}")