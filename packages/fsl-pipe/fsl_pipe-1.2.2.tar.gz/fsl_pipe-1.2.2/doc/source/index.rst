Welcome to fsl-pipe's documentation!
=====================================

Framework to build pipelines in a declarative manner based on FileTrees.
fsl-pipe has the following features:

   - The directory tree containing the input, intermediate, and output files are defined separately from the pipeline code in the convenient `file-tree <https://open.win.ox.ac.uk/pages/fsl/file-tree/>`_ format
   - The pipeline writer only defines the individual recipes in regular python code (e.g., how to convert file A into file B or file B into C), which fsl-pipe will stitch together into a complete pipeline.
   - Users can run part of the pipeline by defining which files they actually want to produce.
   - By default, the pipeline will skip any jobs for which the output files already exist.
   - Jobs can be run locally in sequence as normal python functions or in parallel by submitting to a cluster queue (using `fsl_sub <https://git.fmrib.ox.ac.uk/fsl/fsl_sub>`_) or by using `dask <https://dask.org/>`_.

Install using
::

   pip install fsl-pipe

Typical usage:

.. code-block:: python

    from fsl_pipe import pipe, In, Out, Ref, Var

    @pipe
    def job(input_file: In, output_file: Out):
        # code to convert `input_file` to `output_file`

    pipe.cli()  # runs command line interface

For the tutorial, select "Fsl-pipe tutorial" below. Other resources:

   - `Gitlab repository with code <https://git.fmrib.ox.ac.uk/fsl/fsl-pipe>`_
   - `Example diffusion MRI pipeline <https://git.fmrib.ox.ac.uk/ndcn0236/fsl-pipe-example>`_

.. toctree::
   :maxdepth: 3

   tutorial
   fsl-pipe