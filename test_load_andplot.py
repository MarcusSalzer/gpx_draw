import data_functions as fun
from timeit import timeit

CHECK_TIME = False

activities = fun.load_all_gpx("data/activities", sample=1)

fig = fun.plot_one_gpx(activities[0])

fig.show()


if CHECK_TIME:  
    N_CHECK = 3
    print("checking time...")
    load_time = timeit(
        lambda: fun.load_all_gpx("data/activities", sample=10), number=N_CHECK
    )/N_CHECK
    print("load time:", load_time)
