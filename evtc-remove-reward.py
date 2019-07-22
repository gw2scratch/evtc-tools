#!/usr/bin/python3

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
    b = f.read(4)
    result.write(b)
    agent_count, = struct.unpack('i', b)
    return agent_count


def remove_reward(filename):
    print(f"Removing reward from {filename}")
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
            combatitem_count = 0
            while True:
                b = f.read(64)
                if (b == b""):
                    break
                activation = b[56]
                if (int(activation) == 17):
                    print(f"Reward on item {combatitem_count}, removing")
                else:
                    result.write(b)
                combatitem_count += 1
            print(f"Combat item count: {combatitem_count}")


for filename in argv[1:]:
    try:
        remove_reward(filename)
    except Exception as e:
        print(e)
