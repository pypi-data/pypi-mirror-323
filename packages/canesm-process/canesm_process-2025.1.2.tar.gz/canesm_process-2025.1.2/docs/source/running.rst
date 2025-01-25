.. running

Running a DAG
-------------

The DAG defines the processes that need to be ran, the inputs and outputs and their relationships, 
but is agnostic on how this is executed. For that we use a ``Runner``. A simple runner that works 
well with netcdf, xarray and numpy is ``dask``. To process our dag using dask:

.. code-block:: python
   
   from canproc.runners import DaskRunner
   runner = DaskRunner()
   output = runner.run(dag)