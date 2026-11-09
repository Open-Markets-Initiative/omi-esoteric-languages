#!/usr/bin/env python3
"""Checks every generated program, and what it reads.

Two claims, of different sizes.

The first is that every program is a program: a loop opened is a loop closed. That is claimed
of every file here.

The second is that a program still reads what it read when it was generated. Where a frame was
published beside a program, this runs the program on that frame and compares what it writes
against the output recorded then. That recorded output was not taken on trust: before it was
published, the program's reading was held against the C# parser reading the same bytes through
the same model, field for field and in order. Neither the models nor that parser are here, so
what this can say is that nothing has changed since.

A program carries a frame for each message the capture corpus holds of its protocol, recorded
from the wire, and one laid out from its model besides. A program with no frame at all is one
that none could be proven for, and only the first claim is made about it.
"""

import pathlib
import sys

INSTRUCTIONS = set("><+-.,[]")

FRAME = ".frame"
WROTE = ".wrote"

# the stated dialect: cells of one byte that wrap, a tape of 65,536 of them, the pointer
# starting at the first and never leaving, and a read yielding zero once the input is spent
CELLS = 65536
STEPS = 100_000_000


def unbalanced(text):
    """The character of the first loop with no partner, or None when every loop has one."""
    opened = []

    for offset, character in enumerate(text):
        if character == "[":
            opened.append(offset)
        elif character == "]":
            if not opened:
                return offset
            opened.pop()

    return opened[0] if opened else None


def compiled(text):
    """The instructions alone, each loop's partner found once rather than searched for."""
    code = [character for character in text if character in INSTRUCTIONS]
    jumps = {}
    opened = []

    for at, character in enumerate(code):
        if character == "[":
            opened.append(at)
        elif character == "]":
            start = opened.pop()
            jumps[start] = at
            jumps[at] = start

    return code, jumps


def run(code, jumps, given):
    """What the program writes, and how much of the input it took."""
    tape = bytearray(CELLS)
    written = bytearray()
    cell = 0
    at = 0
    taken = 0
    steps = 0

    while at < len(code):
        steps += 1

        if steps > STEPS:
            raise RuntimeError(f"ran away: more than {STEPS:,} steps")

        character = code[at]

        if character == ">":
            cell += 1
            if cell >= CELLS:
                raise RuntimeError("stepped off the end of the tape")
        elif character == "<":
            cell -= 1
            if cell < 0:
                raise RuntimeError("stepped off the start of the tape")
        elif character == "+":
            tape[cell] = (tape[cell] + 1) & 0xFF
        elif character == "-":
            tape[cell] = (tape[cell] - 1) & 0xFF
        elif character == ".":
            written.append(tape[cell])
        elif character == ",":
            # a read once the input is spent yields zero and takes nothing, because there is
            # nothing there to take. Counted as a byte it made a program that reads to the end
            # of its input — a session does — look as though it had read past it
            if taken < len(given):
                tape[cell] = given[taken]
                taken += 1
            else:
                tape[cell] = 0
        elif character == "[":
            if tape[cell] == 0:
                at = jumps[at]
        elif character == "]":
            if tape[cell] != 0:
                at = jumps[at]

        at += 1

    return bytes(written), taken


def bytes_of(path):
    """A published frame, or a published output: hexadecimal, so that it can be read."""
    return bytes.fromhex("".join(path.read_text(encoding="utf-8").split()))


def parted(written, recorded):
    """Where two readings of the same frame first differ, said in a line."""
    for offset in range(min(len(written), len(recorded))):
        if written[offset] != recorded[offset]:
            return (f"wrote something else from byte {offset}: {written[offset:offset + 48]!r} "
                    f"where {recorded[offset:offset + 48]!r} was recorded")

    return f"wrote {len(written)} bytes where {len(recorded)} were recorded"


def reads(program, frame, wrote):
    """What is wrong with how the program reads its frame, or None."""
    given = bytes_of(frame)
    recorded = bytes_of(wrote)

    code, jumps = compiled(program.read_text(encoding="utf-8"))

    try:
        written, taken = run(code, jumps, given)
    except RuntimeError as fault:
        return str(fault)

    if taken != len(given):
        return f"read {taken} of the frame's {len(given)} bytes"

    if written != recorded:
        return parted(written, recorded)

    return None


def main():
    root = pathlib.Path(__file__).resolve().parent
    programs = sorted(root.rglob("*.bf"))

    if not programs:
        print("no programs found")
        return 1

    instructions = 0
    checked = 0
    refused = 0

    for program in programs:
        text = program.read_text(encoding="utf-8")
        instructions += sum(1 for character in text if character in INSTRUCTIONS)

        offset = unbalanced(text)

        if offset is not None:
            print(f"{program.relative_to(root)}: a loop at character {offset} has no partner")
            refused += 1
            continue

        # a program has a frame for each message the corpus holds a capture of, and one laid
        # out from its model besides, so there is no one frame to look for
        for frame in sorted(program.parent.glob(program.stem + ".*" + FRAME)):
            wrote = frame.with_suffix(WROTE)

            if not wrote.exists():
                print(f"{frame.relative_to(root)}: has no {WROTE} beside it")
                refused += 1
                continue

            checked += 1
            fault = reads(program, frame, wrote)

            if fault is not None:
                print(f"{frame.relative_to(root)}: {fault}")
                refused += 1

    print(f"{len(programs)} programs, {instructions:,} instructions, "
          f"{checked} frames read, {refused} refused")

    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())