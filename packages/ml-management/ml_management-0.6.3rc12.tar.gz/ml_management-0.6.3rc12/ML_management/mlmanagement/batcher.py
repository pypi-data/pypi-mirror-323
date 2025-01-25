import time
import warnings
from collections import deque
from threading import Event, Thread
from typing import Dict

from sgqlc.operation import Operation

from ML_management import variables
from ML_management.graphql import schema
from ML_management.graphql.schema import MetricInput
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.singleton_pattern import Singleton
from ML_management.variables import METRIC_ACCUMULATION_DURATION, TIMEOUT_LOG_METRIC_BATCH


class Batcher(metaclass=Singleton):
    def __init__(self):
        self.batch = deque()
        self.thread = None
        self.stop_event = Event()

    def log_metric(self, key: str, value: float, step: int):
        self.batch.append((key, value, step))
        self._start_thread()

    def log_metrics(self, metrics: Dict[str, float], step: int):
        self.batch.extend((key, value, step) for key, value in metrics.items())
        self._start_thread()

    def _start_thread(self):
        if not self.thread:
            self.stop_event.clear()
            self.thread = Thread(target=self.log_batch_metric, args=(self.stop_event,), daemon=True)
            self.thread.start()

    def _stop_batching(self):
        self.batch = deque()
        if self.thread:
            self.stop_event.set()
            self.thread.join()

    def log_batch_metric(self, stop_event):
        while not stop_event.is_set():
            metrics_to_log = self.batch.copy()
            op = Operation(schema.Mutation)
            op.log_metrics(
                metrics=[MetricInput(key=key, value=value, step=step) for key, value, step in metrics_to_log],
                job_run_id=variables.job_run_id,
            )
            try:
                send_graphql_request(op, json_response=False, timeout=5)
                for _ in range(len(metrics_to_log)):
                    self.batch.popleft()
            except Exception as err:
                warnings.warn(str(err))
            time.sleep(METRIC_ACCUMULATION_DURATION)

    def wait_log_metrics(self):
        stop_time = time.time()
        while self.batch and time.time() - stop_time < TIMEOUT_LOG_METRIC_BATCH:
            time.sleep(1)
        self._stop_batching()
