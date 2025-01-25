from sgqlc.operation import Operation

from ML_management import variables
from ML_management.graphql import schema
from ML_management.graphql.schema import ExecutionJob
from ML_management.graphql.send_graphql_request import send_graphql_request
from ML_management.mlmanagement.batcher import Batcher
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.variables import DEFAULT_EXPERIMENT


class ActiveJob(ExecutionJob):
    """
    A context manager that allows for the execution of a task locally.

    This class provides a convenient way to run a job locally.

    """

    def __enter__(self):
        op = Operation(schema.Mutation)
        op.start_local_job(job_name=self.name)
        job_run_id = send_graphql_request(op=op, json_response=False).start_local_job
        variables.job_run_id = job_run_id
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        Batcher().wait_log_metrics()
        if exc_type:
            status = "FAILED"
        else:
            status = "SUCCESSFUL"
        op = Operation(schema.Mutation)
        op.stop_local_job(job_run_id=variables.job_run_id, status=status)
        try:
            _ = send_graphql_request(op=op, json_response=False).stop_local_job
        finally:
            variables.job_run_id = None


def start_local_job(
    job_name, experiment_name: str = DEFAULT_EXPERIMENT, visibility=VisibilityOptions.PRIVATE
) -> ActiveJob:
    """
    Create local job.

    Parameters
    ----------
    job_name: str | None
        Name of the new job. If not passed, it will be generated.
    experiment_name: str = "Default"
        Name of the experiment. Default: "Default"
    visibility: VisibilityOptions
        Visibility of this job to other users. Default: PRIVATE.

    Returns
    -------
    ActiveJob
        Active job.

    Usage:
        with start_local_job('my-beautiful-job') as job:
            mlmanagement.log_metric(...)
            mlmanagement.log_artifacts(...)
    """
    op = Operation(schema.Mutation)
    create_local_job = op.create_local_job(
        job_name=job_name, experiment_name=experiment_name, visibility=visibility.name
    )
    create_local_job.name()
    create_local_job.visibility()
    create_local_job.experiment.name()
    job = send_graphql_request(op=op, json_response=True)
    return ActiveJob(job["createLocalJob"])
