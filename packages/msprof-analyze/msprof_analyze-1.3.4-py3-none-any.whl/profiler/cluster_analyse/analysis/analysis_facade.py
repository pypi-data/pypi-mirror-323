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
from multiprocessing import Process, Value, Lock
from tqdm import tqdm
from analysis.communication_analysis import CommunicationAnalysis
from analysis.communication_analysis import CommunicationAnalysisOptimized
from analysis.comm_matrix_analysis import CommMatrixAnalysis
from analysis.comm_matrix_analysis import CommMatrixAnalysisOptimized
from analysis.step_trace_time_analysis import StepTraceTimeAnalysis
from analysis.host_info_analysis import HostInfoAnalysis
from profiler.prof_common.constant import Constant


class AnalysisFacade:
    default_module = {CommunicationAnalysis, StepTraceTimeAnalysis, CommMatrixAnalysis, HostInfoAnalysis}
    simplified_module = {
        CommunicationAnalysisOptimized, StepTraceTimeAnalysis, CommMatrixAnalysisOptimized, HostInfoAnalysis
    }

    def __init__(self, params: dict):
        self.params = params

    def cluster_analyze(self):
        # 多个profiler用多进程处理
        process_list = []
        if self.params.get(Constant.DATA_SIMPLIFICATION) and self.params.get(Constant.DATA_TYPE) == Constant.DB:
            analysis_module = self.simplified_module
        else:
            analysis_module = self.default_module

        num_processes = len(analysis_module)
        completed_processes = Value('i', 0)
        lock = Lock()

        # 自定义进度条格式，显示已完成任务数量和总数量
        bar_format = '{l_bar}{bar} | {n_fmt}/{total_fmt}'

        with tqdm(total=num_processes, desc="Cluster analyzing", bar_format=bar_format) as pbar:
            for analysis in analysis_module:
                pbar.n = completed_processes.value
                pbar.refresh()
                process = Process(target=analysis(self.params).run, args=(completed_processes, lock))
                process.start()
                process_list.append(process)

            while any(p.is_alive() for p in process_list):
                with lock:
                    pbar.n = completed_processes.value
                    pbar.refresh()

        for process in process_list:
            process.join()

        with lock:
            pbar.n = completed_processes.value
            pbar.refresh()
