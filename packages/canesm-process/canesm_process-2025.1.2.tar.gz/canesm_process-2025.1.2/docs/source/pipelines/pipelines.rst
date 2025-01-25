.. pipelines


Pipeline Overview
-----------------

A pipeline is organized into :code:`stages`. Each option at the base 
level of a :code:`YAML` file is treated as a "stage". The only required 
stage is :code:`setup`. For more detailed information on stage options 
see :ref:`stages`


:code:`setup` Stage
*******************
Defines the directory structure, high level information like model version 
and the order in which the following :code:`stages` are evaluated.


Output directories
^^^^^^^^^^^^^^^^^^

Output directories are specified relative to the input directory.

.. code-block:: YAML

    setup:

      # defines where the output files for each stage will be written too.
      output_directories:
        monthly: "diags/monthly"
        daily: "diags/daily"
        rtd: "diags/rtd"
        variability: "diags/landon"



.. note::

   If a stage is not present in :code:`output_directories` the variables created in that stage will not be written to disc.


General information
^^^^^^^^^^^^^^^^^^^

.. code-block:: YAML

    setup:
      # general options that may affect how we process yaml->dag
      canesm_version: "6.0"
      file_format: "netcdf4"


Ordering Stages
^^^^^^^^^^^^^^^
This defines the order in which :code:`stages` are executed. For example, we may want to reuse data from the daily stage when
computing the monthly averages, in this case we could write:

.. code-block:: YAML

    setup:
      stages:
        - daily
        - monthly


If no data is reused between stages then this section can be omitted.


Reusing Stages
^^^^^^^^^^^^^^
To reuse results from a previous stage, the `reuse` keyword can be used

.. code-block:: YAML

    setup:
      stages:
        - transforms
        - daily
        - monthly

    transforms:
      variables:
        - GT:
            rename: TS

    daily:
      reuse: transforms
      variables:
        - GT

    monthly:
      reuse: daily
      variables:
        - GT
        - ST


This will tell the :code:`daily` stage to use the variables from the output of 
the :code:`transforms` stage and the :code:`monthly` stage to use the variables from 
the output of the :code:`daily` stage. This will be applied to all variables in 
the stage in this file. Variables that are not defined in prior stages, e.g. :code:`ST` here,
will fallback to earlier stages, in this case the raw data loaded from disc.


Resampling Stages
*****************

Resampling stages take variables and aggregrate them into coarser time bins. Currently the following stages are supported:

 - daily
 - monthly
 - yearly


.. code-block:: YAML
    
    # compute the monthly mean of `GT` and `ST` variables
    monthly:
      variables:
        - GT
        - ST


:code:`rtd` Stage
*****************
A default RTD stage that converts variables to yearly global average values.

.. code-block:: YAML

    # compute the global, annual mean of `GT` and `ST` variables
    rtd:
      variables:
        - GT
        - ST


Custom Stages
*************
Users can create their own stages. These do not perform any operations by default except saving the ouptut to a file.


.. code-block:: YAML

    # compute monthly standard deviation of the `GT` variable
    variability:
      variables:
        - GT:
            dag:
              dag:
                - name: resampled
                  function: xr.self.resample
                  args: [GT]
                  kwargs:
                    time: MS
                - name: monthly_std
                  function: xr.self.std
                  args: [resampled]
              output: monthly_std


If you would like to call your own functions in a pipeline, see :ref:`custom_functions`.