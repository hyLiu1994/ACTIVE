import sys, os, requests, zipfile, csv, pandas as pd, numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from Index.RTree import format_mbr
from utils.SaveLoadModule import save_processed_traj_data, load_processed_traj_data, save_dataset_statistics
from concurrent.futures import ProcessPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

time_col_name = "# Timestamp"
Lat_col_name = "Latitude"
Lon_col_name = "Longitude"
time_formulation = "%d/%m/%Y %H:%M:%S"
  
# Download raw data of AISDK and AISUS
def download_ais_dataset(file_name_list):
    csv_file_path_list = []
    for file_name in file_name_list:
        # Step 1: Set base information about raw dataset
        global time_col_name, Lat_col_name, Lon_col_name, time_formulation
        if "aisdk" in file_name:
            download_url = "http://web.ais.dk/aisdata/"
            csv_file_name = f"{file_name}.csv"
            if ("2006" in file_name):
                csv_file_name = file_name[:5] + "_" + file_name[5:].replace("-", "") + ".csv"
            print(csv_file_name)
            time_col_name, Lat_col_name, Lon_col_name = "# Timestamp", "Latitude", "Longitude"
            time_formulation = "%d/%m/%Y %H:%M:%S"
        else:
            download_url = "https://coast.noaa.gov/htdata/CMSP/AISDataHandler/" + file_name[4:8] + "/"
            csv_file_name = f"{file_name}.csv"
            time_col_name, Lat_col_name, Lon_col_name = "BaseDateTime", "LAT", "LON"
            time_formulation = "%Y-%m-%dT%H:%M:%S"

        # Step 2: Check if CSV file already exists
        csv_file_path = os.path.join("./Data/RawData/", csv_file_name)

        if os.path.exists(csv_file_path):
            print(f"CSV file '{csv_file_path}' already exists. No download needed.")
            csv_file_path_list.append(csv_file_path)
            continue

        # Step 3: Download and unzip if CSV doesn't exist
        def attempt_download(url, zip_path):
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                total_length = int(response.headers.get('content-length'))
                with open(zip_path, 'wb') as file, tqdm(
                    desc=zip_path,
                    total=total_length,
                    unit='iB',
                    unit_scale=True,
                    unit_divisor=1024,
                ) as bar:
                    for chunk in response.iter_content(chunk_size=8192):
                        size = file.write(chunk)
                        bar.update(size)
                print(f"ZIP file downloaded successfully as {zip_path}")
                return True
            except requests.exceptions.HTTPError:
                return False

        # First attempt
        if not os.path.exists(f'./Data/RawData/'):
            os.makedirs(f'./Data/RawData/')
        zip_path = "./Data/RawData/" + file_name + ".zip"
        url = download_url + file_name + ".zip"
        if not attempt_download(url, zip_path):
            # Second attempt
            url = download_url + file_name[:-3] + ".zip"
            zip_path = "./Data/RawData/" + file_name[:-3] + ".zip"
            if not attempt_download(url, zip_path):
                print(f"Error: Unable to download the file for {file_name}. The file may not exist.")
                return None

        def unzip_file(zip_path, extract_to):
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                    print(f"File '{zip_path}' has been unzipped.")
            except zipfile.BadZipFile:
                print(f"Error: The file '{zip_path}' is not a valid ZIP file.")
            except Exception as e:
                print(f"Error unzipping the file '{zip_path}': {e}")
        # Unzip the file
        unzip_file(zip_path, "./Data/RawData/")

        # Check if CSV file now exists after unzipping
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file '{csv_file_path}' not found after unzipping.")
            return None

        csv_file_path_list.append(csv_file_path)
    print(csv_file_path_list)
    return csv_file_path_list

def analysis_frequency_time_interval(df, dataset_identifier, ratio = 2.0/3, file_dir = "./"):
    # 时间戳已经是 UNIX 时间戳，不需要再次转换
    df['Second'] = pd.to_datetime(df[time_col_name], unit='s')
    df.sort_values(by=['MMSI', 'Second'], inplace=True)
    df['Time_diff'] = df.groupby('MMSI')['Second'].diff().dt.total_seconds()
    df['Time_diff'].fillna(0, inplace=True)
    df['Time_diff'] = df['Time_diff'].astype(int)
    time_diff_freq = df['Time_diff'].value_counts().reset_index()
    time_diff_freq.columns = ['Time_diff', 'Frequency']
    plt.figure(figsize=(10, 6))
    plt.bar(time_diff_freq['Time_diff'], time_diff_freq['Frequency'], width=100)  # 调整宽度以适应您的数据
    plt.xlim(0, 1000)
    plt.xlabel('Time Interval')
    plt.ylabel('Frequency (log scale)') 
    plt.yscale('log') 
    plt.title(dataset_identifier)
    if not os.path.exists(file_dir + f'./Result/Figure/'):
        os.makedirs(file_dir + f'./Result/Figure/')
    plt.savefig(file_dir + f'./Result/Figure/frequency_distribution_{dataset_identifier}.png')

    time_diff_freq.sort_values('Time_diff', inplace=True)
    total_frequency = time_diff_freq['Frequency'].sum()
    time_diff_freq['Cumulative_Percentage'] = time_diff_freq['Frequency'].cumsum() / total_frequency * 100

    plt.figure(figsize=(10, 6))
    plt.plot(time_diff_freq['Time_diff'], time_diff_freq['Cumulative_Percentage'], marker='o', linestyle='-')
    plt.xlim(0, 1000)
    plt.xlabel('Time Interval')
    plt.ylabel('Percentage of Data <= Interval (%)')
    plt.title('Cumulative Percentage of Data <= Each Time Interval')
    plt.grid(True)
    plt.savefig(file_dir + f'./Result/Figure/cumulative_percentage_distribution_{dataset_identifier}.png')

    total_data_points = len(df)
    time_diff_freq_sorted = time_diff_freq.sort_values(by='Time_diff')
    time_diff_freq_sorted['Cumulative_Frequency'] = time_diff_freq_sorted['Frequency'].cumsum()

    threshold_frequency = ratio * total_data_points
    selected_interval = time_diff_freq_sorted.loc[time_diff_freq_sorted['Cumulative_Frequency'] >= threshold_frequency, 'Time_diff'].iloc[0]
    print("Selected Interval:", selected_interval, "seconds,  ", "ratio: ", ratio * 100, "%.")
    return selected_interval

def filter_invalid_coordinates(data, traj_id, times_interval, traj_data, max_segment_length):
        timestamps = data['timestamps']
        latitudes = data['latitudes']
        longitudes = data['longitudes']

        valid_coords = (-90 <= latitudes) & (latitudes <= 90) & (-180 <= longitudes) & (longitudes <= 180)
        
        timestamps = timestamps[valid_coords]
        latitudes = latitudes[valid_coords]
        longitudes = longitudes[valid_coords]

        if len(timestamps) == 0:
            return

        time_diffs = np.diff(timestamps)
        split_indices = np.where(time_diffs > times_interval)[0] + 1
        
        segments = np.split(timestamps, split_indices)
        lat_segments = np.split(latitudes, split_indices)
        lon_segments = np.split(longitudes, split_indices)

        # Further split segments exceeding 300 points
        new_segments = []
        new_lat_segments = []
        new_lon_segments = []

        for seg, lat_seg, lon_seg in zip(segments, lat_segments, lon_segments):
            if len(seg) > max_segment_length:
                num_splits = int(np.ceil(len(seg) / max_segment_length))
                split_indices = np.array_split(np.arange(len(seg)), num_splits)
                new_segments.extend([seg[idx] for idx in split_indices])
                new_lat_segments.extend([lat_seg[idx] for idx in split_indices])
                new_lon_segments.extend([lon_seg[idx] for idx in split_indices])
            else:
                new_segments.append(seg)
                new_lat_segments.append(lat_seg)
                new_lon_segments.append(lon_seg)

        # Replace original segments with new ones
        segments, lat_segments, lon_segments = new_segments, new_lat_segments, new_lon_segments

        # Pre-allocate dictionary with estimated size
        estimated_size = len(split_indices) + 1
        traj_data_local = {}
        for seq_id in range(estimated_size):
            traj_data_local[f"{traj_id}_{seq_id}"] = None

        for seq_id, (ts_seg, lat_seg, lon_seg) in enumerate(zip(segments, lat_segments, lon_segments)):
            if len(ts_seg) >= 5:
                traj_data_local[f"{traj_id}_{seq_id}"] = {
                    'timestamps': ts_seg.tolist(),
                    'latitudes': lat_seg.tolist(),
                    'longitudes': lon_seg.tolist()
                }

        # Remove None values and update the main traj_data dictionary
        traj_data.update({k: v for k, v in traj_data_local.items() if v is not None}) 

def process_filter_invalid_coordinates(new_id, ship_df, selected_interval, time_col_name, Lat_col_name, Lon_col_name, max_segment_length):
    traj_data = {}
    filter_invalid_coordinates({
        'timestamps': ship_df[time_col_name].values,  # Now using numpy array directly
        'latitudes': ship_df[Lat_col_name].values,
        'longitudes': ship_df[Lon_col_name].values
    }, new_id, selected_interval, traj_data, max_segment_length)
    return traj_data

def load_ais_dataset(args):
    #region Step 0: Check if processed data exists
    # Generate a unique identifier for the processed dataset
    dataset_identifier = f"{args.dataset}_{args.datascalability}_{args.connection_ratio}"
    processed_data_path = f"./Data/ProcessedData/{dataset_identifier}.pkl"

    if os.path.exists(processed_data_path):
        return load_processed_traj_data(dataset_identifier, with_segment=False), dataset_identifier  # Add dataset_identifier here
    print("Processed data not found. Processing raw data...")
    #endregion

    #region Step 1: DataSet Selections (dataset list and scalability)
    if "@" in args.dataset:
        dataset_start, dataset_end = args.dataset.split("@")[0], int(args.dataset.split("@")[1])
        print(dataset_start, dataset_end)
        file_name_list = [dataset_start[:-2] + str(i).zfill(2) for i in range(int(dataset_start.split(dataset_start[-3])[-1]), int(dataset_end)+ 1)]
        print(file_name_list)
    else:
        file_name_list = [args.dataset]

    csv_file_list = download_ais_dataset(file_name_list)
    print("begin load aisdk_dataset")
    df_list = []
    data_size_mb = 0
    for csv_file in csv_file_list:
        print(f"Reading file: {csv_file}")
        df = pd.read_csv(csv_file)
        df_list.append(df)
        data_size_mb += os.path.getsize(csv_file) / (1024 * 1024) 
    df = pd.concat(df_list, ignore_index=True)
    print("end load aisdk_dataset")
    # Calculate Data Size (Mb)
    datascalability = args.datascalability
    df = df.head(int(len(df) * datascalability))
    data_size_mb *= datascalability
    #endregion

    # Step 2 Data Filter and Process
    #region Step 2.1 Trajectory Generation according to connection_ratio
    # Convert timestamps to UNIX timestamp during data loading
    df[time_col_name] = pd.to_datetime(df[time_col_name], format=time_formulation).astype(int) / 10**9
    df[time_col_name] = df[time_col_name].astype(int) 
    selected_interval = analysis_frequency_time_interval(df, dataset_identifier, args.connection_ratio)
    mmsi_unique = df['MMSI'].unique()
    mmsi_to_new_id = dict(zip(mmsi_unique, range(len(mmsi_unique))))
    df['New_ID'] = df['MMSI'].map(mmsi_to_new_id)

    # Use numpy arrays for faster operations
    timestamps = df[time_col_name].values
    latitudes = df[Lat_col_name].values
    longitudes = df[Lon_col_name].values
    new_ids = df['New_ID'].values
    #endregion
    #region Step 2.2 Filter invalid data
    # Use multiprocessing to parallelize the processing
    traj_data = {}
    with ProcessPoolExecutor() as executor:
        futures = []
        for new_id in np.unique(new_ids):
            mask = new_ids == new_id
            ship_df = pd.DataFrame({
                time_col_name: timestamps[mask],
                Lat_col_name: latitudes[mask],
                Lon_col_name: longitudes[mask]
            })
            futures.append(executor.submit(process_filter_invalid_coordinates, new_id, ship_df, selected_interval, time_col_name, Lat_col_name, Lon_col_name, args.max_segment_length))
        
        for future in tqdm(futures, desc="Filter Raw Data"):
            traj_data.update(future.result())
    #endregion

    #region Step 3 Generate Data
    recordNum = 0
    total_time_diff = 0
    max_segment_length = 0
    for traj_id, data in tqdm(traj_data.items(), desc="Load Ship Data"):
        positions_list = list(zip(data['latitudes'], data['longitudes']))
        max_segment_length = max(max_segment_length, len(positions_list))
        mbr_list = [format_mbr((data['latitudes'][idx], data['longitudes'][idx], data['latitudes'][idx+1], data['longitudes'][idx+1])) for idx in range(len(data['latitudes'])-1)]
        traj_data[traj_id].update({
            'traj_mbr': [min(data['latitudes']), min(data['longitudes']), max(data['latitudes']), max(data['longitudes'])],
            'positions_list': positions_list,
            'mbr_list': mbr_list
        })
        recordNum += len(positions_list) 
        # Calculate total time difference for average time interval
        if len(data['timestamps']) > 1:
            total_time_diff += data['timestamps'][-1] - data['timestamps'][0]
    #endregion

    # Step 4: Stacstic Result of datasets
    #region Step 4.1: Print result of datasets
    # Calculate metrics
    avg_time_interval = total_time_diff / (recordNum - len(traj_data)) if recordNum > len(traj_data) else 0
    trajectory_number = len(traj_data)

    print(f"Data Size (Mb): {data_size_mb:.2f}")
    print(f"Record Number: {recordNum}")
    print(f"Avg. Time interval between adjacent GPS points: {avg_time_interval:.2f} seconds")
    print(f"Trajectory (MMSI) number: {trajectory_number}")
    #endregion
    #region Step 4.2: Write result of datasets
    # Write the result to the specified CSV file
    save_dataset_statistics(dataset_identifier, args.dataset_statistics_csv_path, data_size_mb, trajectory_number, recordNum, avg_time_interval, selected_interval, max_segment_length)
    #endregion

    #region Step 5: Save processed data
    # Save processed data
    os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
    save_processed_traj_data(dataset_identifier, traj_data, with_segment=False)
    print(f"Processed data saved to {processed_data_path}")
    #endregion

    # Return both traj_data and dataset_identifier
    # traj_data {'traj_id':{'traj_mbr':[], 'positions_list':[], 'mbr_list':[], 'segment_list':[]}}
    return traj_data, dataset_identifier

def hyperparameter_DataProcess(parser):
    # Dataset Process 
    # aisdk-2006-03-02@05 0.99
    # AIS_2023_12_11@31 0.99 
    # aisdk-2024-09-16@22 0.99
    parser.add_argument("--dataset", type=str, default='aisdk-2006-03-02@05')
    #aisdk-2006-03-02@050.2, 0.4, 0.6, 0.8, 1.0
    parser.add_argument("--datascalability", type=float, default=1)
    # Connection Ratio
    parser.add_argument("--connection_ratio", type=float, default=0.99)
    # max_segment_length
    parser.add_argument("--max_segment_length", type=int, default=300)
    # Result Path
    parser.add_argument("--dataset_statistics_csv_path", type=str, default="./Result/DatasetStatistics.csv")
    return parser

