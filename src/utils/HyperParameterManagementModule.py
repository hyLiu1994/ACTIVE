import argparse
from utils.utils import model_wrapper
from Index.IndexWrapper import hyperparameter_Index
from Measure.MeasureWrap import hyperparameter_Measure
from utils.DataProcessModule import hyperparameter_DataProcess
from utils.utils import hyperparameter_Model
from utils.utils import hyperparameter_Segment
from utils.CurrentTrajectoryProcessModule import hyperparameter_CurrentTrajectoryProcess

def load_hypermater():
    # Setting hyperpameter 
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp_name", type=str, default="Default")

    parser = hyperparameter_DataProcess(parser)
    parser = hyperparameter_Index(parser)
    parser = hyperparameter_Model(parser)
    parser = hyperparameter_Segment(parser) 
    parser = hyperparameter_Measure(parser)
    parser = hyperparameter_CurrentTrajectoryProcess(parser)

    args = parser.parse_args()
    args = model_wrapper(args)
    args.exp_name = args.dataset + "_" + args.exp_name 

    return args