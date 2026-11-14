#!/usr/bin/env python3
"""Compiles every program that needs a compiler, and replays it on the frames beside it.

check.py holds every program here to being a program, and runs the ones it can interpret. This
is the other half. A language whose only implementation is a compiler cannot be run by a
script carrying an interpreter in two hundred lines, so those programs are compiled and run
here instead, each on every frame published beside it, and held to writing what its .wrote
file records.

That recorded output was not taken on trust. Before it was published, the reading it records
was held against the C# parser reading the same bytes through the same model - field for
field, in order, and accounting for every byte. Neither the models nor that parser are in this
repository, so what this says is that the compiled program does what was recorded.

The compiler is taken from emojicodec on the path, or from the environment variable of that
name in upper case. With --required, a missing compiler is a failure; without it, this says
what it would have run and stops, so that running it on a machine with no toolchain does not
look like a pass.
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

EXTENSION = ".emojic"
COMPILER = "emojicodec"
LANGUAGE = "Emojicode"

FRAME = ".frame"
WROTE = ".wrote"


def kept(program):
    """The folder a program's runs are kept in: runs/ for a venue's, frames/ for a protocol's,
    and under that the program's own name less the word it opens with, in lower case."""
    kind = "runs" if "exchanges" in program.parent.parts else "frames"

    return program.parent / kind / program.stem.split(".", 1)[-1].lower()

# a program takes the frame to read and the file to write, because the language it is in has
# no standard input: the file package is the only way in or out
SECONDS = 120


def compiler():
    """The compiler, as this machine has it, or None."""
    named = os.environ.get(COMPILER.upper())

    if named:
        path = pathlib.Path(named)

        return path if path.exists() else None

    found = shutil.which(COMPILER)

    return pathlib.Path(found) if found else None


def packaged(built, work):
    """Puts the compiler's own packages where it looks for them: beside the program."""
    packages = built.parent / "packages"

    if not packages.is_dir():
        return False

    beside = work / "packages"

    try:
        beside.symlink_to(packages, target_is_directory=True)
    except (OSError, NotImplementedError):
        shutil.copytree(packages, beside)

    return True


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


def built(compiled, program, work):
    """The compiled program, or None and what the compiler said about it."""
    shutil.copy(program, work / program.name)

    try:
        made = subprocess.run(
            [str(compiled), program.name], cwd=work, capture_output=True, timeout=SECONDS)
    except subprocess.TimeoutExpired:
        return None, f"the compiler did not finish within {SECONDS} seconds"

    if made.returncode != 0:
        said = (made.stderr or made.stdout).decode("utf-8", "replace").strip().splitlines()
        return None, said[0] if said else f"the compiler refused it ({made.returncode})"

    program = work / program.stem

    if not program.exists():
        return None, "the compiler wrote no program"

    return program, None


def reads(program, frame, wrote, work):
    """What is wrong with how the compiled program reads its frame, or None."""
    given = work / "frame.bin"
    actual = work / "actual.bin"

    given.write_bytes(bytes_of(frame))
    actual.unlink(missing_ok=True)

    try:
        ran = subprocess.run(
            [f"./{program.name}", given.name, actual.name],
            cwd=work, capture_output=True, timeout=SECONDS)
    except subprocess.TimeoutExpired:
        return f"did not finish within {SECONDS} seconds"

    if ran.returncode != 0:
        said = (ran.stderr or ran.stdout).decode("utf-8", "replace").strip().splitlines()
        return said[0] if said else f"stopped ({ran.returncode})"

    if not actual.exists():
        return "wrote no output at all"

    written = actual.read_bytes()
    recorded = bytes_of(wrote)

    if written != recorded:
        return parted(written, recorded)

    return None


def main():
    required = "--required" in sys.argv[1:]

    root = pathlib.Path(__file__).resolve().parent
    programs = sorted(root.rglob("*" + EXTENSION))

    if not programs:
        print(f"no {LANGUAGE} programs found")
        return 0

    compiled = compiler()

    if compiled is None:
        print(f"no {COMPILER} on the path or in {COMPILER.upper()}: "
              f"{len(programs)} {LANGUAGE} programs were not replayed")
        return 1 if required else 0

    replayed = 0
    refused = 0

    with tempfile.TemporaryDirectory() as named:
        work = pathlib.Path(named)

        if not packaged(compiled, work):
            print(f"{compiled}: its packages are not beside it, so nothing can be compiled")
            return 1

        for program in programs:
            made, fault = built(compiled, program, work)

            if made is None:
                print(f"{program.relative_to(root)}: {fault}")
                refused += 1
                continue

            # a program has a frame for each message the corpus holds a capture of, and one
            # laid out from its model besides, so there is no one frame to look for
            for frame in sorted(kept(program).glob("*" + FRAME)):
                wrote = frame.with_suffix(WROTE)

                if not wrote.exists():
                    print(f"{frame.relative_to(root)}: has no {WROTE} beside it")
                    refused += 1
                    continue

                replayed += 1
                fault = reads(made, frame, wrote, work)

                if fault is not None:
                    print(f"{frame.relative_to(root)}: {fault}")
                    refused += 1

    print(f"{len(programs)} {LANGUAGE} programs compiled, "
          f"{replayed} frames replayed, {refused} refused")

    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())