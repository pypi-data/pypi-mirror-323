from canproc.dag import DAGProcess, DAG
from canproc.pipelines.utils import OPERATION_MAP, UUID, AstParser
from typing import Callable
from pathlib import Path
from typing import Literal
from typing_extensions import Self
import ast


class Variable:
    """
    Class to keep track of operations that have been applied to dataset.

    Example
    -------

    >>> variable = Variable('temperature')
    >>> variable.open('test/input_directory', engine='netcdf4')
    >>> variable.scale(10.0)
    >>> variable.write('test/output_directory')
    >>> dag = variable.render()
    """

    def __init__(self, name: str, get_filename: Callable | None = None, from_file: bool = True):
        """Initialization

        Parameters
        ----------
        name : str
            name given to the variable. Used for generating function names
        get_filename : Callable | None, optional
            method used to get the filename for opening the dataset, by default None
        from_file : bool, optional
            whether the file is derived from a on-disk source (True) or computed (False), by default True
        """

        self.name: str = name  # used for node names
        self.var_name: str = name  # used for renaming and branching
        self.current_uuid: UUID = UUID()
        self._nodes: list[str] = []
        self.output: list[str] = []
        self.tags: dict[str, str] = {}
        self.operations: list[DAGProcess] = []
        self.from_file = from_file
        self.allowed_operations = [
            "shift",
            "scale",
            "divide",
            "rename",
            "destination",
            "mask",
        ]
        self._output_filename: str | None = None
        self.current_label = None
        self.chunks = {"time": 96}

        if get_filename is not None:
            self.get_filename = get_filename
        else:
            self.get_filename = lambda input_dir, var: (input_dir / f"{var}.nc").as_posix()

    @property
    def output_filename(self) -> str:
        if self._output_filename is None:
            return f"{self.name}.nc"
        else:
            return self._output_filename

    def destination(self, value: str):
        self._output_filename = value

    def next(self, label: str | None = None) -> str:
        """get the next node ID

        Parameters
        ----------
        label : str | None, optional
            include an optional label in the ID, by default None

        Returns
        -------
        str
            ID of the next node
        """
        self.current_uuid = UUID()
        self.current_label = label
        self._nodes.append(self.current())
        return self.current()

    def current(self, custom_label: str | None = None) -> str:
        """current node ID

        Returns
        -------
        str
            current ID
        """
        tmp = f"{self.name}"

        if self.current_label:
            tmp += f"_{self.current_label}"

        if custom_label is not None:
            tmp += f"_{custom_label}"

        tmp += f"-{self.current_uuid.short}"
        return tmp

    def add_tag(self, tag: str):
        """Add a tag that can be used to reference the current node.

        Parameters
        ----------
        tag : str
        """
        self.tags[tag] = self.current()

    def get_tag(self, tag: str | list[str], allow_fallback: bool = False) -> str:
        """get the ID of the node with the tag. If a list is provided then return the first valid.

        Parameters
        ----------
        tag : str | list[str]
        allow_fallback : bool, optional
            Return a previous node if the tag cannot be found. By default False

        Returns
        -------
        str
            node ID

        Raises
        ------
        KeyError
            If tag cannot be found
        """
        if tag is None:
            tag = [None]
        elif isinstance(tag, str):
            tag = [tag]

        for tg in tag:
            if tg == "latest":
                return self.current()
            try:
                return self.tags[tg]
            except KeyError:
                pass

        if not allow_fallback:
            raise KeyError(f"could not find tag: {tag} in {self.tags}")

        try:
            return self.tags["transforms"]
        except KeyError:
            return self.tags["native"]

    def render(self) -> DAG:
        """create a DAG from the variable operations

        Returns
        -------
        DAG
        """
        return DAG(dag=self.operations, output=self.output)

    def store_output(self, tag: str | list[str] | None = None, custom_label: str | None = None):
        """append a node ID to the list of DAG outputs.

        Parameters
        ----------
        tag : str | list[str] | None, optional
            Add output from a tag instead of the current ID, by default None
        """
        if tag is not None:
            self.output.append(self.get_tag(tag))
        self.output.append(self.current(custom_label=custom_label))

    def dag(
        self,
        dag: dict,
        reuse_from_tag: str | list[str] | None = None,
        variables: dict[str, Self] | None = None,
        allow_fallback: bool = True,
    ):
        """add a DAG to the list of operations

        Parameters
        ----------
        dag : dict
        reuse_from_tag : str | list[str] | None, optional
            start from the tag, by default None
        variables : dict[str, Self] | None, optional
            list of variables that may be used by the dag, by default None

        """

        # replace dag inputs with correct names.
        if variables:
            for node in dag["dag"]:
                new_args = []
                for arg in node["args"]:
                    if isinstance(arg, list):
                        arg = [
                            (
                                variables[a].get_tag(reuse_from_tag, allow_fallback=allow_fallback)
                                if a in variables.keys()
                                else a
                            )
                            for a in arg
                        ]
                    else:
                        if arg in variables:
                            arg = variables[arg].get_tag(
                                reuse_from_tag, allow_fallback=allow_fallback
                            )
                    new_args.append(arg)
                node["args"] = new_args

        # this may have already been done if self in variables
        try:
            input = self.get_tag(reuse_from_tag, allow_fallback=allow_fallback)
        except KeyError:  # computed variables won't necessarily have a previous state
            pass
        else:
            # update arguments to match input variable
            input_nodes = [el for el in dag["dag"] if self.name in el["args"]]
            for in_node in input_nodes:
                in_node["args"] = [input if self.name == x else x for x in in_node["args"]]

        # rename internal node edges to avoid collisions between pipelines
        # TODO: this doesn't properly handle kwargs but we can't simply do a replace like in args
        # due to operations such as xr.self.rename({"ST": "TAS"}) where the kwarg overlaps with args
        # but doesn't need replacement
        # NOTE: not clear if replacing kwargs would generally work anyway for local dask,
        # see: https://github.com/dask/dask/issues/3741
        int_nodes = [el for el in dag["dag"] if self.name not in el["args"]]
        for node in int_nodes:
            name = node["name"]
            new_name = self.next(f"{name}")
            for sub_node in dag["dag"]:
                args = sub_node["args"]
                if name in args:
                    args[args.index(name)] = new_name
                    node["name"] = new_name

        # update names and output to match output
        out_nodes = [el for el in dag["dag"] if dag["output"] in el["name"]]
        if len(out_nodes) > 1:
            raise ValueError("only one output node is allowed")

        output = self.next(f'{out_nodes[0]["name"]}')
        out_nodes[0]["name"] = output
        dag["output"] = output
        for process in dag["dag"]:
            self.operations.append(DAGProcess(**process))

    ##################################################################
    #   convenience functions provided for simplifying yaml format
    ##################################################################

    def _add_op(
        self,
        function: str,
        args: list | None = None,
        kwargs: dict = {},
        short_name: str | None = None,
    ):
        """append an operation to the variable starting from the last node"""
        input = [self.current()]
        output = self.next(short_name)
        if args is not None:
            input += args
        self.operations.append(
            DAGProcess(name=output, function=function, args=input, kwargs=kwargs)
        )

    def sort(self, sortby: str = "time"):
        self._add_op("xr.self.sortby", kwargs={"variables": sortby}, short_name="sort")

    def open(self, input_dir, engine: str, assume_single_var: bool = True):

        # TODO: filename should probably be optional arg and created only if None
        filename = self.get_filename(input_dir, self.name)
        kwargs = {"engine": engine, "parallel": engine == "netcdf4", "chunks": self.chunks}
        if not assume_single_var:
            kwargs["vars"] = [self.name]

        output = self.next("open")
        self.operations.append(
            DAGProcess(name=output, function="open_mfdataset", args=[filename], kwargs=kwargs)
        )

    def write(self, output_dir: str, **kwargs):

        filename = None
        if "destination" in kwargs:
            filename = kwargs.pop("destination")

        if filename is None:
            filename = self.output_filename

        input = [self.current(), (Path(output_dir) / filename).as_posix()]
        output = self.current("to_netcdf")
        self.operations.append(
            DAGProcess(name=output, function="to_netcdf", args=input, kwargs=kwargs)
        )
        self.store_output(custom_label="to_netcdf")

    def rename(self, new_name: str):
        if self._output_filename is None:
            self._output_filename = f"{new_name}.nc"

        self._add_op("rename", args=[new_name], short_name="rename")
        self.var_name = new_name

    def shift(self, shift: float | int):
        self._add_op("xr.add", args=[shift], short_name="shift")

    def scale(self, scale: float | int):
        self._add_op("xr.mul", args=[scale], short_name="scale")

    def divide(self, div: float | int):
        # it seems xarray doesn't do this automatically, so turn
        # scalar division into a multiplication for better speed.
        if isinstance(div, float) | isinstance(div, int):
            div = 1 / div
            op = "xr.mul"
        else:
            op = "xr.truediv"

        self._add_op(op, args=[div], short_name="divide")

    def resample(
        self,
        resolution: str,
        method: Literal["mean", "min", "max", "std"] = "mean",
        reuse_from_tag: str | list[str] | None = None,
    ):

        pandas_res_map = {"monthly": "MS", "daily": "1D", "yearly": "YS"}
        resolution = pandas_res_map[resolution]

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next(f"resample_{resolution}")
        self.operations.append(
            DAGProcess(
                name=output, function="xr.self.resample", args=[input], kwargs={"time": resolution}
            )
        )

        input = self.current()
        output = self.next("mean")
        self.operations.append(
            DAGProcess(
                name=output, function=f"xr.self.{method}", args=[input], kwargs={"dim": "time"}
            )
        )

    def area_mean(
        self,
        reuse_from_tag: str | list[str] | None = None,
    ):

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next("area_mean")
        self.operations.append(DAGProcess(name=output, function=f"area_mean", args=[input]))

    def zonal_mean(
        self,
        reuse_from_tag: str | list[str] | None = None,
    ):

        input = self.get_tag(reuse_from_tag, allow_fallback=True)
        output = self.next("zonal_mean")
        self.operations.append(DAGProcess(name=output, function=f"zonal_mean", args=[input]))

    def mask(
        self,
        mask: Self,
        reuse_from_tag: str | list[str] | None = None,
    ):
        self._add_op(
            "mask_where",
            args=[mask.get_tag(tag=reuse_from_tag, allow_fallback=True)],
            short_name="mask",
        )

    def operator(
        self, a: Self, b: Self, operation: str, reuse_from_tag: str | list[str] | None = None
    ):
        output = self.next(f"{operation}")
        self.operations.append(
            DAGProcess(
                name=output,
                function=operation,
                args=[a.get_tag(reuse_from_tag), b.get_tag(reuse_from_tag)],
            )
        )

    def from_formula(
        self,
        formula: str,
        variables: dict[str, Self],
        reuse_from_tag: str | list[str] | None = None,
    ):
        """Create a DAG from a formula string. Each variable should be the
        name of a variable in the stage. Brackets () can be used for order
        of operations.

        Parameters
        ----------
        formula : str
            Formula as a string
        variables : dict[str, Self]
            dictionary of variables that will be used to create the actual DAG.
            The keys should align with `var` in the formula str.
        reuse_from_tag : str | list[str] | None, optional
            If provided, the variable at `tag` is used, by default None

        """

        tree = ast.parse(formula)
        dag = AstParser().build_dag(tree)
        self.dag(dag, variables=variables, reuse_from_tag=reuse_from_tag)

    def branch_from_variable(self, variable: Self, reuse_from_tag: str | list[str] | None = None):
        output = self.next()
        self.operations.append(
            DAGProcess(
                name=output,
                function="xr.self.rename",
                args=[variable.get_tag(reuse_from_tag, allow_fallback=True)],
                kwargs={variable.var_name: self.var_name},
            )
        )
