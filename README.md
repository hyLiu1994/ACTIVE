# ACTIVE: Continuous Similar Search for Vessel Trajectories
## Abstract
Trajectory similarity search has attracted significant attention, especially in applications such as transportation, maritime navigation, and traffic monitoring, where identifying patterns in movement is critical. Existing studies typically focus on finding similarities between entire trajectories using retrospective analysis. However, these methods become less effective when applied to real-time scenarios, where continuous and evolving trajectory comparisons are required as new data is constantly generated. 

We address these limitations by proposing a real-time continuous trajectory similarity search method for vessels  (ACTIVE). We introduce a novel similarity measure, Object-Trajectory Real-time Distance (OTRD), that places greater emphasis on the future trend of moving objects, allowing for more predictive and forward-looking comparisons. To optimize performance, we develop an index structure, Segment-based Vessel Trajectory Index (SVTI), that organizes historical trajectories into smaller and manageable segments, facilitating faster and more efficient similarity calculations. Next, we implement a variety of pruning strategies to reduce unnecessary computations during the similarity calculation and the continuous search process, further improving the ACTIVE's efficiency and scalability. Through extensive experimental evaluations using two large real-world AIS datasets, we demonstrate that ACTIVE significantly outperforms existing solutions in both efficiency and effectiveness. For index construction, our method reduces costs by a factor of 100 in terms of construction time and index size. For search, ACTIVE outperforms six state-of-the-arts by up to 70\% in terms of query time and 60\% in terms of hit rate.

## Environment Setting
```bash
conda create -n ACTIVE python=3.8
conda activate ACTIVE
bash environment_install.sh
```
## Code Structure

```
.
├── Data                # Directory for automatically storing datasets
├── Result              # Directory for automatically storing experimental results
├── src
    ├── Index           # Implementation of data structures
    ├── Measure         # Implementation of trajectory similarity measures
    ├── utils           # Implementation of common functions
    └── main.py         # Main program entry point
├── README.md           # Main documentation file with project overview and instructions
├── environment_install.sh  # Shell script for installing required Python packages
```

## Dataset Preparation
The datasets can be automatically downloaded from http://web.ais.dk/aisdata/ or https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2023/index.html based on the dataset hyperparameter. The dataset parameter follows the format:

- For AISDK dataset: aisdk-YYYY-MM-DD1@DD2 (e.g. aisdk-2023-01-01@02)
- For AISUS dataset: AIS_YYYY_MM_DD1@DD2 (e.g. AIS_2023_12_11@31)

where YYYY-MM-DD1@DD2 specifies the date range of the dataset.

## Running of ACTIVE
```
python main.py --dataset aisdk-2023-01-01@02 --model_type ACTIVE
```
The detailed results of the execution can be found in the ./Result folder.

## Hyper-paramter Explain of ACTIVE

### Data Processing Parameters
- **dataset**: The dataset identifier in format 'aisdk-YYYY-MM-DD@DD' (e.g. aisdk-2006-03-02@05) for Danish AIS data or 'AIS_YYYY_MM_DD@DD' for US AIS data.

- **datascalability**: Controls the proportion of data to use, ranging from 0.2 to 1.0. A value of 1.0 uses the full dataset while 0.2 uses 20% of the data.

- **connection_ratio**: Threshold for trajectory connectivity, ranging from 0 to 1. Higher values (e.g. 0.99) ensure more continuous trajectories by filtering out those with large gaps.

### Query Parameters
- **target_trajectory_list**: List of trajectory IDs to use as query trajectories, specified as tuples of (trajectory_id, segment_id). Default is [(2273, 0), (3274, 0), (4275, 0)].

- **query_traj_num**: Number of query trajectories to process. 

- **continuous_length**: Length of continuous trajectory segments to consider during search. 

- **query_range**: Spatial range threshold for candidate trajectory filtering.   

- **query_length**: Number of historical points to use from query trajectory. 

- **future_length**: Number of future points to predict and compare. 

- **topk**: Number of most similar trajectories to return. 

- **candidate_ratio**: Ratio of candidate trajectories to consider relative to total trajectories. Default is 10, meaning 10 * topk trajectories are considered as candidates.

### Hyper-parameter of ACTIVE
- **lm**: Minimum length of trajectory segments (minlen_seq).
- **ln**: Maximum length of trajectory segments (maxlen_seq).
- **theta**: Decay factor for historical trajectory points, ranging from 0 to 1. Lower values assign greater importance to recent points, while higher values treat all points with similar weight.
- **alpha**: Threshold parameter for trajectory similarity matching, ranging from 0 to 1. Lower values place more emphasis on the destination, while higher values focus more on the historical trajectory.
- **gran**: Granularity parameter that controls the level of detail in trajectory comparison. Lower values provide higher precision but require more computation time, while higher values improve speed at the cost of some accuracy. Default is 1.





