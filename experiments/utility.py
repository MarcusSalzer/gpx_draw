from timeit import default_timer
import pandas as pd

def time_functions(
    functions,
    table_outputs: dict = {"output": 0},
    out_format=None,
    verbose=False,
):
    """Time a list of functions and provide timings and results"""
    results = {}
    outputs = {}
    for f in functions:
        name = f.__name__
        if verbose:
            print(f"running {name}")
        t_start = default_timer()
        out = f()

        time = default_timer() - t_start

        results[name] = {"time (s)": time}

        if out:  # collect outputs
            outputs[name] = out

            for k in table_outputs:
                if out_format:
                    results[name][k] = out_format(out[table_outputs[k]])
                else:
                    results[name][k] = out[table_outputs[k]]

    return pd.DataFrame.from_dict(results, orient="index"), outputs
