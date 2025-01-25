from fsl_pipe import job, testing
from fsl.utils.tempdir import tempdir
import os
import pytest


def test_file_target_caching():
    """
    Ensure the same `FileTarget` is returned when requested multiple times
    """
    all_targets = {}
    t1 = job.get_target("A", all_targets)
    t2 = job.get_target("A", all_targets)
    assert t1 is t2
    assert len(all_targets) == 1

    t2 = job.get_target("./A", all_targets)
    assert t1 is t2
    assert len(all_targets) == 1

    t2 = job.get_target("./B", all_targets)
    assert t1 is not t2
    assert len(all_targets) == 2


def test_file_target_existence():
    """
    Test FileTarget existence check including caching
    """
    with tempdir():
        all_targets = {}
        t1 = job.get_target("A", all_targets)
        t2 = job.get_target("B", all_targets)
        assert not t1.exists()
        assert not t2.exists()

        testing.touch('A')
        assert not t1.exists()
        t1.reset_existence()
        assert t1.exists()


def test_one_job_pipeline():
    """
    Test a single job pipeline can run
    """
    with tempdir():
        def func(input, output):
            assert os.path.exists(input)
            testing.touch(output)

        all_targets={}
        t1 = job.get_target("A", all_targets)
        t2 = job.get_target("B", all_targets)
        torun = job.SingleJob(
            func, {'input': 'A', 'output': 'B'}, 
            submit_params={}, 
            input_targets=[t1],
            output_targets=[t2],
            optionals=[],
        )
        with pytest.raises(job.InputMissingRun):
            torun(job.RunMethod.local)

        testing.touch('A')
        job.get_target('A', all_targets).reset_existence()
        assert os.path.exists('A')
        torun(job.RunMethod.local)
        assert os.path.exists('B')


def test_two_job_pipeline():
    """
    Test a two jobs pipeline can run and figure out the dependencies
    """
    with tempdir():
        def func1(output):
            testing.touch(output)

        def func2(input, output):
            assert os.path.exists(input)
            testing.touch(output)

        all_targets={}
        t1 = job.get_target("A", all_targets)
        t2 = job.get_target("B", all_targets)
        torun1 = job.SingleJob(
            func1, {'output': 'A'}, 
            submit_params={}, 
            input_targets=[],
            output_targets=[t1],
            optionals=[],
        )
        torun2 = job.SingleJob(
            func2, {'input': 'A', 'output': 'B'}, 
            submit_params={}, 
            input_targets=[t1],
            output_targets=[t2],
            optionals=[],
        )
        with pytest.raises(job.InputMissingRun):
            torun2(job.RunMethod.local)

        for overwrite, overwrite_dependencies, njobs in [
            (False, False, 2),
            (False, True, 2),
            (True, False, 2),
            (True, True, 2),
        ]:
            all_jobs = ([], set())
            torun2.add_to_jobs(all_jobs, overwrite, overwrite_dependencies)
            assert len(all_jobs[0]) == njobs

        torun1(job.RunMethod.local)

        for overwrite, overwrite_dependencies, njobs in [
            (False, False, 1),
            (False, True, 2),
            (True, False, 1),
            (True, True, 2),
        ]:
            all_jobs = ([], set())
            torun2.add_to_jobs(all_jobs, overwrite, overwrite_dependencies)
            assert len(all_jobs[0]) == njobs

        torun2(job.RunMethod.local)
        assert os.path.exists('A')
        assert os.path.exists('B')

        for overwrite, overwrite_dependencies, njobs in [
            (False, False, 0),
            (False, True, 0),
            (True, False, 1),
            (True, True, 2),
        ]:
            all_jobs = ([], set())
            torun2.add_to_jobs(all_jobs, overwrite, overwrite_dependencies)
            assert len(all_jobs[0]) == njobs