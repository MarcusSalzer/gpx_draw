import fitdecode
from timeit import timeit


filepath = "data/activities/2023-12-23-14-40-24.fit"  # 66kB
# filepath = "data/activities/2024-03-23-09-15-50.fit"  # 735kB

required_message_types = [
    "file_id",
    "activity",
    "session",
    "record",
]

print(
    "time to load (and list) a file:",
    round(
        timeit(
            lambda: list(
                fitdecode.FitReader(
                    filepath, check_crc=fitdecode.CrcCheck.RAISE, keep_raw_chunks=False
                )
            ),
            number=1,
        )
        * 1000
    ),
    "ms",
)


print("======")
found_m = []
fit = fitdecode.FitReader(
    filepath, check_crc=fitdecode.CrcCheck.RAISE, keep_raw_chunks=False
)
for frame in fit:
    if frame.frame_type == fitdecode.FIT_FRAME_DATA:
        # Here, frame is a FitDataMessage object.
        # A FitDataMessage object contains decoded values that
        # are directly usable in your script logic.
        found_m.append(frame.name)

        if frame.name == "activity":
            print(frame.get_value(0))
            for i, field in enumerate(frame):
                print(i, field.name, ":", field.value)

        if frame.name == "unknown_233":  # WTF is this data?
            for i, field in enumerate(frame):
                print(i, field.name, ":", field.value)

print("----")
print(set(found_m))
