#!/usr/bin/env python3
"""Checks every generated program, and what it reads.

Two claims, of different sizes.

The first is that every program is a program. For a Brainfuck program that is a loop opened
being a loop closed; for an Emojicode program it is a block opened being a block closed. That
is claimed of every file here, in either language.

The second is that a program still reads what it read when it was generated. Where a frame was
published beside a program, this runs the program on that frame and compares what it writes
against the output recorded then. That recorded output was not taken on trust: before it was
published, the program's reading was held against the C# parser reading the same bytes through
the same model, field for field and in order. Neither the models nor that parser are here, so
what this can say is that nothing has changed since.

A program carries a frame for each message the capture corpus holds of its protocol, recorded
from the wire, and one laid out from its model besides. A program with no frame at all is one
that none could be proven for, and only the first claim is made about it.

Running an Emojicode program needs its compiler, which is not here and is not something a
script can carry the way this one carries an interpreter of eight instructions. So those are
held to being programs, and to carrying their evidence: every frame beside one has the output
it should produce beside it too. Whether it produces it is settled where the compiler is, and
that language's own readme says so.
"""

import json
import pathlib
import sys

INSTRUCTIONS = set("><+-.,[]")

BRAINFUCK = ".bf"
EMOJICODE = ".emojic"

# the block markers of the second language, which are its brackets. Written as code points
# so that this script is plain ascii, and taken from the dialect the generator emits
OPENS = "\U0001F347"
CLOSES = "\U0001F349"

FRAME = ".frame"
WROTE = ".wrote"

# what is published and how it joins, stated once so that nothing has to take a file's
# name apart to find out
MANIFEST = "manifest.json"

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


def unclosed(text):
    """The offset of the first block with no partner, or None when every block has one.

    Counted over the characters themselves, which is sound here because a generated program
    puts neither marker inside a string or a comment: a string here holds a field's name or
    a new line, and a comment holds a protocol's name. A hand written program could defeat
    this, and nothing here is hand written.
    """
    opened = []

    for offset, character in enumerate(text):
        if character == OPENS:
            opened.append(offset)
        elif character == CLOSES:
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


def listed(root, programs):
    """Holds the manifest to the files: how many programs it lists, how many joins hold, and
    what is wrong.

    Three things. Everything it lists is here. Every program here is listed, so a program
    cannot be published without being said. And each join it states is true: what one of a
    venue's programs wrote is, byte for byte, what the next was given - which is the whole
    of the claim that a gateway, a market and a feed here are one venue."""
    path = root / MANIFEST

    if not path.exists():
        return 0, 0, [f"{MANIFEST}: is not here, so nothing says what is published or how it joins"]

    manifest = json.loads(path.read_text(encoding="utf-8"))
    faults = []
    stated = set()

    for program in manifest["programs"]:
        stated.add(program["path"])

        for named in [program["path"]] + [run[kind] for run in program["runs"] for kind in ("frame", "wrote")]:
            if not (root / named).exists():
                faults.append(f"{MANIFEST}: lists {named}, which is not here")

    for program in programs:
        relative = program.relative_to(root).as_posix()

        if relative not in stated:
            faults.append(f"{relative}: is here, and {MANIFEST} does not list it")

    joined = 0

    for join in manifest["joins"]:
        wrote, frame = root / join["wrote"], root / join["frame"]

        if not wrote.exists() or not frame.exists():
            faults.append(f"{MANIFEST}: joins {join['wrote']} to {join['frame']}, and one is not here")
        elif bytes_of(wrote) != bytes_of(frame):
            faults.append(f"{join['wrote']}: is not what {join['frame']} holds, so the two "
                          "programs do not join there")
        else:
            joined += 1

    return len(manifest["programs"]), joined, faults


def main():
    root = pathlib.Path(__file__).resolve().parent
    programs = sorted(root.rglob("*" + BRAINFUCK)) + sorted(root.rglob("*" + EMOJICODE))

    if not programs:
        print("no programs found")
        return 1

    instructions = 0
    characters = 0
    written = 0
    carried = 0
    checked = 0
    refused = 0

    for program in programs:
        text = program.read_text(encoding="utf-8")

        # the second language is held to being a program and no more, because running one
        # needs a compiler this script has no way to be
        if program.suffix == EMOJICODE:
            written += 1
            characters += len(text)

            offset = unclosed(text)

            if offset is not None:
                print(f"{program.relative_to(root)}: "
                      f"a block at character {offset} has no partner")
                refused += 1
                continue

            # the evidence is held to being whole even though it cannot be replayed here: a
            # frame with no recorded output beside it is a frame nothing can ever check
            for frame in sorted(program.parent.glob(program.stem + ".*" + FRAME)):
                wrote = frame.with_suffix(WROTE)

                if not wrote.exists():
                    print(f"{frame.relative_to(root)}: has no {WROTE} beside it")
                    refused += 1
                    continue

                carried += 1

            continue

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

    count, joined, faults = listed(root, programs)

    for fault in faults:
        print(fault)
        refused += 1

    print(f"{len(programs) - written} Brainfuck programs, {instructions:,} instructions, "
          f"{checked} frames read")
    print(f"{written} Emojicode programs, {characters:,} characters, "
          f"{carried} frames carried")
    print(f"{count} programs listed, {joined} joins held")
    print(f"{refused} refused")

    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())