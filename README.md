# ACTIVE: Continuous Similar Search for Vessel Trajectories
This repository is the official implementation of the real-time continuous trajectory similarity search method for vessels.

## Abstract
Publicly available vessel trajectory data is emitted continuously from the global AIS system. Continuous trajectory similarity search on this data has applications in, e.g., maritime navigation and safety.
Existing proposals typically assume an offline setting and focus on finding similarities between complete trajectories. Such proposals are less effective when applied to online scenarios, where similarity comparisons must be performed continuously as new trajectory data arrives and trajectories evolve.
We therefore propose a re$\underline{\textbf{a}}$l-time $\underline{\textbf{c}}$ontinuous $\underline{\textbf{t}}$rajectory s$\underline{\textbf{i}}$milarity search method for $\underline{\textbf{ve}}$ssels  ($\texttt{ACTIVE}$). We introduce a novel similarity measure, object-trajectory real-time distance, that emphasizes the anticipated future movement trends of vessels, enabling more predictive and forward-looking comparisons. Next, we propose a segment-based vessel trajectory index structure that organizes historical trajectories into smaller and manageable segments, facilitating accelerated similarity computations. Leveraging this index, we propose an efficient continuous similar trajectory search ($\texttt{CSTS}$) algorithm together with a variety of search space pruning strategies that reduce unnecessary computations during the continuous similarity search, thereby further improving efficiency. 
Extensive experiments on two large real-world AIS datasets offer evidence that $\texttt{ACTIVE}$ is capable of outperforming state-of-the-art methods considerably. $\texttt{ACTIVE}$ significantly reduces index construction costs and index size while achieving a 70\% reduction in terms of query time and a 60\% increase in terms of hit rate.

## Environment Setting
```bash
conda create -n ACTIVE python=3.8
conda activate ACTIVE
bash environment_install.sh
```
## Code Structure

```
.
📦 ACTIVE
 ┣ 📂 Data                     # Directory for storing datasets
 ┣ 📂 Result                   # Directory for storing experimental results
 ┣ 📂 src                      # Source code directory
 ┃ ┣ 📂 Index                  # Data structure implementations
 ┃ ┣ 📂 Measure               # Trajectory similarity measures
 ┃ ┣ 📂 utils                 # Common utility functions
 ┃ ┗ 📜 main.py               # Main program entry point
 ┣ 📜 README.md               # Project documentation and instructions
 ┗ 📜 environment_install.sh  # Environment setup script
```

## Dataset Preparation
The datasets can be automatically downloaded from http://web.ais.dk/aisdata/ or https://coast.noaa.gov/htdata/CMSP/AISDataHandler/2023/index.html based on the dataset hyperparameter. The dataset parameter follows the format:

- For AISDK dataset: aisdk-YYYY-MM-DD1@DD2 (e.g. aisdk-2023-01-01@02)
- For AISUS dataset: AIS_YYYY_MM_DD1@DD2 (e.g. AIS_2023_12_11@31)

where YYYY-MM-DD1@DD2 specifies the date range of the dataset.

## Running of ACTIVE
```
python ./src/main.py --dataset aisdk-2023-01-01@02 --model_type ACTIVE
```
The detailed results of the execution can be found in the ./Result folder.

## Hyper-paramter Explain of ACTIVE

### Data Processing Parameters
- **dataset**: The dataset identifier in format 'aisdk-YYYY-MM-DD@DD' (e.g. aisdk-2006-03-02@05) for Danish AIS data or 'AIS_YYYY_MM_DD@DD' for US AIS data.

- **datascalability**: Controls the proportion of data to use, ranging from 0.2 to 1.0. A value of 1.0 uses the full dataset while 0.2 uses 20% of the data.

- **connection_ratio**: Threshold for trajectory connectivity, ranging from 0 to 1. Higher values (e.g. 0.99) ensure more continuous trajectories by filtering out those with large gaps.

### Query Parameters
- **target_trajectory_list**: List of trajectory IDs to use as query trajectories, specified as tuples of (trajectory_id, segment_id). Default is [], which means all trajectories are used as query trajectories.

- **query_traj_num**: Number of query trajectories to process. 

- **continuous_length**: Length of continuous trajectory segments to consider during search. 

- **query_range**: Spatial range threshold for candidate trajectory filtering.   

- **query_length**: Least number of historical points to use from query trajectory. 

- **topk**: Number of most similar trajectories to return. 

- **candidate_ratio**: Ratio of candidate trajectories to consider relative to total trajectories. Default is 10, meaning 10 * topk trajectories are considered as candidates.

### Hyper-parameter of ACTIVE
- **lm**: Minimum length of trajectory segments (minlen_seq).
- **ln**: Maximum length of trajectory segments (maxlen_seq).
- **theta**: Decay factor for historical trajectory points, ranging from 0 to 1. Lower values assign greater importance to recent points, while higher values treat all points with similar weight.
- **alpha**: Threshold parameter for trajectory similarity matching, ranging from 0 to 1. Lower values place more emphasis on the destination, while higher values focus more on the historical trajectory.
- **gran**: Granularity parameter that controls the level of detail in trajectory comparison. Lower values provide higher precision but require more computation time, while higher values improve speed at the cost of some accuracy. Default is 1.





