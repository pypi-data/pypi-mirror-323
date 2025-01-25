[![Documentation](https://img.shields.io/badge/Documentation-fsl--pipe-blue)](https://open.win.ox.ac.uk/pages/fsl/fsl-pipe)
[![File-tree Documentation](https://img.shields.io/badge/Documentation-file--tree-blue)](https://open.win.ox.ac.uk/pages/fsl/file-tree)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6577069.svg)](https://doi.org/10.5281/zenodo.6577069)
[![Pipeline status](https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/badges/main/pipeline.svg)](https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/pipelines/latest)
[![Coverage report](https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/badges/main/coverage.svg)](https://open.win.ox.ac.uk/pages/fsl/fsl-pipe/htmlcov)

Declarative pipelines based on Filetrees. A pipeline is defined by:
- A file-tree, which defines the directory structure of the inputs and outputs of the pipeline. A tutorial on these file-trees is available [here](https://open.win.ox.ac.uk/pages/fsl/file-tree).
- A set of recipes describing how all the pipeline outputs are produced. A tutorial on writing these recipes is available [here](https://open.win.ox.ac.uk/pages/fsl/fsl-pipe).
Fsl-pipe will stitch these recipes together to produce any user-selected output files.
Resulting jobs will either run locally, run distributed using [dask](https://www.dask.org), or be submitted to a cluster using [fsl-sub](https://git.fmrib.ox.ac.uk/fsl/fsl_sub).

An example diffusion MRI pipeline using fsl-pipe with detailed comments is available [here](https://git.fmrib.ox.ac.uk/ndcn0236/fsl-pipe-example).

# Installation
```shell
pip install fsl-pipe
```

Any bug reports and feature requests are very welcome (see [issue tracker](https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/issues)).

# Setting up local test environment
This package uses [uv](https://docs.astral.sh/uv/) for project management.
You will need to install uv to develop this package.

First clone the repository:
```shell
git clone https://git.fmrib.ox.ac.uk/fsl/fsl-pipe.git
```

Then we can ask uv to set up the local envoriment.
```shell
cd fsl-pipe
uv sync
```

## Running tests
Tests are run using the [pytest](https://docs.pytest.org) framework.
This will already be available in the `uv` virtual environment.
```shell
uv run pytest src/tests
```

## Compiling documentation
The documentation is build using [sphinx](https://www.sphinx-doc.org/en/master/).
```shell
cd doc
uv run sphinx-build source build
open build/index.html
```

## Contributing
[Merge requests](https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/merge_requests) with any bug fixes or documentation updates are always welcome. 

For new features, please raise an [issue](https://git.fmrib.ox.ac.uk/fsl/fsl-pipe/-/issues) to allow for discussion before you spend the time implementing them.

## Releasing new versions
- Ensure CHANGELOG.md is up to date.
- Edit the version number on `pyproject.toml`
- Create a new tag for the version number
- Push to gitlab (including tags).
    - The pipeline from the tag will automatically publish fsl-pipe to [pypi](https://pypi.org/project/fsl-pipe/).
- Upload code on conda-forge using their automated release detection.
