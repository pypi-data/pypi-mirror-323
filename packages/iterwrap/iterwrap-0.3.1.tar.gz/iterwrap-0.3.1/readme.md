Wrapper on an iterable to support interruption & auto resume, retrying and multiprocessing.

The code is tested on Linux.

# APIs

## iterate_wrapper

```python
def iterate_wrapper(
    func: Callable[Concatenate[IO, DataType, dict[str, Any], ParamTypes], ReturnType],
    data: Iterable[DataType],
    output: str | IO | None = None,
    restart=False,
    retry=5,
    on_error: Literal["raise", "continue"] = "raise",
    num_workers=1,
    bar=True,
    flush=True,
    total_items: int | None = None,
    run_name=__name__,
    envs: list[dict[str, str]] = [],
    vars_factory: Callable[[], dict[str, Any]] = lambda: {},
    *args: ParamTypes.args,
    **kwargs: ParamTypes.kwargs,
) -> Sequence[ReturnType] | None:

    """Wrapper on a processor (func) and iterable (data) to support multiprocessing, retrying and automatic resuming.

    Args:
        func: The processor function. It should accept the following argument patterns: data item only; output stream, data item; output stream, data item, vars. Additional args (*args and **kwargs) can be added in func, which should be passed to the wrapper. Within func, the output stream can be used to save data in real time. See `vars_factory` for the usage of `vars`.
        data: The data to be processed. It can be an iterable or a sequence. In each iteration, the data item in data will be passed to func.
        output: The output stream. It can be a file path, a file object or None. If None, no output will be written.
        restart: Whether to restart from the beginning.
        retry: The number of retries for processing each data item.
        on_error: The action to take when an exception is raised in func.
        num_workers: The number of workers to use. If set to 1, the processor will be run in the main process.
        bar: Whether to show a progress bar (package tqdm required).
        flush: Whether to flush the output stream after each data item is processed.
        total_items: The total number of items in data. It is required when data is not a sequence.
        run_name: The name of the run. It is used to construct the checkpoint file path.
        envs: Additional environment variables for each worker. This will be set before spawning new processes.
        vars_factory: A callable that returns a dictionary of variables to be passed to func. The factory will be called after each process is spawned and before entering the loop. For plain vars, include them in *args and **kwargs.
        *args: Additional positional arguments to be passed to func.
        **kwargs: Additional keyword arguments to be passed to func.

    Returns:
        A list of return values from func.
    """
```

## IterateWrapper

```python
class IterateWrapper(Generic[DataType]):
    def __init__(
        self,
        *data: Iterable[DataType],
        mode: Literal["product", "zip"] = "product",
        restart=False,
        bar=0,
        total_items: int | None = None,
        convert_type=list,
        run_name=__name__,
    ):
        """
        wrap some iterables to provide automatic resuming on interruption, no retrying and limited to sequence

        Args:
            data: iterables to be wrapped
            mode: how to combine iterables. 'product' means Cartesian product, 'zip' means zip()
            restart: whether to restart from the beginning
            bar: the position of the progress bar. -1 means no bar
            total_items: total items to be iterated
            convert_type: convert the data to this type
            run_name: name of the run to identify the checkpoint and output files
        """
```

# Examples

## iterate_wrapper

```python
from typing import IO
from time import sleep

from iterwrap import iterate_wrapper

def square(f_io: IO, item: int, fn: Callable[[float], float]):
    result = fn(item)
    f_io.write(f"{result}\n")

data = list(range(10))
num_workers = 3
iterate_wrapper(
    square,
    data,
    output="output.txt",
    num_workers=num_workers,
    fn=lambda x: x * x,
)

with open("output.txt") as f:
    print(f.read()) # [0, 1, 4, 9, ..., 81]
```

## IterateWrapper

Just the same as `tqdm.tqdm`.

```python
from iterwrap import IterateWrapper

data = [1, 2, 3]
results = []
for i in IterateWrapper(data):
    results.append(i * i)
print(results) # [1, 4, 9]
```
