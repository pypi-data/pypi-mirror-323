import click
import json
from canproc import DAG, merge
from canproc.runners import DaskRunner
from canproc.pipelines.pipelines import canesm_pipeline, Pipeline
import os
import logging
import yaml
from pathlib import Path


@click.command()
@click.argument("dags", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--scheduler",
    default="threads",
    help="The dask scheduler to be used, threads, processes or single-threaded",
)
def run(dags, scheduler):
    """Combine and run a series of DAGs.

    Example
    -------

    >>> canproc-run "load_region_data.json" "monthly_anomalies.json" "enso.json" "to_netcdf.json"

    """

    dag_list = []
    for filename in dags:
        dag_list.append(DAG(**json.load(open(filename, "r"))))

    dag = merge(dag_list)

    runner = DaskRunner(scheduler=scheduler)
    runner.run(dag)


@click.command()
@click.argument("config", nargs=1, type=click.Path(exists=True))
@click.argument("input", nargs=1, type=click.Path(exists=True))
@click.option(
    "--output",
    default=None,
    help="location of the output data",
)
@click.option(
    "--scheduler",
    default="threads",
    help="The dask scheduler to be used, threads, processes or single-threaded",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="print the created dag but do not run, useful for debugging",
)
def process_pipeline(config, input, output, scheduler, dry_run):
    """Run a data pipeline

    Example
    -------

    >>> canproc-pipeline "config.yaml" "/space/hall5/sitestore/..."

    """

    pipeline = Pipeline(config, input, output)
    dag = pipeline.render()

    if dry_run:  # useful for testing
        print(dag)
        return

    if output is None:
        output = input
    else:
        output = Path(output)

    for directory in pipeline.directories.values():
        os.makedirs(directory, exist_ok=True)

    # print(f'{dag}')
    runner = DaskRunner(scheduler=scheduler)
    runner.run(dag)
