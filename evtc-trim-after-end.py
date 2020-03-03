#!/usr/bin/python3

# Removes everything after the LogEnd event from EVTC files.
# Has to be used on non-compressed logs, can be used to batch-process

# This can be useful for fixing broken logs with random trash data after the
# log end.

# Example usage:
#  ./evtc-trim-after-end.py 20190412-210528.evtc 20190420-204619.evtc
# Will create two files:
#  20190412-210528.evtc-mod
#  20190420-204619.evtc-mod


from sys import argv
import struct


def skip_bytes(f, result, n):
    for x in range(n):
        byte = f.read(1)
        if byte == b"":
            return False
        result.write(byte)
    return True


def read_byte(f, result):
    byte = f.read(1)
    result.write(byte)
    return byte


def read_int(f, result):
    data = f.read(4)
    result.write(data)
    value, = struct.unpack('i', data)
    return value


def trim_after_log_end(filename):
    print(f"Trimming data after log end from {filename}")
    with open(filename, "rb") as f:
        with open(filename + "-mod", "wb") as result:
            # Header
            skip_bytes(f, result, 12)
            revision = read_byte(f, result)
            assert revision == b"\x01", "Can only handle revision 1"
            print(f"Revision {revision}")
            skip_bytes(f, result, 3)

            # Agents
            agent_count = read_int(f, result)
            print(f"Agent count: {agent_count}")
            for _ in range(agent_count):
                skip_bytes(f, result, 96)

            # Skills
            skill_count = read_int(f, result)
            print(f"Skill count: {skill_count}")
            for _ in range(skill_count):
                skip_bytes(f, result, 68)

            # Combat items
            combatitem_count = 0
            while True:
                b = f.read(64)
                if (b == b""):
                    break
                state_change = b[56]
                result.write(b)
                combatitem_count += 1

                if (int(state_change) == 10):
                    print(f"LogEnd on item {combatitem_count}, ending")
                    break

            removed_combatitem_count = 0
            while True:
                b = f.read(64)
                if (b == b""):
                    break
                removed_combatitem_count += 1

            print(f"New combat item count: {combatitem_count}, "
                  + f"trimmed {removed_combatitem_count} items.")


for filename in argv[1:]:
    try:
        trim_after_log_end(filename)
    except Exception as e:
        print(e)
