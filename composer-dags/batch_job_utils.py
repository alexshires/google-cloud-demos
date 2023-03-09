#  Copyright 2023 Google. This software is provided as-is, without warranty
#   or representation for any use or purpose. Your use of it is subject to your
#    agreement with Google.

# Example python submit job - https://cloud.google.com/batch/docs/create-run-basic-job#python


def get_job(project_id: str, region: str, job_name: str):
    """
    Retrieve information about a Batch Job.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        region: name of the region hosts the job.
        job_name: the name of the job you want to retrieve information about.

    Returns:
        A Job object representing the specified job.
    """
    from google.cloud import batch_v1

    client = batch_v1.BatchServiceClient()

    return client.get_job(
        name=f"projects/{project_id}/locations/{region}/jobs/{job_name}"
    )


def list_jobs(project_id: str, region: str):
    """
    Get a list of all jobs defined in given region.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        region: name of the region hosting the jobs.

    Returns:
        An iterable collection of Job object.
    """
    from google.cloud import batch_v1

    client = batch_v1.BatchServiceClient()

    return client.list_jobs(parent=f"projects/{project_id}/locations/{region}")


def create_container_job(
    project_id: str, region: str, job_name: str, network: str, subnetwork: str
):
    """
    This method shows how to create a sample Batch Job that will run
    a simple command inside a container on Cloud Compute instances.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        region: name of the region you want to use to run the job. Regions that are
            available for Batch are listed on: https://cloud.google.com/batch/docs/get-started#locations
        job_name: the name of the job that will be created.
            It needs to be unique for each project and region pair.

    Returns:
        A job object representing the job created.
    """
    from google.cloud import batch_v1

    client = batch_v1.BatchServiceClient()

    # Define what will be done as part of the job.
    runnable = batch_v1.Runnable()
    runnable.container = batch_v1.Runnable.Container()
    runnable.container.image_uri = "gcr.io/google-containers/busybox"
    runnable.container.entrypoint = "/bin/sh"
    runnable.container.commands = [
        "-c",
        "echo Hello world! This is task ${BATCH_TASK_INDEX}. This job has a total of ${BATCH_TASK_COUNT} tasks.",
    ]

    # Jobs can be divided into tasks. In this case, we have only one task.
    task = batch_v1.TaskSpec()
    task.runnables = [runnable]

    # We can specify what resources are requested by each task.
    resources = batch_v1.ComputeResource()
    resources.cpu_milli = 2000  # in milliseconds per cpu-second. This means the task requires 2 whole CPUs.
    resources.memory_mib = 16  # in MiB
    task.compute_resource = resources

    task.max_retry_count = 2
    task.max_run_duration = "3600s"

    # Tasks are grouped inside a job using TaskGroups.
    # Currently, it's possible to have only one task group.
    group = batch_v1.TaskGroup()
    group.task_count = 4
    group.task_spec = task

    # network setup
    networkpolicy = batch_v1.AllocationPolicy.NetworkPolicy()
    networkinterface = batch_v1.AllocationPolicy.NetworkInterface()
    networkinterface.network = f"global/networks/{network}"
    networkinterface.subnetwork = f"regions/{region}/subnetworks/{subnetwork}"
    networkinterface.no_external_ip_address = True
    networkpolicy.network_interfaces = [networkinterface]

    # Policies are used to define on what kind of virtual machines the tasks will run on.
    # In this case, we tell the system to use "e2-standard-4" machine type.
    # Read more about machine types here: https://cloud.google.com/compute/docs/machine-types
    policy = batch_v1.AllocationPolicy.InstancePolicy()
    policy.machine_type = "e2-standard-4"
    instances = batch_v1.AllocationPolicy.InstancePolicyOrTemplate()
    instances.policy = policy
    allocation_policy = batch_v1.AllocationPolicy()
    allocation_policy.instances = [instances]
    allocation_policy.network = networkpolicy

    job = batch_v1.Job()
    job.task_groups = [group]
    job.allocation_policy = allocation_policy
    job.labels = {"env": "testing", "type": "container"}
    # We use Cloud Logging as it's an out of the box available option
    job.logs_policy = batch_v1.LogsPolicy()
    job.logs_policy.destination = batch_v1.LogsPolicy.Destination.CLOUD_LOGGING

    create_request = batch_v1.CreateJobRequest()
    create_request.job = job
    create_request.job_id = job_name
    # The job's parent is the region in which the job will run
    create_request.parent = f"projects/{project_id}/locations/{region}"

    return client.create_job(create_request)
