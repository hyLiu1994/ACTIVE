
def get_current_trajectory_info(traj_idx, timestamp, traj_data, args):
    num_target_traj = len(args.target_trajectory_list)
    if (num_target_traj == 0):
        args.target_trajectory_list = [(int(raw_traj_id.split('_')[0]), int(raw_traj_id.split('_')[1])) if (len(args.target_trajectory_list) <= args.query_traj_num) else args.target_trajectory_list[0] for raw_traj_id in traj_data.keys()]
        num_target_traj = len(args.target_trajectory_list)
    raw_traj_id = str(args.target_trajectory_list[traj_idx % num_target_traj][0]) \
            + '_' + str(args.target_trajectory_list[traj_idx % num_target_traj][1])
    timestamp = timestamp + args.query_length
    if (raw_traj_id not in traj_data.keys()):
        raw_traj_id = list(traj_data.keys())[0]

    target_trajectory_idx = args.target_trajectory_list[traj_idx % num_target_traj][0]
    while (raw_traj_id not in traj_data.keys() or len(traj_data[raw_traj_id]['positions_list']) <= args.query_length + args.future_length):
        target_trajectory_idx += 1
        raw_traj_id = str(target_trajectory_idx) \
            + '_' + str(args.target_trajectory_list[traj_idx % num_target_traj][1])

    if (timestamp >= len(traj_data[raw_traj_id]['positions_list'])):
        timestamp = len(traj_data[raw_traj_id]['positions_list']) - 1
    current_point = traj_data[raw_traj_id]['positions_list'][timestamp-1]
    next_point = traj_data[raw_traj_id]['positions_list'][timestamp]
    current_traj = traj_data[raw_traj_id]['positions_list'][:timestamp]
    current_target = traj_data[raw_traj_id]['positions_list'][-1]
    print("----------------------------------------------------------------------------------")
    print("traj_idx & timestamp", args.target_trajectory_list[traj_idx % num_target_traj], timestamp)
    print("current_point & target_point", current_point, current_target)
    print("----------------------------------------------------------------------------------")
    return (raw_traj_id, current_point, current_traj, current_target, next_point)

def hyperparameter_CurrentTrajectoryProcess(parser):
    parser.add_argument("--target_trajectory_list", type=list, default=[]) 
    parser.add_argument("--query_traj_num", type=int, default=30)
    parser.add_argument("--continuous_length", type=int, default=10)
    parser.add_argument("--query_range", type=float, default=0.000000125)
    parser.add_argument("--query_length", type=int, default=10)
    parser.add_argument("--future_length", type=int, default=10)
    parser.add_argument("--topk", type=int, default=10) 
    parser.add_argument("--candidate_ratio", type=float, default=10)
    return parser
