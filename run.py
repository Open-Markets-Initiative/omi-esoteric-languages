#!/usr/bin/env python3
"""Puts orders to a generated market and says what it published.

A market's program reads its venue's internal protocol: a length, a type byte, then fields at the
widths and byte orders that venue's model states. The layout published beside the program is what
makes that writable from here — so an order can be said as "buy 1 7@9995" rather than composed as
hexadecimal with a length reckoned by hand.

    python3 run.py <market.bf> to PreOpen , buy 1 7@9995 , sell 2 4@9995 , phase Open
    python3 run.py <market.bf> --frame <published .frame>
    python3 run.py <market.bf> --at 0 to PreOpen , buy 1 7@9995
    python3 run.py --every

A step is stamped with the clock, because the engine has none of its own and publishes whatever
stamp arrived with the message it answers. A coarse clock reads the same for several steps, which is
the clock and not the engine; --at fixes the stamp instead, so two runs can be compared.

Nothing here is evidence. What a program is held to is the frames published beside it, which were
checked against the C# parser reading the same bytes through the real model; check.py is what makes
that claim. This builds a stream and reads one back for a person, and a mistake in it could only put
a wrong order, never make a wrong program look right.
"""

import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

# nothing of this is left behind in the repository it ran in: importing writes a __pycache__ beside
# whatever it imported, and a published repository that grows a directory when somebody uses it is a
# repository that needs a rule about it
sys.dont_write_bytecode = True

# the dialect has one implementation in this repository and it is check.py's. A second would be a
# second dialect, which is the one thing a generated program cannot survive
import check  # noqa: E402

LAYOUT = ".messages.json"

# what a field is to an engine, as a venue's model marks it
TIMESTAMP = "Timestamp"
ORDER = "Order"
REPLACEMENT = "Replacement"
INSTRUMENT = "Instrument"
SIDE = "Side"
PRICE = "Price"
QUANTITY = "Quantity"
CHANGE = "PhaseChange"

# the stamp every step of this run carries, where it was fixed rather than read off the clock
FIXED = None


class Refused(Exception):
    """Something a person asked for that this venue does not state."""


# --- the bytes a field holds -----------------------------------------------------------------------


def integer(field, data):
    """The number a field's bytes hold, read the way the field states them."""
    return int.from_bytes(data, "big" if field["endian"] == "big" else "little")


def serialised(field, value):
    """A number as the field's own bytes, or the field's own padding where it holds nothing.

    A text field left empty is spaces rather than noughts, because a frame of nought bytes is one no
    venue would send. That is the same rule the generator lays a published run out by.
    """
    width = field["width"]

    if isinstance(value, bytes):
        return value[:width].ljust(width, b" ")

    if not value and field.get("text"):
        return b" " * width

    return int(value).to_bytes(width, "big" if field["endian"] == "big" else "little")


def stated(field, data):
    """What a field holds, said as a person would read it."""
    held = integer(field, data)

    for name, code in field.get("values", {}).items():
        if code == held:
            return name

    if field.get("scale"):
        scale = int(field["scale"])

        if scale < 0:
            return f"{held / (10 ** -scale):.{-scale}f}"

        return str(held * (10 ** scale))

    if field.get("text"):
        return data.decode("latin-1").rstrip() or "(blank)"

    return str(held)


# --- the layout a market publishes about itself -----------------------------------------------------


def layout_of(program):
    """The layout published beside a program, or None where it publishes none."""
    beside = program.parent / (program.stem + LAYOUT)

    if not beside.exists():
        return None

    return json.loads(beside.read_text(encoding="utf-8"))


def speaking(layout, does):
    """The message that does this, as this venue states it."""
    for message in layout["messages"]:
        if message["does"] == does:
            return message

    raise Refused(f"{layout['venue']} states no message that {does}s")


def held(field, holding):
    """What one field of a message this run states, or nothing and the field's own padding."""
    return holding.get(field.get("role"), 0)


def framed(layout, message, holding):
    """One message as the venue frames it: a length, the type byte, then its fields."""
    frame = layout["frame"]
    body = b"".join(serialised(field, held(field, holding)) for field in message["fields"])

    # the length is what the protocol's own rule reckons, so what is built here is what the program
    # will read back out of it
    length = frame["length"]["width"] + frame["type"]["width"] + len(body) - frame["addend"]

    return (serialised(frame["length"], length)
            + serialised(frame["type"], message["codes"][0])
            + body)


# --- what a person asks for -------------------------------------------------------------------------


def priced(field, text):
    """A price as the field holds it: a bare number is the field's own integer, and one written with
    a point is scaled the way the model scales that field."""
    if "." not in text:
        return int(text)

    scale = int(field.get("scale") or 0)

    if scale >= 0:
        raise Refused(f"{field['named']} states no decimal places, so {text} cannot be put in it")

    return round(float(text) * (10 ** -scale))


def walked(layout, there):
    """The shortest run of changes from the phase the day starts in to the one wanted, breadth first
    over the changes the chart answers."""
    phases = {phase["named"].lower(): phase["index"] for phase in layout["day"]["phases"]}

    if there.lower() not in phases:
        raise Refused(f"{layout['day']['named']} states no phase {there}; it states "
                      + ", ".join(phase["named"] for phase in layout["day"]["phases"]))

    wanted = phases[there.lower()]
    start = layout["day"]["starts"]
    reached = {start: []}
    queue = [start]

    while queue:
        phase = queue.pop(0)

        for change in layout["day"]["changes"]:
            if change["from"] != phase or change["to"] in reached:
                continue

            reached[change["to"]] = reached[phase] + [change]
            queue.append(change["to"])

    if wanted not in reached:
        raise Refused(f"no run of the changes {layout['day']['named']} answers reaches {there}")

    return reached[wanted]


def changed(layout, named):
    """The change of phase a person named, as the chart states it."""
    for change in layout["day"]["changes"]:
        if change["named"].replace(" ", "").lower() == named.replace(" ", "").lower():
            return change

    raise Refused(f"{layout['day']['named']} answers no change {named}; it answers "
                  + ", ".join(change["named"] for change in layout["day"]["changes"]))


def banded(layout):
    """The band as the price field states it, where that is not the integer the field holds."""
    field = next((held for message in layout["messages"] for held in message["fields"]
                  if held.get("role") == PRICE), None)

    if field is None or not field.get("scale"):
        return ""

    lowest = stated(field, serialised(field, layout["band"]["lowest"]))
    highest = stated(field, serialised(field, layout["band"]["highest"]))

    return f" ({lowest} to {highest})"


def moment():
    """Now, in the nanoseconds since the epoch an Ipc timestamp counts, or the stamp a run fixed."""
    return FIXED if FIXED is not None else time.time_ns()


def order(layout, side, identifier, quantity, price):
    """One order as the venue frames one."""
    message = speaking(layout, "order")
    field = next(held for held in message["fields"] if held.get("role") == PRICE)

    return framed(layout, message, {
        TIMESTAMP: moment(),
        ORDER: int(identifier),
        INSTRUMENT: layout.get("symbol", "").encode("latin-1"),
        SIDE: message["buys"] if side == "buy" else message["sells"],
        PRICE: priced(field, price),
        QUANTITY: int(quantity),
    })


def cancel(layout, identifier):
    return framed(layout, speaking(layout, "cancel"), {
        TIMESTAMP: moment(),
        ORDER: int(identifier),
    })


def replace(layout, identifier, replacement, side, quantity, price):
    """One replace as the venue frames one: the order it names, and what replaces it."""
    message = speaking(layout, "replace")
    field = next(held for held in message["fields"] if held.get("role") == PRICE)
    arriving = speaking(layout, "order")

    return framed(layout, message, {
        TIMESTAMP: moment(),
        ORDER: int(identifier),
        REPLACEMENT: int(replacement),
        INSTRUMENT: layout.get("symbol", "").encode("latin-1"),
        SIDE: arriving["buys"] if side == "buy" else arriving["sells"],
        PRICE: priced(field, price),
        QUANTITY: int(quantity),
    })


def asking(layout, change):
    return framed(layout, speaking(layout, "phase"), {
        TIMESTAMP: moment(),
        CHANGE: change["code"],
    })


def built(layout, steps):
    """The stream a run of steps makes, and the steps as they will be reported."""
    stream = bytearray()
    said = []

    for step in steps:
        words = step.split()
        does = words[0].lower()

        if does in ("buy", "sell") and len(words) == 3 and "@" in words[2]:
            quantity, price = words[2].split("@", 1)
            stream += order(layout, does, words[1], quantity, price)
            said.append(f"{does} {quantity} at {price}, as order {words[1]}")
        elif does == "cancel" and len(words) == 2:
            stream += cancel(layout, words[1])
            said.append(f"take order {words[1]} back")
        elif (does == "replace" and len(words) == 6 and words[2] == "with"
              and words[4] in ("buy", "sell") and "@" in words[5]):
            quantity, price = words[5].split("@", 1)
            stream += replace(layout, words[1], words[3], words[4], quantity, price)
            said.append(f"replace order {words[1]} with {words[4]} {quantity} at {price}, as order {words[3]}")
        elif does == "phase" and len(words) == 2:
            change = changed(layout, words[1])
            stream += asking(layout, change)
            said.append(f"ask for {change['named']}"
                        + (f", which crosses {change['crosses']}" if change.get("crosses") else ""))
        elif does == "to" and len(words) == 2:
            for change in walked(layout, words[1]):
                stream += asking(layout, change)
                said.append(f"ask for {change['named']}")
        else:
            raise Refused(f"'{step}' is not something to do; the steps are "
                          "buy <order> <quantity>@<price>, sell <order> <quantity>@<price>, "
                          "cancel <order>, replace <order> with <new order> buy|sell "
                          "<quantity>@<price>, phase <change>, to <phase>")

    return bytes(stream), said


# --- what the program published ---------------------------------------------------------------------


def published(layout, written):
    """What the program wrote, message by message, or a line saying where it stopped making sense."""
    frame = layout["frame"]
    header = frame["length"]["width"] + frame["type"]["width"]
    by_code = {code: message for message in layout["messages"] for code in message["codes"]}
    said = []
    at = 0

    while at < len(written):
        if len(written) - at < header:
            said.append(f"  {len(written) - at} bytes left over, which is less than a frame's header")
            break

        length = integer(frame["length"], written[at:at + frame["length"]["width"]])
        code = integer(frame["type"], written[at + frame["length"]["width"]:at + header])
        whole = length + frame["addend"]

        if whole > len(written) - at:
            said.append(f"  a frame at byte {at} states {length}, which runs past what was written")
            break

        message = by_code.get(code)

        if message is None:
            said.append(f"  a frame at byte {at} is typed {code}, which this venue states no message for")
            at += whole
            continue

        held = []
        offset = at + header

        for field in message["fields"]:
            held.append(f"{field['named']}={stated(field, written[offset:offset + field['width']])}")
            offset += field["width"]

        said.append(f"  {message['does']:<10} " + "  ".join(held))
        at += whole

    return said


# --- running it -------------------------------------------------------------------------------------


def every():
    """Every market here, over every frame published beside it, decoded.

    What this is for is the runner itself. A published runner that quietly stopped understanding a
    layout would be worse than none, so this is the shape of it a check can run without being told
    any venue's name: it finds the markets, replays what shipped with them, and reads it back.
    """
    root = pathlib.Path(__file__).resolve().parent
    layouts = sorted(root.rglob("*" + LAYOUT))

    if not layouts:
        print("no markets found")
        return 1

    replayed = 0
    refused = 0

    for beside in layouts:
        program = beside.parent / (beside.name[:-len(LAYOUT)] + ".bf")

        if not program.exists():
            print(f"{beside.relative_to(root)}: no program beside it")
            refused += 1
            continue

        for frame in sorted(program.parent.glob(program.stem + ".*.frame")):
            replayed += 1

            if main([str(program), "--frame", str(frame)]) != 0:
                refused += 1

            print()

    print(f"{len(layouts)} markets, {replayed} runs replayed, {refused} refused")

    return 1 if refused else 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1

    if argv[0] == "--every":
        return every()

    program = pathlib.Path(argv[0])

    if not program.exists():
        print(f"{program}: no such program")
        return 1

    layout = layout_of(program)

    if layout is None:
        print(f"{program.name}: publishes no {LAYOUT} beside it, so there is no stream to build for "
              "it. Only a market publishes one.")
        return 1

    rest = argv[1:]

    if rest[:1] == ["--at"]:
        global FIXED

        try:
            FIXED = int(rest[1])
        except (IndexError, ValueError):
            print(f"{program.name}: --at wants the nanoseconds a run is stamped with")
            return 1

        rest = rest[2:]

    try:
        if rest[:1] == ["--frame"]:
            given = check.bytes_of(pathlib.Path(rest[1]))
            said = [f"the frame published in {pathlib.Path(rest[1]).name}"]
        else:
            # steps are separated by commas so a shell need not be fought over the quoting
            steps = [step.strip() for step in " ".join(rest).split(",") if step.strip()]

            if not steps:
                print(__doc__)
                return 1

            given, said = built(layout, steps)
    except (Refused, IndexError, ValueError) as refused:
        print(f"{program.name}: {refused}")
        return 1

    print(f"{layout['venue']} market, {layout['protocol']}")
    print(f"a book of the {layout['band']['highest'] - layout['band']['lowest'] + 1} prices from "
          f"{layout['band']['lowest']} to {layout['band']['highest']}{banded(layout)}, and the day "
          f"{layout['day']['named']}")
    print()

    for line in said:
        print(f"  {line}")

    print()

    code, jumps = check.compiled(program.read_text(encoding="utf-8"))
    written, taken = check.run(code, jumps, given)

    if taken != len(given):
        print(f"  it read {taken} of the {len(given)} bytes put to it")

    print(f"  {len(given)} bytes in, {len(written)} out")
    print()

    for line in published(layout, written):
        print(line)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))