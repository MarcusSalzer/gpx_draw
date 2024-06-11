from timeit import default_timer
import pandas as pd
from statistics import mean, stdev
import math


def round_significant(value, digits=3):
    """Round a float-like to a number of significant digits"""

    if value == 0:
        return 0
    else:
        scale = math.pow(10, digits - math.ceil(math.log10(abs(value))))

        return round(value * scale) / scale


def time_functions(
    functions,
    table_outputs: dict = None,
    iterations=1,
    format_time=False,
    out_format=None,
    verbose=True,
):
    """Create a table of timing results for a list of functions.

    ## Parameters
    - functions: iterable of functions to test
    - table_outputs (dict[str,int]): names and indicies of outputs to include in table
    - iterations (int): number of times to measure. If >1, returns mean, std, max.
    - format_time (bool): use only 3 significant digits
    - out_format (function): applied to all outputs included in table
    - verbose (bool): print progress

    ## Returns
    - results (DataFrame): table of timing results and selected function outputs
    - outputs (dict): all outputs from all functions, indexed by function name.

    """

    if format_time:

        def form_t(x):
            return round_significant(x, 3)
    else:

        def form_t(x):
            return x

    results = {}
    outputs = {}
    for f in functions:
        name = f.__name__
        if verbose:
            print(f"running {name}")

        t_start = default_timer()
        out = f()
        time = default_timer() - t_start

        if iterations <= 1:
            results[name] = {"time (s)": form_t(time)}
        else:
            time = [time]
            for _ in range(iterations):
                t_start = default_timer()
                out = f()
                time.append(default_timer() - t_start)
            results[name] = {
                "mean(time)": form_t(mean(time)),
                "std(time)": form_t(stdev(time)),
                "max(time)": form_t(max(time)),
            }

        if out:  # collect outputs
            outputs[name] = out

            for k in table_outputs:
                if out_format:
                    results[name][k] = out_format(out[table_outputs[k]])
                else:
                    results[name][k] = out[table_outputs[k]]

    return pd.DataFrame.from_dict(results, orient="index"), outputs
