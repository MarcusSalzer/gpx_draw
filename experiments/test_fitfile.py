import fitdecode
import numpy as np


filepath = "data_test/15589755789_ACTIVITY.fit"

required_message_types = [
    "file_id",
    "activity",
    "session",
    "record",
]

found_m = []
record_m = []

with fitdecode.FitReader(filepath, check_crc=fitdecode.CrcCheck.RAISE) as fit:
    for frame in fit:
        # The yielded frame object is of one of the following types:
        # * fitdecode.FitHeader (FIT_FRAME_HEADER)
        # * fitdecode.FitDefinitionMessage (FIT_FRAME_DEFINITION)
        # * fitdecode.FitDataMessage (FIT_FRAME_DATA)
        # * fitdecode.FitCRC (FIT_FRAME_CRC)

        if frame.frame_type == fitdecode.FIT_FRAME_HEADER:
            print(frame)
        if frame.frame_type == fitdecode.FIT_FRAME_DATA:
            # Here, frame is a FitDataMessage object.
            # A FitDataMessage object contains decoded values that
            # are directly usable in your script logic.
            found_m.append(frame.name)

            if frame.name == "activity":
                print("\nACTIVITY:")
                for i, field in enumerate(frame):
                    print(i, field.name, field.value)

            # if frame.name == "device_settings":
            #     print("\nDEVICE SETTINGS:")
            #     for i, field in enumerate(frame):
            #         print(i, field.name, field.value)
            if frame.name == "event":
                print("\nEVENT:")
                for i, field in enumerate(frame):
                    print(i, field.name, field.value)
            if frame.name == "file_id":
                print("\nFILE ID:")
                for i, field in enumerate(frame):
                    print(i, field.name, field.value)
            if frame.name == "session":
                print("\nSESSION:")
                for i, field in enumerate(frame):
                    print(i, field.name, field.value)
            if frame.name == "sport":
                print("\nSPORT:")
                for i, field in enumerate(frame):
                    print(i, field.name, field.value)

            if frame.name == "record":
                record_m.append(frame)

found_m_unique = sorted(set(found_m))

ids = [found_m_unique.index(t) for t in found_m]
counts = np.bincount(ids)

print("\nCounts:\n")
for c, name in zip(counts, found_m_unique):
    print(name, ":", c)

print("total:", sum(counts))

print("\nCheck one record")
for i, field in enumerate(record_m[37]):
    print(i, field.name, field.value)
