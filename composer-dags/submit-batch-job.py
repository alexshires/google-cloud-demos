#  Copyright 2023 Google. This software is provided as-is, without warranty
#   or representation for any use or purpose. Your use of it is subject to your
#    agreement with Google.

from datetime import datetime
from airflow import DAG
from airflow.decorators import task


@task.virtualenv(
    task_id="virtualenv_batch",
    requirements=["google-cloud-batch==0.9.0"], # Todo track package until integrated into composer
    system_site_packages=True,
    # TODO: sadly need this to import local modules (batch_job_utils), even if it breaks the google-cloud setup - maybe another solution?
)
def batch_virtualenv():
    """
    runs a batch job form a virtual environment
    :return:
    """
    from time import sleep
    import uuid
    from batch_job_utils import create_container_job, get_job

    project_id = "XXXXX"  # TODO REPLACE WITH PROJECTID
    gcp_region = "us-central1"
    job_name = f"example-job-{str(uuid.uuid4())}"
    job = create_container_job(
        project_id=project_id, region=gcp_region, job_name=job_name
    )
    print(job_name)
    # wait for join to complete - really need to implewment as an operator
    res = None
    # TODO improve polling framework (with a vision to migrating to an operator)
    while True:
        job = get_job(project_id=project_id, region=gcp_region, job_name=job_name)
        print(job.status.state)
        # TODO can clearly implement a better assertion with the enums
        if (
            str(job.status.state) == "State.SUCCEEDED"
            or str(job.status.state) == "State.FAILED"
        ):
            print("finished")
            res = job
            break
        else:
            sleep(1)
    print(res)
    return str(res.status.State)


with DAG(
    "submit-batch-dag",
    schedule="@daily",
    default_args={"retries": 1},
    tags=["example"],
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    # Batch Job
    batch_task = batch_virtualenv()
