import pytest

from chancy import Worker, Chancy, Job, Queue, QueuedJob


def job_to_run():
    return


def job_that_fails():
    raise ValueError("This job should fail.")


@pytest.mark.asyncio
async def test_basic_job(chancy: Chancy, worker: Worker):
    """
    Simply test that we can push a job, and it runs successfully.
    """
    await chancy.declare(
        Queue(
            "default",
            concurrency=1,
        ),
        upsert=True,
    )
    ref = await chancy.push(Job.from_func(job_to_run))
    job = await chancy.wait_for_job(ref, timeout=30)
    assert job.state == QueuedJob.State.SUCCEEDED


@pytest.mark.asyncio
async def test_failing_job(chancy: Chancy, worker: Worker):
    """
    Test that a job that fails will be marked as failed.
    """
    await chancy.declare(
        Queue(
            "default",
            concurrency=1,
        ),
        upsert=True,
    )
    ref = await chancy.push(Job.from_func(job_that_fails))
    job = await chancy.wait_for_job(ref, timeout=30)
    assert job.state == QueuedJob.State.FAILED
