import fitdecode
import numpy as np


filepath = "data/activities/2023-12-23-14-40-24.fit"

required_message_types = [
    "file_id",
    "activity",
    "session",
    "record",
]

found_m = []

with fitdecode.FitReader(filepath) as fit:
    for frame in fit:
        # The yielded frame object is of one of the following types:
        # * fitdecode.FitHeader (FIT_FRAME_HEADER)
        # * fitdecode.FitDefinitionMessage (FIT_FRAME_DEFINITION)
        # * fitdecode.FitDataMessage (FIT_FRAME_DATA)
        # * fitdecode.FitCRC (FIT_FRAME_CRC)

        if frame.frame_type == fitdecode.FIT_FRAME_HEADER:
            print("header", frame)

        if frame.frame_type == fitdecode.FIT_FRAME_DATA:
            # Here, frame is a FitDataMessage object.
            # A FitDataMessage object contains decoded values that
            # are directly usable in your script logic.
            found_m.append(frame.name)

            if frame.name == "activity":
                print(frame.get_value(0))
                for i, field in enumerate(frame):
                    print(i, field.name, field.value)


found_m_unique = sorted(set(found_m))

ids = [found_m_unique.index(t) for t in found_m]
counts = np.bincount(ids)

print("\nCounts:\n")
for c, name in zip(counts, found_m_unique):
    print(name, ":", c)

print("total:", sum(counts))

## again
print("======")
fit = tuple(
    fitdecode.FitReader(
        filepath, check_crc=fitdecode.CrcCheck.RAISE, keep_raw_chunks=False
    )
)
print(len(fit))
print(fit[2])
