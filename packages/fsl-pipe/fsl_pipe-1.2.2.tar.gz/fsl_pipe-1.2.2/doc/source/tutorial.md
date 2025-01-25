# Fsl-pipe tutorial
Building a pipeline in fsl-pipe consists of three steps:
1. Define the directory structure containing the pipeline output in a FileTree.
2. Write python functions representing individual steps in the pipeline.
3. Run the CLI interface.

## Exploring the command line interface (CLI)
### Basic pipeline runs
To start with a trivial example, copy the following to a text file called "pipe.py":
```python
from file_tree import FileTree
from fsl_pipe import pipe, In, Out

tree = FileTree.from_string("""
A.txt
B.txt
C.txt
""")

@pipe
def gen_A(A: Out):
    with open(A, 'w') as f:
        f.write('A\n')

@pipe
def gen_B(B: Out):
    with open(B, 'w') as f:
        f.write('B\n')

@pipe
def gen_C(A: In, B: In, C: Out):
    with open(C, 'w') as writer:
        with open(A, 'r') as reader:
            writer.writelines(reader.readlines())
        with open(B, 'r') as reader:
            writer.writelines(reader.readlines())

if __name__ == "__main__":
    pipe.cli(tree)
```

This is a fully functioning pipeline with 3 jobs:
1. Generating the file A.txt containing the text "A".
2. Generating the file B.txt containing the text "B".
3. Generating the file C.txt with the concatenation of A and B

Let's check the command line interface by running
```bash
python pipe.py --help
```

This will generate the following output:
```
usage: Runs the pipeline [-h] [-m {local,submit,dask}] [-o] [-d] [-j JOB_HOLD] [--datalad] [templates ...]

positional arguments:
  templates             Set to one or more template keys or file patterns (e.g., "*.txt"). Only these templates/files will be produced. If not provided all templates will be produced (A, B, C).

optional arguments:
  -h, --help            show this help message and exit
  -m {local,submit,dask}, --pipeline_method {local,submit,dask}
                        method used to run the jobs (default: local)
  -o, --overwrite       If set overwrite any requested files.
  -d, --overwrite_dependencies
                        If set also overwrites dependencies of requested files.
  -j JOB_HOLD, --job-hold JOB_HOLD
                        Place a hold on the whole pipeline until job has completed.
  --skip-missing SKIP_MISSING
                        If set skip running any jobs depending on missing data. This replaces the
                        default behaviour of raising an error if any required input data is missing.
  -q, --quiet           Suppresses the report on what will be run (might speed up starting up the
                        pipeline substantially).
  -b, --batch           Batch jobs based on submit parameters and pipeline labels before running them.
  -g, --gui             Start a GUI to select which output files should be produced by the pipeline.
```

The main argument here is the `templates`, which allow you to select which of the potential pipeline output files
you want to produce. By default, the full pipeline will be run.
Let's try this out by producing just "B.txt":
```bash
python pipe.py B
# Alternative using file pattern
# python pipe.py B.txt
```
Only a single job in the pipeline is run, which is sufficient to produce "B.txt".
The other files ("A.txt" and "C.txt") are not required and hence their jobs are not run.
Note that either the template key could be given ("B") or the full filename ("B.txt").
The full filename can also contain shell-style wildcards (e.g., "*" or "?") to match multiple files.

Let's now request file "C.txt":
```bash
python pipe.py C
```
In this case two jobs are run. To generate "C.txt", the pipeline first needs to create "A.txt".
Although, "B.txt" is also required, that file already existed and hence is not regenerated.
In other words, fsl-pipe is lazy.
It only runs what is strictly necessary to produce the requested output files.

So far, we have defined our targets based on the template keys in the file-tree.
However, we can also define the output files directly based on the filename, for example:
```bash
python pipe.py C.txt
```
Unix-style filename patterns can be used to define multiple target filenames. For example,
- `python pipe.py *.txt`: produce all text files in the top-level directory
- `python pipe.py **/*.pdf`: produce any PDFs, no matter where they are in the output file-tree.
- `python pipe.py **/summary.dat`: produce any file named "summary.dat" irrespective of where it is defined in the file-tree.
- `python pipe.py subject-A/**`: produce any files in the `subject-A` directory.

Alternatively, the output files can be selected using a graphical user interface (GUI).
This GUI can be started using the `-g/--gui` flag.
The GUI is terminal-based, which means that it will work when connecting to a computing cluster over SSH.
"fsl-pipe-gui" needs to be installed for the GUI to run (`conda/pip install fsl-pipe-gui`).
More details on the GUI can be found at [https://git.fmrib.ox.ac.uk/fsl/fsl-pipe-gui](the fsl-pipe-gui gitlab repository).

When defining output files in this way, the pipeline will run *only* those jobs that are necessary to produce the user-define outputs.
These jobs might produce intermediate or additional files that do not match the output pattern.
So, even though you did not explicitly request these files, `fsl-pipe` will still produce them.

### Overwriting existing files
If we want to regenerate any files we can use the `-o/--overwrite` and/or `-d/--overwrite-dependencies` flags.
The former will just overwrite the files that we explicitly request (in addition to generating any missing dependencies):
```bash
python pipe.py C -o
```
This will just run the single job to generate "C.txt".

The `-d/--overwrite-dependencies` will also overwrite any dependencies of the requested files:
```bash
python pipe.py C -do
```
This will rerun the full pipeline overwriting all of the files.

Setting the `-d/--overwrite-dependencies` flag does not imply the `-o/--overwrite` flag.
If the overwrite flag is not provided, the dependencies are only rerun if "C.txt" does not exist.
So, the following does nothing:
```bash
python pipe.py C -d
```

However, after removing "C.txt" the same command will rerun the full pipeline:
```bash
rm C.txt
python pipe.py C -d
```

### Understanding the stdout
fsl-pipe writes some helpful information to the terminal while running
First, we can see a file-tree representation looking like:
```
.
├── A.txt [1/0/0]
├── B.txt [1/0/0] 
└── C.txt [0/1/0]
```
This shows the *relevant* part of the file-tree for this specific pipeline run.
The numbers indicate the number of files matching the template that are involved in this pipeline.
The first number (in red) shows the number of files that will be overwritten.
The second number (in yellow) shows the number of new files that will be produced.
The third number (in blue) shows the number of files that will be used as input.

After this file-tree representation, fsl-pipe will report which (if any) jobs were run or submitted.

## Iterating over subjects or other placeholders
Let's adjust the pipeline above to iterate over multiple subjects:
```python
from file_tree import FileTree
from fsl_pipe import pipe, In, Out, Var

tree = FileTree.from_string("""
subject = 01, 02
A.txt
sub-{subject}
    B.txt
    C.txt
""")

@pipe
def gen_A(A: Out):
    with open(A, 'w') as f:
        f.write('A\n')

@pipe
def gen_B(B: Out, subject: Var):
    with open(B, 'w') as f:
        f.write(f'B\n{subject.value}\n')

@pipe
def gen_C(A: In, B: In, C: Out):
    with open(C, 'w') as writer:
        with open(A, 'r') as reader:
            writer.writelines(reader.readlines())
        with open(B, 'r') as reader:
            writer.writelines(reader.readlines())

if __name__ == "__main__":
    pipe.cli(tree)
```
Copy this text to "pipe.py". 
You might also want to remove the output from the old pipeline (```rm *.txt```).

There are two changes here to the pipeline
The main one is with the file-tree:
```python
tree = FileTree.from_string("""
subject = 01, 02
A.txt
sub-{subject}
    B.txt
    C.txt
""")
```
Here we have defined two subjects ("01" and "02").
For each subject we will get a subject directory
(matching the subject ID with the prefix "sub-"), 
which will contain "B.txt" and "C.txt".
The file "A.txt" is not subject-specific, which we can see because it is outside of the subject directory.

The second change is with the function generating "B.txt",
which now takes the subject ID as an input and writes it into "B.txt".
```python
@pipe
def gen_B(B: Out, subject: Var):
    with open(B, 'w') as f:
        f.write(f'B\n{subject.value}\n')
```

Let's run this pipeline again:
```bash
python pipe.py C
```

There is now also a table in the terminal output listing the subject IDs:
```
 Placeholders with  
  multiple options  
┏━━━━━━━━━┳━━━━━━━━┓
┃ name    ┃ value  ┃
┡━━━━━━━━━╇━━━━━━━━┩
│ subject │ 01, 02 │
└─────────┴────────┘
.
├── A.txt [0/1/0]
└── {subject}
    ├── B.txt [0/2/0]
    └── C.txt [0/2/0] 
```

In total, 5 jobs got run now. 
One to create "A.txt" and two each for generating 
"B.txt" and "C.txt" for both subjects.
Feel free to check that the files "B.txt" and "C.txt"
contain the correct subject IDs.

When iterating over multiple placeholder values,
the command line interface is expanded to allow one to set the parameters.
In this case, we now have an additional flag to set the subject ID:
```
  --subject SUBJECT [SUBJECT ...]
                        Use to set the possible values of subject to the selected values (default: 01,02)
```
We can use this, for example, to rerun only subject "01":
```
python pipe.py C -do --subject=01
```

An alternative way to just produce the files for a single subject, is to explicitly match the files that need to be produced.
For example, the following will reproduce all the files matching "02/*.txt" (namely, "02/B.txt" and "02/C.txt"):
```
python pipe.py "02/*.txt" -o
```
The quotes around 02/*.txt are required here to prevent the shell from expanding the filenames.

Note that when defining the function to generate "C.txt",
there is no distinction made between the input that depends
on subject ("{subject}/B.txt") and the one that does not ("A.txt"):
```
@pipe
def gen_C(A: In, B: In, C: Out):
    ...
```
fsl-pipe figures out which of the input or output files
depend on the subject placeholder based on file-tree.
This is particularly useful when considering some 
input configuration file, which could be either made global or 
subject-specific just by changing the file-tree without altering
the pipeline itself.

## Concatenating/merging across subjects or other placeholders
By default, when any input or output template depends on
some placeholder in the file-tree (e.g., subject ID) the pipeline
will run that job for each subject independently.
However, in some cases we might not want this default behaviour,
for example if we are merging or comparing data across subjects.
In that case we can use "no_iter":
```python
from file_tree import FileTree
from fsl_pipe import pipe, In, Out, Var

tree = FileTree.from_string("""
subject = 01, 02
A.txt
sub-{subject}
    B.txt
    C.txt
merged.txt
""")

@pipe
def gen_A(A: Out):
    with open(A, 'w') as f:
        f.write('A\n')

@pipe
def gen_B(B: Out, subject: Var):
    with open(B, 'w') as f:
        f.write(f'B\n{subject.value}\n')

@pipe
def gen_C(A: In, B: In, C: Out):
    with open(C, 'w') as writer:
        with open(A, 'r') as reader:
            writer.writelines(reader.readlines())
        with open(B, 'r') as reader:
            writer.writelines(reader.readlines())

@pipe(no_iter=['subject'])
def merge(C: In, merged: Out):
    with open(merged, 'w') as writer:
        for fn in C.data:
            with open(fn, 'r') as reader:
                writer.writelines(reader.readlines())

if __name__ == "__main__":
    pipe.cli(tree)
```
Again there are two changes. 
First, we added a new file "merged.txt" to the file-tree.
This file will contain the concatenated text
from all the subject-specific "C.txt", which is defined by adding a new job to the pipeline:
```python
@pipe(no_iter=['subject'])
def merge(C: In, merged: Out):
    with open(merged, 'w') as writer:
        for fn in C.data:
            with open(fn, 'r') as reader:
                writer.writelines(reader.readlines())
```
Here the "no_iter" flag tells fsl-pipe that this function
should not iterate over the subject ID and rather pass on
all of subject-specific "C.txt" filenames, so that we can iterate over them within the function.

## Writing your own pipeline
### Importing fsl-pipe
A pipeline script will typically start by importing fsl-pipe:
```python
from fsl_pipe import pipe, In, Out, Ref, Var
```
Here `pipe` is an empty pipeline already initialized for you.
Using this pipeline is fine for scripts,
however in a python library we strongly recommend using
```python
from fsl_pipe import Pipeline, In, Out, Ref, Var
pipe = Pipeline()
```
This ensures you work on your own pipeline without interfering
with any user-defined pipelines or pipelines in other python
libraries.

### Adding functions to the pipeline
The next step is to wrap individual python functions:
```python
@pipe
def myfunc(input_file: In, other_input: In, output_file: Out, reference_file: Ref, placeholder_value: Var, some_config_var=3):
```
Here we use the python [typing syntax](https://docs.python.org/3/library/typing.html) to define what different keyword arguments are:
- Any input files (i.e., files that need to exist before this function can run) are marked with `In`.
- Any output files (i.e., files that are expected to exist after the function runs) are marked with `Out`.
- Reference files are marked with `Ref`. These will be extracted from the file-tree like input or output files, but their existence is not checked at any point and  they do not form part of the pipeline build.
- Placeholder values (e.g., subject ID used above) are marked with `Var`.

fsl-pipe will determine which jobs to run based on the inputs (`In`)
and outputs (`Out`) produced by all the functions added to the pipeline.

Alternatively, these keyword argument definitions can be set
directly when adding the functions to the pipeline.
This will override any definitions set as type hints.
This can be useful when wrapping a pre-existing function.
For example, if we want to create a job that copies "A" to "B":
```
from shutil import copyfile
pipe(copyfile, kwargs={'src': In('A'), 'dst': Out('B')})
```
Here we use one new feature, namely that
we can explicitly set the template key (for `In`, `Out`, or `Ref`) or placeholder (for `Var`) by using syntax like (`In(<template name>)`).
So, `'src': In('A')` indicates that the keyword argument `src` expected in the `copyfile` function should be mapped to the template "A" in the file-tree.
If the template or placeholder name is not explicitly set,
it defaults to the name of the keyword argument 
(which is the behaviour we have been using so far).

### What is passed into the functions?
The default behaviour is to pass in filenames as a string.
This is what happens for keywords marked with `In`, `Out`, or `Ref`.

For keywords marked with `Var` a named tuple is returned with three elements:
- `key`: string containing the name of the placeholder.
- `index`: integer containing the index of the placeholder value (zero-based).
- `value`: the actual placeholder value.

This changes when "no_iter" is used. 
In that case for some of the templates or placeholders, there might be multiple variables that need to be passed in.

For placeholders with multiple values the `index` and `value` elements in the named tuple will be tuples rather than individual values.

For templates with multiple values the data will be passed in as an [xarray DaraArray](https://docs.xarray.dev/en/stable/user-guide/data-structures.html). 
This is similar to a numpy array, but the axes are named (with the placeholder `key`) and can be indexed based on the placeholder values.  A good way to access individual filenames is to use the placeholder key and values returned by a keyword marked by `Var`:
```python
@pipe
def write_all_subject_ids(output: Out, subject: Var(no_iter=True)):
    for subject_id in subject.value:
        # select the filename corresponding to this subject ID
        fn = Out.sel({subject.key: subject_id}).item()

        # write the subject ID to the that subject's output file
        with open(fn, 'w') as f:
            f.write(subject_id)
```

### Submitting jobs to the cluster
By default `fsl-pipe` will submit jobs to the cluster if available. 
This can be overriden on the command line using the flag:
```
  -m {local,submit,dask}, --pipeline_method {local,submit,dask}
                        method used to run the jobs (default: submit)
```

The job submission will use `fsl_sub` under the hood.
You can set options for `fsl_sub` in two ways:
1. When creating the pipeline: ```pipe = PipeLine(default_submit={...})```
2. When adding a function to the pipeline: 
```python
@pipe(submit={...})
def func(...):
```

Function-specific keywords defined in step 2 will take precedence over pipeline-wide ones defined in step 1.
Similarly, to the function keyword arguments, any submit argument referring to `Ref` will be replaced by 
the filename matching the template and those referring to `Var` will be replaced by the placeholder value.
For example, ```pipe = Pipeline(default_submit=dict(logdir=Ref('log')))``` will write the pipeline log files
to the `log` template in the file-tree.

The submit keywords will be passed on to `fsl_sub.submit`.
A list of possible keywords can be found in the [fsl_sub documentation](https://git.fmrib.ox.ac.uk/fsl/fsl_sub#fsl_subsubmit).

### Adjusting the default pipeline interface
So far we have run our pipelines using `pipe.cli`, which produces the default `fsl-pipe` command line interface.
Users might want to create their own command line interface. 
This can be particularly useful if you want to have which flags
There are several options for doing so, depending on your use case
#### Customising the existing command line interface

This can be done by defining one's own argument parser:
```python
from argparser import ArgumentParser
parser = ArgumentParser(description="<my pipeline descriptor>")
parser.add_argument("--<my_flag>", help="<my argument descriptor>")
pipe.default_parser(tree, parser=parser)  # adds the default fsl-pipe arguments
args = parser.parse_args()
# do something based on `args.my_flag` (e.g., `pipe.configure` to set keyword arguments in individual jobs)
pipe.run_cli(args, tree)
```
Note that this still requires the pipeline and filetree to already be fully defined by the time the command line gets read.

#### Creating one's own custom command line interface
In this case the command line interface can be run before creating the pipeline or reading the FileTree.
Any tool can be used to read the command line.
After creating the pipeline and FileTree based on the user-provided arguments.

The pipeline developer then needs to reproduce the code in `pipe.run_cli` to actually run the pipeline.
Alternatively, `pipe.run_cli` can be called with an object (e.g., `ArgParser.Namespace`) with the default fsl-pipe arguments. The required objects are described in the `pipe.run_cli` docstring.

## Merging or extending existing pipelines
Let's consider the situations where somebody has written some amazing pipeline processing some data for a single subject.
As part of this pipeline they will have created a Pipeline object (called "amazing_pipe") and a file-tree stored in the file "amazing_pipe.tree", which looks something like
```
input_data.dat
input_config.conf
... (lots of processed data)
```

Now, we want to run this pipeline on our own data, which has multiple subjects.
The first step will be to write our own file-tree, which describes where to find the input data ("my_data/sub-{subject}/raw/sub-{subject}_input.data" in our case) and where to put the result from the pipeline ("my_data/sub-{subject}/from_pipeline" in our case):
```
my_config.conf
my_data
    sub-{subject}
        raw
            sub-{subject}_input.data (my_input)
        from_pipeline
            ->amazing_pipe (amazing_pipe)
        my_processing_output.dat
```

We can then process our multi-subject data using a script like this:
```
from file_tree import FileTree
from their_pipeline import amazing_pipe  # import the PipeLine object containing their pipeline
tree = FileTree.load("my_tree.tree")

pipe = amazing_pipe.move_to_subtree(
    "amazing_pipe",  # tell their pipeline that their templates are defined in "amazing_pipe" sub-tree
    {"input_data": "my_input", "input_config": "my_config"}  # except for the "input_data" and "input_config", which are explicitly mapped to the relevant templates in our file-tree
    )

# we can now add our own processing to the pipeline
@pipe
def my_processing(their_file: In("amazing_pipe/some_file"), my_processing_output: Out):
    ...

pipe.cli(tree)
```
This small script and file-tree have allowed us both to run the single-subject pipeline across multiple subjects and to add our own post-processing steps to the pipeline.

Other helpful functions to manage pipelines by other people are:
- `Pipeline.merge` which creates a new pipeline by merging the content of multiple pipelines.
- `pipe.find` or `pipe.remove` which allows one to find or remove specific functions in the pipeline. This can be useful if you want to replace a specific step in the pipeline using your own code.
- `pipe.configure` or `pipe.find(<func_name>).configure`, which allow you to set flags passed on as keyword arguments across the whole pipeline or in a specific function.

## Dealing with missing data
For this section we will consider two datasets per subject ("dataA" and "dataB"), which will be processed separately producing ("procA" and "procB") and then combined in a single dataset ("combined"). So, the filetree might look something like:
```
suject-{subject_id}
    A
        dataA
        procA
    B
        dataB
        procB
    combined
```

And the pipeline like:
```python
@pipe
process_A(dataA: In, procA: Out):
    ...

@pipe
process_B(dataB: In, procB: Out):
    ...

@pipe
combine_data(procA: In, procB: In, combined: Out):
    ...
```

However, for some subjects the input data for B (i.e., "dataB") is missing. By default this will cause an `InputMissingError` to be raised pointing you to one of the missing input files. You can change this behaviour using the `--skip-missing` flag or using optional inputs.
1. The `--skip_missing` flag (set as a keyword argument to `JobList.filter`) indicates that it is okay if some of the requested outputs cannot be produced due to missing inputs. If set, fsl-pipe will simply produce all the files it can and skip any jobs for which required inputs are missing.
2. Optional inputs can be used to indicate that a job should be run, even if those particular input files cannot be produced. So, by setting the "procB" input to "combine_data" as optional the pipeline developer can indicate that "combine_data" should still be run even for subjects where "dataB" does not exist. In code this will look like:
```
@pipe
combine_data(procA: In, procB: In(optional=True), combine: Out):
    ...
```

The table summarised which output files will actually be produced given (1) whether the `--skip-missing` flag has been set, (2) whether "procB" as been marked as optional in "combine_data", and (3) whether the requested outputs include all files (the default) or just the final "combined" data. "Only valid" indicates that these files will only be produced for subjects where the input "dataB" data is not missing.

| --skip-missing flag | optional procB | requested targets | error raised?               | procA produced? | procB produced? | combined produced? |
|---------------------|----------------|-------------------|-----------------------------|-----------------|-----------------|--------------------|
| N                   | N              | all               | yes: missing procB/combined | No              | No              | No                 |
| N                   | N              | combined          | yes: missing combined       | No              | No              | No                 |
| N                   | Y              | all               | yes; missing procB          | No              | No              | No                 |
| N                   | Y              | combined          | -                           | All             | Only valid      | All                |
| Y                   | N              | all               | -                           | All             | Only valid      | Only valid         |
| Y                   | N              | combined          | -                           | Only valid      | Only valid      | Only valid         |
| Y                   | Y              | all               | -                           | All             | Only valid      | All                |
| Y                   | Y              | combined          | -                           | All             | Only valid      | All                |

Output files can also be marked as optional. If all non-optional output files exist, the jobs is considered to have finished successfully and will not be rerun (unless `--overwrite` or `--overwrite-dependencies` flags are set).

## Fitting it all together
An example diffusion MRI pipeline using many of the features discussed here is available [here](https://git.fmrib.ox.ac.uk/ndcn0236/fsl-pipe-example).