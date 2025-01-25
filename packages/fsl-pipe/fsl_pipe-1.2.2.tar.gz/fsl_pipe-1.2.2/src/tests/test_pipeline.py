from fsl_pipe import Pipeline, In, Out, Ref, testing, Var
from fsl_pipe.job import OutputMissing, InputMissingPipe
from file_tree import FileTree
import pytest
import os
import warnings
import sys
from fsl.utils.tempdir import tempdir
import shutil
import numpy as np


def test_linear_pipe():
    tree = FileTree.from_string("A.txt\nB.txt\nC.txt\n")
    pipe = Pipeline()

    @pipe
    def gen_A(A: Out):
        testing.touch(A)

    @pipe
    def gen_B(B: Out):
        testing.touch(B)

    @pipe
    def gen_C(A: In, B: In, C: Out):
        testing.touch(C)

    jobs = pipe.generate_jobs(tree)
    assert len(jobs.jobs) == 3

    job_a = jobs.filter(['A'])
    assert len(job_a.jobs) == 1
    assert job_a.jobs[0].kwargs == {'A': 'A.txt'}

    assert len(jobs.filter(['A', 'B']).jobs) == 2
    assert len(jobs.filter(['C']).jobs) == 3
    for method in ("local", "dask"):
        with tempdir():
            jobs.run(method)
            assert os.path.exists("A.txt")
            assert os.path.exists("B.txt")
            assert os.path.exists("C.txt")


def test_iter_pipe():
    tree = FileTree.from_string("{subject}\n    A.txt\n    B.txt\nC.txt\n")
    tree.placeholders['subject'] = ['01', '02']
    pipe = Pipeline()

    @pipe
    def gen_A(A: Out, subject: Var(no_iter=True)):
        for fn in A.data.flatten():
            testing.touch(fn)

    @pipe
    def gen_B(B: Out, subject: Var):
        testing.touch(B)

    @pipe
    def gen_C(A: In, B: In, C: Out, subject: Var(no_iter=True)):
        testing.touch(C)

    jobs = pipe.generate_jobs(tree)
    assert len(jobs.jobs) == 4

    job_a = jobs.filter(['A'])
    assert job_a.jobs == jobs.filter(['*/A.txt']).jobs
    assert len(job_a.jobs) == 1
    assert list(job_a.jobs[0].kwargs['A'].data) == ['01/A.txt', '02/A.txt']
    assert job_a.jobs[0].kwargs['subject'].key == 'subject'
    assert job_a.jobs[0].kwargs['subject'].index == (0, 1)
    assert job_a.jobs[0].kwargs['subject'].value == ('01', '02')

    # Testing filtering with pattern matching
    assert set(jobs.jobs) == set(jobs.filter(['C.txt']).jobs)
    assert len(jobs.filter(['01/?.txt']).jobs) == 2

    assert len(jobs.filter(['A', 'B']).jobs) == 3
    for idx, s, job in zip(range(2), ('01', '02'), jobs.filter(['B']).jobs):
        assert job.kwargs['B'] == s + '/B.txt'
        assert job.kwargs['subject'].key == 'subject'
        assert job.kwargs['subject'].index == idx
        assert job.kwargs['subject'].value == s
    assert len(jobs.filter(['C']).jobs) == 4
    job_c = jobs.filter(['C']).jobs[-1]
    assert job_c.kwargs['C'] == 'C.txt'
    assert list(job_c.kwargs['A'].data) == ['01/A.txt', '02/A.txt']
    assert list(job_c.kwargs['B'].data) == ['01/B.txt', '02/B.txt']
    s = job_c.kwargs['subject']
    assert s.key == 'subject'
    assert s.index == (0, 1)
    assert s.value == ('01', '02')


def test_submit_check():
    Pipeline(default_submit={'jobtime': '10'})
    with pytest.raises(ValueError):
        Pipeline(default_submit={'unknown_parameter': '10'})


def test_template_glob():
    pipe = Pipeline()
    tree = FileTree.from_string("""
    base_file.txt
    base_other_file.txt
    base_f0.txt
    base_f1.txt
    unrelated.txt
    """)

    @pipe
    def function(all_base: Ref("base_*"), all_idx: Out("base_f?"), empty: Ref("no_files*")):
        assert len(all_base) == 4
        for t in all_base:
            assert all_base[t] == t + '.txt'

        assert len(all_idx) == 2
        for t in all_idx:
            assert all_base[t] == t + '.txt'
            assert all_idx[t] == t + '.txt'

        assert len(empty) == 0

    job = pipe.scripts[0]
    assert job.filter_templates(True, tree.template_keys()) == {'base_f1', 'base_f0'}
    assert job.filter_templates(False, tree.template_keys()) == set()

    with pytest.raises(OutputMissing):
        pipe.generate_jobs(tree).run()

def test_optional_input():
    for _ in range(20):
        for optional in (False, True):
            for skip_missing in (False, True):
                for target in ({"combined"}, None, {"combined"}):
                    with tempdir():
                        pipe = Pipeline()

                        @pipe(kwargs=dict(input=In('dataB'), output=Out('procB')))
                        @pipe(kwargs=dict(input=In('dataA'), output=Out('procA')))
                        def process_input(input, output):
                            assert os.path.exists(input)
                            testing.touch(output)

                        @pipe
                        def combined_processed_data(procA: In, procB: In(optional=optional), combined: Out):
                            with open(combined, 'w') as f:
                                f.write(f"{os.path.exists(procA)} {os.path.exists(procB)}")

                        testing.touch("dataA")
                        tree = FileTree.from_string("""
                        dataA
                        procA
                        dataB
                        procB
                        combined
                        """)

                        if skip_missing or (optional and target is not None):
                            if skip_missing and target is None:
                                jobs = pipe.generate_jobs(tree).filter(target, skip_missing=True)
                            else:
                                jobs = pipe.generate_jobs(tree).filter(target, skip_missing=True)
                            expected_njobs = 1 if target is None else 0
                            if optional:
                                expected_njobs = 2
                            assert len(jobs) == expected_njobs
                            jobs.run()
                            if optional:
                                assert os.path.exists("combined")
                                assert os.path.exists("procA")
                                assert not os.path.exists("procB")
                                assert open("combined", "r").read() == "True False"
                            else:
                                assert not os.path.exists("combined")
                                if target is None:
                                    assert os.path.exists("procA")
                                else:
                                    assert not os.path.exists("procA")
                            assert not os.path.exists("procB")
                        else:
                            with pytest.raises(InputMissingPipe):
                                with warnings.catch_warnings():
                                    warnings.simplefilter("ignore")
                                    pipe.generate_jobs(tree).filter(target, skip_missing=False)
                        
def test_batching():
    pipe = Pipeline()

    @pipe(batch="base", submit={"jobtime": 1, "jobram": 100})
    def gen_A(A: Out, subject: Var):
        testing.touch(A)

    @pipe(batch="base", submit={"jobtime": 3, "jobram": 10})
    def gen_B(A: In, B: Out):
        testing.touch(B)

    @pipe(submit={"coprocessor": "cuda"})
    def gen_C(B: In, C: Out):
        testing.touch(C)

    @pipe(batch="base", submit={"jobtime": 9})
    def gen_D(B: In, C: In, D:Out):
        testing.touch(D)

    @pipe(batch="base", submit={"jobtime": 81})
    def gen_E(A: In, E: Out):
        testing.touch(E)

    @pipe(batch="base")
    def gen_F(D: In, F:Out):
        testing.touch(F)

    @pipe(batch="base", no_iter="subject", submit={"jobtime": 300})
    def combine(F: In, G: Out):
        testing.touch(G)

    tree = FileTree.from_string("""
    subject=01,02

    sub-{subject}
        A.txt
        B.txt
        C.txt
        D.txt
        E.txt
        F.txt
    G.txt
    """)


    for use_placeholders in (False, True, ["subject"], ["session"]):
        placeholders_used = use_placeholders in (True, ["subject"])
        for use_label in (False, True):
            for only_connected in (True, False):
                jobs = pipe.generate_jobs(tree)
                assert len(jobs) == 13
            
                batches = jobs.batch(use_label=use_label, only_connected=only_connected, use_placeholders=use_placeholders)

                (n_expected, expected_times, expected_names) = {
                    (False, False, False): (3, {None, 170, 318}, {"base_gen_a-gen_b-gen_e", "gen_c", "base_combine-gen_d-gen_f"}),
                    (False, True, False): (4, {None, 170, 318}, {"base_gen_a-gen_b-gen_e", "gen_c_subject-01", "gen_c_subject-02", "base_combine-gen_d-gen_f"}),
                    (False, False, True): (5, {None, 85, 318}, {"base_gen_a-gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_combine-gen_d-gen_f"}),
                    (False, True, True): (5, {None, 85, 318}, {"base_gen_a-gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_combine-gen_d-gen_f"}),
                    (True, False, False): (7, {None, 9, 85, 300}, {"base_gen_a-gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                    (True, True, False): (7, {None, 9, 85, 300}, {"base_gen_a-gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                    (True, False, True): (7, {None, 9, 85, 300}, {"base_gen_a-gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                    (True, True, True): (7, {None, 9, 85, 300}, {"base_gen_a-gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                }[(placeholders_used, use_label, only_connected)]

                assert len(batches) == n_expected

                jobtimes = set(batch.submit_params.get("jobtime", None) for batch in batches.jobs)
                assert jobtimes == expected_times

                jobrams = set(batch.submit_params.get("jobram", None) for batch in batches.jobs)
                assert jobrams == {None, 100}

                jobnames = set(batch.job_name() for batch in batches.jobs)
                assert jobnames == expected_names

                with tempdir():
                    os.mkdir("sub-01")
                    testing.touch("sub-01/A.txt")

                    jobs = pipe.generate_jobs(tree).filter(None)
                    assert len(jobs) == 12

                    batches = jobs.batch(use_label, only_connected=only_connected, use_placeholders=use_placeholders)

                    (n_expected, expected_times, expected_names) = {
                        (False, False, False): (3, {None, 169, 318}, {"base_gen_a-gen_b-gen_e", "gen_c", "base_combine-gen_d-gen_f"}),
                        (False, True, False): (4, {None, 169, 318}, {"base_gen_a-gen_b-gen_e", "gen_c_subject-01", "gen_c_subject-02", "base_combine-gen_d-gen_f"}),
                        (False, False, True): (6, {None, 3, 81, 85, 318}, {"gen_b_subject-01", "gen_e_subject-01", "gen_c_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_combine-gen_d-gen_f"}),
                        (False, True, True): (6, {None, 3, 81, 85, 318}, {"gen_b_subject-01", "gen_e_subject-01", "gen_c_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_combine-gen_d-gen_f"}),
                        (True, False, False): (7, {None, 9, 84, 85, 300}, {"base_gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                        (True, True, False): (7, {None, 9, 84, 85, 300}, {"base_gen_b-gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                        (True, False, True): (8, {None, 3, 9, 81, 85, 300}, {"gen_b_subject-01", "gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                        (True, True, True): (8, {None, 3, 9, 81, 85, 300}, {"gen_b_subject-01", "gen_e_subject-01", "gen_c_subject-01", "base_gen_d-gen_f_subject-01", "base_gen_a-gen_b-gen_e_subject-02", "gen_c_subject-02", "base_gen_d-gen_f_subject-02", "combine"}),
                    }[(placeholders_used, use_label, only_connected)]

                    assert len(batches) == n_expected

                    jobtimes = set(batch.submit_params.get("jobtime", None) for batch in batches.jobs)
                    assert jobtimes == expected_times

                    expected_times_scaled = {None if t is None else t * 2 for t in expected_times}
                    jobtimes_scaled = set(batch.submit_params.get("jobtime", None) for batch in batches.copy().scale_jobtime(2.).jobs)
                    assert jobtimes_scaled == expected_times_scaled

                    jobnames = set(batch.job_name() for batch in batches.jobs)
                    assert jobnames == expected_names

                    jobrams = set(batch.submit_params.get("jobram", None) for batch in batches.jobs)
                    if only_connected or placeholders_used:
                        assert jobrams == {None, 10, 100}
                    else:
                        assert jobrams == {None, 100}

                    batches.run()
                    assert os.path.exists("G.txt")

                    os.remove("G.txt")
                    shutil.rmtree("sub-01")
                    os.mkdir("sub-01")
                    testing.touch("sub-01/A.txt")

                    jobs.filter(["G"]).run()
                    assert os.path.exists("G.txt")
    for use_ram in (False, True):
        with tempdir():
            os.mkdir("sub-01")
            testing.touch("sub-01/A.txt")

            stages = pipe.generate_jobs(tree).split_pipeline(split_on_ram=use_ram)
            assert len(stages) == 4 if use_ram else 3

            for (b, params, stage) in stages:
                print(b, params)
                stage.run()
            assert os.path.exists("G.txt")


def test_split_pipeline_without_inputs(mocker):
    mocked = mocker.patch("fsl_pipe.job.FileTarget.exists")
    pipe = Pipeline()

    @pipe(batch="base", submit={"jobtime": 3, "jobram": 10})
    def gen_B(A: In, B: Out):
        testing.touch(B)

    @pipe(batch="base", submit={"jobtime": 8, "jobram": 100})
    def gen_C(B: In, C: Out):
        testing.touch(C)

    tree = FileTree.from_string(
        """
        subject = 01,02
        sub-{subject}
            A.txt
            B.txt
            C.txt
        """
    )

    stages = pipe.generate_jobs(tree).split_pipeline(split_on_ram=True)
    assert len(stages) == 2
    assert stages[0][1] == {"jobtime": 6, "jobram": 10}
    assert stages[1][1] == {"jobtime": 16, "jobram": 100}

    stages = pipe.generate_jobs(tree).split_pipeline(split_on_ram=False)
    assert len(stages) == 1
    assert stages[0][1] == {"jobtime": 22, "jobram": 100}

    mocked.assert_not_called()



def test_linking():
    pipe = Pipeline()

    @pipe
    def gen_group(group_file: Out, group: Var):
        with open(group_file, 'w') as f:
            f.write(group.value)

    @pipe
    def gen_subject(subject_file: Out, group: Var, subject: Var):
        with open(subject_file, 'w') as f:
            f.write(group.value + " " + subject.value)

    tree = FileTree.from_string("""
    group = control, control, disease
    subject=01,02,03
    &LINK group, subject

    group-{group}
        group_file.txt                                
        sub-{subject}
            subject_file.txt
    """)

    jobs = pipe.generate_jobs(tree)
    assert len(jobs) == 5

    with tempdir():
        jobs.run()
        with open("group-control/group_file.txt", "r") as f:
            assert f.readlines() == ["control"]
        with open("group-control/sub-01/subject_file.txt", "r") as f:
            assert f.readlines() == ["control 01"]
        with open("group-control/sub-02/subject_file.txt", "r") as f:
            assert f.readlines() == ["control 02"]
        assert not os.path.exists("group-control/sub-03/subject_file.txt")

        with open("group-disease/group_file.txt", "r") as f:
            assert f.readlines() == ["disease"]
        with open("group-disease/sub-03/subject_file.txt", "r") as f:
            assert f.readlines() == ["disease 03"]
        assert not os.path.exists("group-disease/sub-01/subject_file.txt")
        assert not os.path.exists("group-disease/sub-02/subject_file.txt")


def test_no_filter_with_ref():
    """
    Test a bug where files marked with Ref were considered output files that cannot be produced.
    """
    tree = FileTree.from_string("""
        ref.txt
        output.txt
    """)

    pipe = Pipeline()

    @pipe
    def job_with_ref(ref: Ref, output: Out):
        pass

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        pipe.generate_jobs(tree).filter(None)


def test_var():
    """
    Test a bug where files marked with Ref were considered output files that cannot be produced.
    """
    tree = FileTree.from_string("""
        {single_value}.txt (single)
        {mult_value}.txt (mult)
    """).update(single_value="value", mult_value=["a", "b"])

    pipe = Pipeline()

    @pipe(kwargs=dict(
            single=Out("mult"),
            single_value=Var("mult_value"),
    ))
    @pipe
    def write_value(single: Out, single_value: Var):
        with open(single, "w") as f:
            f.write(single_value.value)

    jobs = pipe.generate_jobs(tree)

    with tempdir():
        jobs.run()
        for txt in ["value", "a", "b"]:
            with open(f"{txt}.txt", "r") as f:
                assert f.readlines() == [txt]


def test_link_template_placeholder():
    tree = FileTree.from_string("""
    name=a,b
    in
        a.txt
        b.txt
    intermediate
        {name}.txt (inter)
    final (final_dir)
        {name}.txt (final)
    """)

    pipe = Pipeline()

    @pipe
    def write_value(a: Out):
        with open(a, "w") as f:
            f.write("a")

    @pipe
    def write_value(b: Out):
        with open(b, "w") as f:
            f.write("b")

    @pipe
    def copy_file(inter: In, final: Out):
        shutil.copyfile(inter, final)

    for name in tree.placeholders["name"]:
        pipe(copy_file, kwargs=dict(inter=In(name), final=Out("inter")), placeholders=dict(name=name))

    jobs = pipe.generate_jobs(tree).filter(["final"])

    output = testing.rich_report(jobs)
    print(output)
    assert output.strip() == """
  Placeholders  
 with multiple  
    options     
┏━━━━━━┳━━━━━━━┓
┃ name ┃ value ┃
┡━━━━━━╇━━━━━━━┩
│ name │ a, b  │
└──────┴───────┘
.
├── final (final_dir)
│   └── {name}.txt (final) [0/2/0]
├── in
│   ├── a.txt [0/1/0]
│   └── b.txt [0/1/0]
└── intermediate
    └── {name}.txt (inter) [0/2/0]
""".strip()

    with tempdir():
        jobs.run()
        for directory in ["in", "intermediate", "final"]:
            for txt in ["a", "b"]:
                filename = f"{directory}/{txt}.txt"
                assert os.path.isfile(filename)
                with open(filename, "r") as f:
                    assert f.read().strip() == txt


def test_wildcards():
    tree = FileTree.from_string("""
        sub-{subject}
            input_{subject}*.txt (input)
            output_sub-{subject}.txt (output)
    """)

    pipe = Pipeline()

    @pipe
    def copy_value(input: In, output: Out):
        shutil.copy(input, output)

    with tempdir():
        for subject in ["A", "B", "C"]:
            os.mkdir(f"sub-{subject}")
        testing.touch("sub-A/input_A.txt")
        testing.touch("sub-B/input_B_old.txt")
        testing.touch("sub-C/input_C_use_this.txt")
        ftree = tree.update_glob("input")

        pipe.generate_jobs(ftree).run()

        for subject in ["A", "B", "C"]:
            os.path.exists(f"sub-{subject}/output_sub-{subject}.txt")


def test_get_matching_targets():
    """
    Test using glob-like filename patterns to select output files.
    """
    tree = FileTree.from_string(
        """
        subject=A,B,C
        session=01,02,10

        sub-{subject}
            ses-{session}
                A.txt
                B.txt
                folder
                    C.txt
        """
    )

    pipe = Pipeline()

    @pipe
    def write_value(A: Out, session: Var, subject: Var):
        with open(A, "w") as f:
            f.write(f"{subject.value} {session.value}")

    @pipe
    def copy_file(A: In, B: Out):
        shutil.copyfile(A, B)

    @pipe
    def copy_file(B: In, C: Out):
        shutil.copyfile(B, C)

    jobs = pipe.generate_jobs(tree)

    assert len(jobs) == 27
    assert len(jobs.filter("C")) == 27
    assert len(jobs.filter("A")) == 9
    assert len(jobs.filter(["A", "B"])) == 18

    assert len(jobs.filter("sub-A/ses-01/A.txt")) == 1
    assert len(jobs.filter("sub-A/ses-01/?.txt")) == 2
    assert len(jobs.filter("sub-A/ses-*/?.txt")) == 6
    assert len(jobs.filter("**/A.txt")) == 9
    with pytest.warns():
        assert len(jobs.filter("C.txt")) == 0
    assert len(jobs.filter("sub-A/**")) == 9

def test_parser():
    tree = FileTree.from_string(
        """
        subject=A,B,C
        session=01,02,10

        sub-{subject}
            ses-{session}
                A.txt
                B.txt
                folder
                    C.txt
        """
    )

    pipe = Pipeline()

    @pipe
    def write_value(A: Out, session: Var, subject: Var):
        with open(A, "w") as f:
            f.write(f"{subject.value} {session.value}")

    @pipe
    def copy_file(A: In, B: Out):
        shutil.copyfile(A, B)

    @pipe
    def copy_file(B: In, C: Out):
        shutil.copyfile(B, C)

    with tempdir():
        pipe.cli(tree, cli_arguments=[])

        assert os.path.exists("sub-A/ses-02/A.txt")
        assert os.path.exists("sub-B/ses-10/folder/C.txt")

    with tempdir():
        pipe.cli(tree, cli_arguments=["A"])

        assert os.path.exists("sub-A/ses-02/A.txt")
        assert os.path.exists("sub-B/ses-02/A.txt")
        assert not os.path.exists("sub-A/ses-10/folder/C.txt")
        assert not os.path.exists("sub-B/ses-10/folder/C.txt")

    with tempdir():
        pipe.cli(tree, cli_arguments=["B", "--subject=A"])

        assert os.path.exists("sub-A/ses-02/A.txt")
        assert not os.path.exists("sub-B/ses-02/A.txt")
        assert os.path.exists("sub-A/ses-02/B.txt")
        assert not os.path.exists("sub-B/ses-02/B.txt")
        assert not os.path.exists("sub-A/ses-10/folder/C.txt")
        assert not os.path.exists("sub-B/ses-10/folder/C.txt")

    with tempdir():
        pipe.cli(tree, cli_arguments=["sub-*/ses-01/folder/*", "--subject=A"])

        assert os.path.exists("sub-A/ses-01/A.txt")
        assert not os.path.exists("sub-A/ses-02/A.txt")
        assert os.path.exists("sub-A/ses-01/folder/C.txt")
        assert not os.path.exists("sub-A/ses-10/folder/C.txt")
        assert not os.path.exists("sub-B/ses-01/folder/C.txt")
        assert not os.path.exists("sub-B/ses-10/folder/C.txt")

    with tempdir():
        with pytest.warns():
            pipe.cli(tree, cli_arguments=["C.txt", "--subject=A"])

        assert not os.path.exists("sub-A/ses-01/A.txt")
        assert not os.path.exists("sub-A/ses-02/A.txt")
        assert not os.path.exists("sub-B/ses-01/folder/C.txt")
        assert not os.path.exists("sub-B/ses-10/folder/C.txt")