# Copyright (c) 2024, Huawei Technologies Co., Ltd.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0  (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analysis.analysis_facade import AnalysisFacade
from cluster_data_preprocess.pytorch_data_preprocessor import PytorchDataPreprocessor
from cluster_data_preprocess.mindspore_data_preprocessor import MindsporeDataPreprocessor
from communication_group.communication_group_generator import CommunicationGroupGenerator
from profiler.prof_common.additional_args_manager import AdditionalArgsManager
from profiler.prof_common.constant import Constant
from profiler.prof_common.file_manager import FileManager
from profiler.prof_common.path_manager import PathManager

COMM_FEATURE_LIST = ['all', 'communication_time', 'communication_matrix']

logger = logging.getLogger("cluster")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('\r\033[K[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class Interface:
    ASCEND_PT = "ascend_pt"
    ASCEND_MS = "ascend_ms"

    def __init__(self, params: dict):
        self.collection_path = PathManager.get_realpath(params.get(Constant.COLLECTION_PATH))
        self.analysis_mode = params.get(Constant.ANALYSIS_MODE)
        self.data_map = {}
        self.communication_group = {}
        self.collective_group_dict = {}
        self.communication_ops = []
        self.matrix_ops = []
        self.origin_params = params
        self.cluster_analysis_output_path = self.get_cluster_analysis_output_path(params)
        self.force = params.get(Constant.FORCE, False)

    def get_cluster_analysis_output_path(self, params):
        cluster_analysis_output_path = params.get(Constant.CLUSTER_ANALYSIS_OUTPUT_PATH)
        if cluster_analysis_output_path:
            return PathManager.get_realpath(cluster_analysis_output_path)
        return self.collection_path

    def allocate_prof_data(self):
        ascend_pt_dirs = []
        ascend_ms_dirs = []
        for root, dirs, _ in os.walk(self.collection_path):
            for dir_name in dirs:
                if dir_name.endswith(self.ASCEND_PT):
                    ascend_pt_dirs.append(os.path.join(root, dir_name))
                if dir_name.endswith(self.ASCEND_MS):
                    ascend_ms_dirs.append(os.path.join(root, dir_name))
        pytorch_processor = PytorchDataPreprocessor(ascend_pt_dirs)
        pt_data_map = pytorch_processor.get_data_map()
        data_type = pytorch_processor.get_data_type()
        ms_data_map = MindsporeDataPreprocessor(ascend_ms_dirs).get_data_map()
        if pt_data_map and ms_data_map:
            logger.error("Can not analyze pytorch and mindspore meantime.")
            return []
        return (pt_data_map, data_type) if pt_data_map else (ms_data_map, Constant.TEXT)

    def run(self):
        PathManager.check_input_directory_path(self.collection_path)
        PathManager.check_path_owner_consistent([self.collection_path])
        data_map, data_type = self.allocate_prof_data()
        if not data_map:
            logger.warning("Can not get rank info or profiling data.")
            return
        if data_type == Constant.INVALID:
            logger.error("The current folder contains both DB and other files. Please check.")
            return
        PathManager.check_input_directory_path(self.cluster_analysis_output_path)
        FileManager.create_output_dir(self.cluster_analysis_output_path)
        PathManager.check_path_writeable(self.cluster_analysis_output_path)
        PathManager.check_path_owner_consistent([self.cluster_analysis_output_path])
        params = {
            Constant.COLLECTION_PATH: self.collection_path,
            Constant.DATA_MAP: data_map,
            Constant.ANALYSIS_MODE: self.analysis_mode,
            Constant.DATA_TYPE: data_type,
            Constant.CLUSTER_ANALYSIS_OUTPUT_PATH: self.cluster_analysis_output_path,
            Constant.DATA_SIMPLIFICATION: self.origin_params.get(Constant.DATA_SIMPLIFICATION, False),
            Constant.FORCE: self.force
        }
        logger.info("Begin generate communication data.")
        comm_data_dict = CommunicationGroupGenerator(params).generate()
        logger.info("Communication data read completed.")
        params[Constant.COMM_DATA_DICT] = comm_data_dict
        AnalysisFacade(params).cluster_analyze()
        logger.info("The cluster analysis result file has been generated: %s", self.cluster_analysis_output_path)


def cluster_analysis_main(args=None):
    parser = argparse.ArgumentParser(description="cluster analysis module")
    parser.add_argument('-d', '--profiling_path', type=str, required=True, help="profiling data path")
    parser.add_argument('-m', '--mode', choices=COMM_FEATURE_LIST,
                        default='all', help="different analysis mode")
    parser.add_argument('-o', '--output_path', type=str, help='Path of cluster analysis output')
    parser.add_argument(
        '--data_simplification', default=False, action='store_true', help='data simplification switch for db data'
    )
    parser.add_argument('--force', action='store_true',
                        help="Indicates whether to skip file size verification and owner verification")
    args_parsed = parser.parse_args(args=args)
    parameter = {
        Constant.COLLECTION_PATH: args_parsed.profiling_path,
        Constant.ANALYSIS_MODE: args_parsed.mode,
        Constant.CLUSTER_ANALYSIS_OUTPUT_PATH: args_parsed.output_path,
        Constant.DATA_SIMPLIFICATION: args_parsed.data_simplification,
        Constant.FORCE: args_parsed.force
    }
    AdditionalArgsManager().init(parameter)
    try:
        Interface(parameter).run()
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    cluster_analysis_main()
