#!/usr/bin/env python3
"""Plays a run through a whole venue and shows what happened, step by step.

A venue here is several programs that join: a gateway reads a client's packets and writes the
venue's own orders, a market reads those and writes the venue's own events, each feed reads
those and writes market data, and a responder answers the client from what the gateway read and
the market wrote. This runs them one after another on a published run, and says what
each one read and wrote as a person would say it, with the book drawn after every step that
changed it.

    python3 demo.py                     the venues here, and the runs each can be shown by
    python3 demo.py <venue>             that venue's day
    python3 demo.py <venue> <run>       any other run published for it
    python3 demo.py --every             every venue's day, which is what the build runs

Every program in it is run here and now, by the interpreter check.py carries; nothing shown was
recorded. What each wrote is held to what was published for that run as it goes, so a demonstration
that disagrees with the repository says so and fails.

Nothing here is evidence. The layouts it reads a packet by are published beside the programs for a
script to read, and a mistake in one could only describe a packet wrongly. What a program is held to
is the frames published for it; check.py is what makes that claim.
"""

import json
import pathlib
import struct
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

# the dialect has one implementation in this repository and it is check.py's
import check  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent

LANGUAGE = "brainfuck"
DAY = "day"

MESSAGES = ".messages.json"
REQUESTS = ".requests.json"
PACKETS = ".packets.json"
ANSWERS = ".answers.json"

# what a field is to an engine, as a venue's model marks it
ORDER = "Order"
REPLACEMENT = "Replacement"
INSTRUMENT = "Instrument"
SIDE = "Side"
PRICE = "Price"
QUANTITY = "Quantity"
AGGRESSOR = "Aggressor"
RESTING = "Resting"
REFUSAL = "Refusal"


class Refused(Exception):
    """Something asked for that is not published here, or a program that did not do what was published."""


# --- the bytes a field holds -----------------------------------------------------------------------


def integer(field, data):
    """The number a field's bytes hold, read the way the field states them."""
    return int.from_bytes(data, "big" if field["endian"] == "big" or field.get("text") else "little")


def stated(field, data):
    """What a field holds, said as a person would read it."""
    if field.get("float"):
        number = struct.unpack((">" if field["endian"] == "big" else "<") + ("d" if len(data) == 8 else "f"), data)[0]

        return str(int(number)) if number.is_integer() else str(number)

    held = integer(field, data)

    for name, code in field.get("values", {}).items():
        if code == held:
            return name

    if field.get("text"):
        return data.decode("latin-1").strip() or "(blank)"

    if field.get("scale"):
        scale = int(field["scale"])

        if scale < 0:
            return f"{held / (10 ** -scale):.{-scale}f}"

        return str(held * (10 ** scale))

    return str(held)


# --- what is published ------------------------------------------------------------------------------


def layout(program, suffix):
    """The layout published beside a program, or None where it publishes none."""
    beside = program.parent / (program.stem + suffix)

    return json.loads(beside.read_text(encoding="utf-8")) if beside.exists() else None


def venues(manifest):
    """Each venue's programs in this language, by what kind of program each is."""
    found = {}

    for program in manifest["programs"]:
        if program["language"] == LANGUAGE and program.get("venue"):
            found.setdefault(program["venue"], []).append(program)

    return found


def opening(programs, named):
    """Where a run of this name begins: the gateway where it has one, and the market otherwise."""
    for kind in ("gateway", "market"):
        for program in programs:
            if program["kind"] != kind:
                continue

            for run in program["runs"]:
                if run["name"] == named:
                    return program, run

    return None


def joined(manifest, programs, run):
    """The programs that read what this run wrote, each with its own run of it."""
    frames = {join["frame"] for join in manifest["joins"] if join["wrote"] == run["wrote"]}
    following = []

    for program in programs:
        for next_run in program["runs"]:
            if next_run["frame"] in frames:
                following.append((program, next_run))

    return following


# --- running one program ----------------------------------------------------------------------------


class Ran:
    """One program run on one input: what it wrote, and how much it had written before each read."""

    def __init__(self, program, run):
        self.program = program
        self.path = ROOT / program["path"]
        self.given = check.bytes_of(ROOT / run["frame"])

        code, jumps = check.compiled(self.path.read_text(encoding="utf-8"))
        marks = []
        started = time.perf_counter()

        self.written, taken = check.run(code, jumps, self.given, marks)
        self.seconds = time.perf_counter() - started
        self.length = len(code)
        self.steps = marks[-1][2] if marks else 0

        if taken != len(self.given):
            raise Refused(f"{self.path.name}: read {taken} of the {len(self.given)} bytes put to it")

        if self.written != check.bytes_of(ROOT / run["wrote"]):
            raise Refused(f"{self.path.name}: did not write what {run['wrote']} records")

        # how much had been written when the byte at each place of the input was first asked for
        self.before = {}

        for taken, written, _ in marks:
            self.before.setdefault(taken, written)

    def wrote_for(self, starts):
        """What was written for each part of the input, the parts given by where each starts.

        A program here reads the whole of one message before it writes anything for it, so what it
        wrote for a message is what it wrote between first asking for that message and first asking
        for the next.
        """
        edges = [self.before.get(start, len(self.written)) for start in starts] + [len(self.written)]

        return [(edges[at], edges[at + 1]) for at in range(len(starts))]


# --- reading a stream back --------------------------------------------------------------------------


def framed(frame, data):
    """Where each frame of a stream starts and ends, by the length each one states."""
    width = frame["length"]["width"]
    stands = frame["length"]["at"]
    parts = []
    at = 0

    while at + stands + width <= len(data):
        whole = integer(frame["length"], data[at + stands:at + stands + width]) + frame["addend"]

        if whole <= 0 or at + whole > len(data):
            break

        parts.append((at, at + whole))
        at += whole

    if at != len(data):
        raise Refused(f"a stream stops making sense as frames at byte {at} of {len(data)}")

    return parts


def fields_of(message, data, at):
    """A message's fields by role and by name, read in the order the wire states them."""
    by_role, by_name = {}, []

    for field in message["fields"]:
        held = data[at:at + field["width"]]
        at += field["width"]

        if field.get("role"):
            by_role[field["role"]] = (field, held)

        by_name.append((field, held))

    return by_role, by_name


def said(by_role, role):
    field, held = by_role[role]

    return stated(field, held)


def number(by_role, role):
    field, held = by_role[role]

    return integer(field, held)


def ordered(by_role, buying):
    """An order in a line: which way, how much, of what, at what price, under which number."""
    return (f"{'buy' if buying else 'sell'} {said(by_role, QUANTITY)}"
            + (f" {said(by_role, INSTRUMENT)}" if INSTRUMENT in by_role else "")
            + f" at {said(by_role, PRICE)}, order {said(by_role, ORDER)}")


def listed(by_name):
    return "  ".join(f"{field.get('title', field['named'])}={stated(field, held)}" for field, held in by_name)


def event(messages, data, start):
    """One of a market's own messages, as (what it does, its fields by role, a line saying it)."""
    frame = messages["frame"]
    header = frame["opening"]
    typed = start + frame["type"]["at"]
    code = integer(frame["type"], data[typed:typed + frame["type"]["width"]])

    message = next((held for held in messages["messages"] if code in held["codes"]), None)

    if message is None:
        return None, {}, f"a message typed {code}, which this venue states no layout for"

    by_role, by_name = fields_of(message, data, start + header)
    does = message["does"]

    if does == "order":
        line = ordered(by_role, number(by_role, SIDE) == message["buys"])
    elif does == "cancel":
        line = f"cancel order {said(by_role, ORDER)}"
    elif does == "accepted":
        line = f"accepted  order {said(by_role, ORDER)}"
    elif does == "rested":
        line = f"rested    order {said(by_role, ORDER)}, {said(by_role, QUANTITY)} at {said(by_role, PRICE)}"
    elif does == "traded":
        line = (f"traded    {said(by_role, QUANTITY)} at {said(by_role, PRICE)}, order "
                f"{said(by_role, AGGRESSOR)} against order {said(by_role, RESTING)}")
    elif does == "canceled":
        line = f"canceled  order {said(by_role, ORDER)}"
    elif does == "refused":
        line = f"refused   order {said(by_role, ORDER)}: {said(by_role, REFUSAL)}"
    else:
        line = f"{does:<9} {listed(by_name)}"

    return message, by_role, line


def request(requests, data, start, end):
    """One of a client's packets in a line: the request it is, or failing that the packet it is."""
    def holds(test):
        return (integer(test, data[start + test["at"]:start + test["at"] + test["width"]])
                in test["codes"]) == test["holds"]

    for asked in requests["requests"]:
        if not all(holds(test) for test in asked["tests"]):
            continue

        by_role = {}

        for field in asked["fields"]:
            if field.get("role"):
                by_role[field["role"]] = (field, data[start + field["at"]:start + field["at"] + field["width"]])

        if asked["admits"] and all(role in by_role for role in (SIDE, QUANTITY, PRICE, ORDER)):
            # which way round is the side's own name for itself in the order entry's model
            return f"{asked['named']}: " + ordered(by_role, said(by_role, SIDE).lower().startswith("b"))

        if ORDER in by_role:
            return f"{asked['named']}: order {said(by_role, ORDER)}"

        return asked["named"]

    frame = requests["frame"]
    at = start + frame["type"]["at"]
    code = integer(frame["type"], data[at:at + frame["type"]["width"]])

    for packet in requests["packets"]:
        if code in packet["codes"]:
            return packet["named"]

    return f"a packet typed {code}"


def packets(layout, data, start, end):
    """The packets a feed wrote in one stretch of its output, each in a line."""
    lines = []
    at = start

    while at < end:
        for packet in layout["packets"]:
            if at + packet["bytes"] > end:
                continue

            offset = at
            matches = True
            shown = []

            for field in packet["fields"]:
                held = data[offset:offset + field["width"]]
                offset += field["width"]

                if "literal" in field:
                    matches = matches and held == bytes.fromhex(field["literal"])

                # a field that never changes is shown only where its value has a name: a
                # reason, which is what a reader wants to know; padding and nought are not
                if not field.get("header") and ("literal" not in field or field.get("values")):
                    shown.append((field, held))

            if matches:
                lines.append(f"{packet['named']}: {listed(shown)}")
                at += packet["bytes"]
                break
        else:
            raise Refused(f"{layout['program']}: wrote something at byte {at} that is none of the packets it states")

    return lines


# --- the book ----------------------------------------------------------------------------------------


class Book:
    """The orders resting, rebuilt from what the market said happened and from nothing else."""

    def __init__(self, messages):
        arriving = next(message for message in messages["messages"] if message["does"] == "order")

        self.buys = arriving["buys"]
        self.orders = {}
        self.drawn = None

    def heard(self, message, by_role):
        does = message["does"]

        if does == "rested":
            self.rest(number(by_role, ORDER), by_role)
        elif does == "traded":
            for role in (AGGRESSOR, RESTING):
                self.take(number(by_role, role), number(by_role, QUANTITY))
        elif does == "canceled":
            self.orders.pop(number(by_role, ORDER), None)
        elif does == "replaced":
            self.orders.pop(number(by_role, ORDER), None)
            self.rest(number(by_role, REPLACEMENT), by_role)

    def rest(self, identifier, by_role):
        self.orders[identifier] = [number(by_role, SIDE) == self.buys, number(by_role, PRICE),
                                   by_role[PRICE], number(by_role, QUANTITY)]

    def take(self, identifier, quantity):
        if identifier in self.orders:
            self.orders[identifier][3] -= quantity

            if self.orders[identifier][3] <= 0:
                del self.orders[identifier]

    def lines(self):
        """The book as a ladder, offers above bids, each price with the orders queued at it."""
        levels = {}

        for identifier, (buying, price, (field, _), quantity) in self.orders.items():
            shown = stated(field, price.to_bytes(field["width"], "big" if field["endian"] == "big" else "little"))
            levels.setdefault((buying, price, shown), []).append((identifier, quantity))

        if not levels:
            return ["(empty)"]

        drawn = []

        for buying in (False, True):
            if buying:
                drawn.append("-" * 44)

            for (side, price, shown), queue in sorted(levels.items(), key=lambda level: -level[0][1]):
                if side == buying:
                    total = sum(quantity for _, quantity in queue)
                    orders = ", ".join(f"{quantity} of order {identifier}" for identifier, quantity in queue)
                    drawn.append(f"{'bid  ' if buying else 'offer'} {shown:>10} {total:>6}   {orders}")

        return drawn

    def changed(self):
        """The ladder where it is not the one last drawn, or nothing."""
        lines = self.lines()

        if lines == self.drawn:
            return None

        self.drawn = lines

        return lines


# --- playing a run ----------------------------------------------------------------------------------


def played(manifest, venue, programs, named):
    """One run through every program of a venue that reads it, said step by step."""
    start = opening(programs, named)

    if start is None:
        raise Refused(f"{venue}: publishes no run {named}; python3 demo.py lists the runs it does")

    first, first_run = start
    gateway = None

    print(f"{venue}, the run {named}")
    print()

    if first["kind"] == "gateway":
        print(f"  running {pathlib.PurePosixPath(first['path']).name} ...", flush=True)
        gateway = Ran(first, first_run)
        following = [(program, run) for program, run in joined(manifest, programs, first_run)
                     if program["kind"] == "market"]

        if not following:
            raise Refused(f"{venue}: nothing here reads what its gateway wrote for {named}")

        market_program, market_run = following[0]
    else:
        market_program, market_run = first, first_run

    print(f"  running {pathlib.PurePosixPath(market_program['path']).name} ...", flush=True)
    market = Ran(market_program, market_run)
    messages = layout(market.path, MESSAGES)

    if messages is None:
        raise Refused(f"{market.path.name}: publishes no layout beside it")

    feeds = []

    for program, run in joined(manifest, programs, market_run):
        if program["kind"] == "feed" and (described := layout(ROOT / program["path"], PACKETS)) is not None:
            print(f"  running {pathlib.PurePosixPath(program['path']).name} ...", flush=True)
            feeds.append((Ran(program, run), described))

    # and the responder, which reads what the gateway read and then what the market wrote
    responder = None

    if gateway is not None:
        for program in programs:
            if program["kind"] != "responder" or (described := layout(ROOT / program["path"], ANSWERS)) is None:
                continue

            for run in program["runs"]:
                if run["name"] == first_run["name"]:
                    print(f"  running {pathlib.PurePosixPath(program['path']).name} ...", flush=True)
                    responder = (Ran(program, run), described)

    print()

    # the venue's own orders, each with the events the market wrote for it
    orders = framed(messages["frame"], market.given)
    answers = market.wrote_for([at for at, _ in orders])
    events = framed(messages["frame"], market.written)
    book = Book(messages)

    # what the responder wrote for each request and each event, by where each was in its input:
    # the client's requests first, as the gateway read them, and the market's events after
    replies = {}

    if responder is not None:
        ran, described = responder
        requested = [at for at, _ in framed(layout(gateway.path, REQUESTS)["frame"], gateway.given)]
        base = len(ran.given) - len(market.written)
        starts = requested + [base + at for at, _ in events]

        if ran.given[:len(gateway.given)] != gateway.given or ran.given[base:] != market.written:
            raise Refused(f"{ran.path.name}: was not given what the gateway read and the market wrote")

        for start, (low, high) in zip(starts, ran.wrote_for(starts)):
            replies[start] = packets(described, ran.written, low, high)

        replies = {("request" if start < len(gateway.given) else "event",
                    start if start < len(gateway.given) else start - base): lines
                   for start, lines in replies.items()}

    def replied(kind, at):
        """What the client was answered with for one request or one event."""
        for line in replies.get((kind, at), []):
            print(f"      responder   {line}")

    def answered(order):
        """What the market and every feed did with one of the venue's own orders."""
        low, high = answers[order]
        mine = [at for at, _ in events if low <= at < high]

        for at in mine:
            message, by_role, line = event(messages, market.written, at)
            print(f"      market      {line}")

            if message is not None:
                book.heard(message, by_role)

        for feed, described in feeds:
            sent = feed.wrote_for([at for at, _ in events])
            index = {at: number for number, (at, _) in enumerate(events)}

            for at in mine:
                for line in packets(described, feed.written, *sent[index[at]]):
                    print(f"      {described['feed']:<11} {line}")

        for at in mine:
            replied("event", at)

        if (ladder := book.changed()) is not None:
            print()

            for line in ladder:
                print(f"          {line}")

    step = 0

    if gateway is not None:
        requests = layout(gateway.path, REQUESTS)
        asked = framed(requests["frame"], gateway.given)
        admitted = gateway.wrote_for([at for at, _ in asked])

        for (at, end), (low, high) in zip(asked, admitted):
            step += 1
            print(f"{step:>3}   client      {request(requests, gateway.given, at, end)}")

            for order, (start_of, _) in enumerate(orders):
                if low <= start_of < high:
                    print(f"      gateway     {event(messages, market.given, start_of)[2]}")
                    answered(order)

            # an order the gateway turned away is answered here, and went no further
            replied("request", at)

            print()
    else:
        for order, (start_of, _) in enumerate(orders):
            step += 1
            print(f"{step:>3}   order       {event(messages, market.given, start_of)[2]}")
            answered(order)
            print()

    print("What that took:")

    for ran in (([gateway] if gateway else []) + [market] + [feed for feed, _ in feeds]
                + ([responder[0]] if responder else [])):
        print(f"  {ran.path.name:<36} {ran.length:>12,} instructions long, {ran.steps:>12,} run"
              f" in {ran.seconds:.1f}s, {len(ran.given):>5} bytes in, {len(ran.written):>5} out")

    print()
    print("Each program wrote, byte for byte, what is published for this run.")


def main(argv):
    manifest = json.loads((ROOT / check.MANIFEST).read_text(encoding="utf-8"))
    found = venues(manifest)

    if not argv:
        print(__doc__)

        # a run another program's output begins is shown from where it began, not from the middle
        handed = {join["frame"] for join in manifest["joins"]}

        for venue, programs in sorted(found.items()):
            runs = sorted({run["name"] for program in programs for run in program["runs"]
                           if program["kind"] in ("gateway", "market") and run["frame"] not in handed})
            print(f"  {venue}: {', '.join(runs)}")

        return 0

    try:
        if argv[0] == "--every":
            shown = 0

            for venue, programs in sorted(found.items()):
                if opening(programs, DAY) is not None:
                    played(manifest, venue, programs, DAY)
                    print()
                    shown += 1

            print(f"{shown} venues shown")

            return 0 if shown else 1

        venue = next((held for held in found if held.lower() == argv[0].lower()), None)

        if venue is None:
            raise Refused(f"{argv[0]}: is not a venue here; the venues are {', '.join(sorted(found))}")

        played(manifest, venue, found[venue], argv[1] if len(argv) > 1 else DAY)
    except Refused as refused:
        print(refused)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))