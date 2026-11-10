# Brainfuck

![Brainfuck](../images/Brainfuck.png)

Programs in Brainfuck that read common binary exchange protocols, generated from the same compiled data models every other Omi repository is generated from.

## Why

Every other generated language lends its generator something: arithmetic, addressing, variables, functions. Brainfuck lends nothing — eight instructions and one tape of bytes — so whatever cannot be expressed here is a gap in the protocol model rather than a gap in the language. These programs are a conformance test of the models as much as they are code.

They are also slow, by some six orders of magnitude against the generated C++. This is a demonstration and a test, not something to run a venue on.

## Usage

A program reads one frame from standard input and writes a line per field: the field's own name, then the bytes it held. Which message it was is said by the order the lines come in, because only one arm of a dispatch ever runs.

```
bf brainfuck/protocols/nasdaq/nsmequities/orders/NsmEquities.Orders.v5.0.Client.bf < frame.bin
```
Most programs have a frame to read published beside them, as hexadecimal in a `.frame` file, with what the program wrote when it read it in a `.wrote` file. Those are what `check.py` runs, and they are the shortest way to see one of these work.

A market can be driven rather than replayed. `run.py` builds that venue's own order stream out of steps said in words, runs the market on it, and reads back what the market published field by field:

```
python3 run.py brainfuck/exchanges/iexequities/IexEquities.Market.bf to Continuous , buy 1 7@9995 , sell 2 4@9995
```
**Or run one without installing anything.** This repository's own build workflow takes a market and a run of orders when it is dispatched by hand, so the Actions tab will run an engine and print what it published — no clone and no Python. What a person types reaches the script through the environment and quoted, so a dispatch states a run of orders and cannot state a command.

The steps are `buy <order> <quantity>@<price>`, `sell` the same, `cancel <order>`, `phase <change>` for a change the venue's chart answers, and `to <phase>` to walk the day to a phase by the shortest run of changes it answers. A price written plainly is the integer the field holds and one written with a point is scaled the way that field is scaled, so `9995` and `0.9995` are the same price where the model states four decimal places. `--frame <file>` replays a published frame instead of building one, `--at <nanoseconds>` fixes the stamp every step carries so that two runs can be compared, and `--every` replays every market here over everything published beside it, which is what the build runs.

Any interpreter will do that holds to the stated dialect: cells of one byte that wrap, a tape of 65,536 of them, the pointer starting at the first and never leaving, and a read yielding zero once the input is spent. Brainfuck has no standard to appeal to for any of that — only a convention, and interpreters really do differ at these points — so whether yours keeps them is a question to ask it rather than to hope about:

```
bf brainfuck/dialect.bf < /dev/null
```
That program takes no input and prints one line per claim, saying of each whether this interpreter kept it. All four should say `ok`. One that says `no`, or a line that stops partway through, names what your interpreter does differently — and the claims are listed in the order the programs here lean on them, which was measured rather than guessed.

The one byte wrap is the one that matters most: of the 153 frames published here, only 18 still read the same under cells of 32 bits. The spent read matters to the markets alone and matters absolutely — a market reads to the end of its input and stops on a length of nothing, so under either of the other two conventions every market run never stops at all. The tape's length matters least: the highest cell anything here touches is 943, so classic Brainfuck's 30,000 would do thirty times over, and the room is asked for because a book over a real price band would want it rather than because anything here does.

## Layout

Where these sit, written from the repository root rather than from here, because the root is where the scripts that run them are:

```
brainfuck/
  protocols/<organization>/<division>/<protocol>/<protocol>.bf
  exchanges/<venue>/ReadMe.md
  exchanges/<venue>/<venue>.<session>.bf
  exchanges/<venue>/<venue>.Market.bf
```
A protocol's decoder sits under `protocols` because it is the same program whoever speaks it; a session and a market sit under `exchanges` because they are the venue's own — a venue is what declares which chart runs over which protocol, which price its book is banded on, and which trading day its market runs. A market's program carries its day in its own notes, and that venue's own readme beside it states which day it ran and why — the days published here are not all the days the venues declare, because a venue declaring two of them for one protocol gets the simplest rather than a program picked between them. Where a chart asks for a cross of what a phase collected, the market crosses it at the change of phase and publishes the venue's own Cross Completed message for it — at each resting level's own price rather than at one clearing price struck for all of it, which each program says of itself.

### Investors Exchange Equities Open

- OrderEntry `Iex.IexEquities.OrderEntry.Fix.v2.91`, session `Fix`
- Feed `Iex.IexEquities.Tops.IexTp.v1.66`
- Feed `Iex.IexEquities.Deep.IexTp.v1.08`
- Feed `Iex.IexEquities.DeepPlus.IexTp.v1.05`
- Snap `Iex.IexEquities.Deep.Snap.v1.6`
- Snap `Iex.IexEquities.Tops.Snap.v1.6`
- Snap `Iex.IexEquities.DeepPlus.Snap.v1.06`
- Ipc `Iex.IexEquities.MatchingEngine.Ipc.v1.0`
- Engine `Iex.IexEquities.Equities.Open.Trading`

### Investors Exchange Equities Session

- OrderEntry `Iex.IexEquities.OrderEntry.Fix.v2.91`, session `Fix`
- Feed `Iex.IexEquities.Tops.IexTp.v1.66`
- Feed `Iex.IexEquities.Deep.IexTp.v1.08`
- Feed `Iex.IexEquities.DeepPlus.IexTp.v1.05`
- Snap `Iex.IexEquities.Deep.Snap.v1.6`
- Snap `Iex.IexEquities.Tops.Snap.v1.6`
- Snap `Iex.IexEquities.DeepPlus.Snap.v1.06`
- Ipc `Iex.IexEquities.MatchingEngine.Ipc.v1.0`
- Engine `Iex.IexEquities.Equities.Session.Trading`

### Nasdaq Stock Market Open

- Ipc `Nasdaq.NsmEquities.MatchingEngine.Ipc.v2026`
- Engine `Nasdaq.NsmEquities.Equities.Open.Trading`
- OrderEntry `Nasdaq.NsmEquities.Orders.Ouch.v5.0`, session `SoupBin.Tcp`
- Feed `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Replay `Nasdaq.NsmEquities.TotalView.Glimpse.v5.0`
- Replay `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.Orders.Ouch.v5.0`

### Nasdaq Stock Market Session

- Ipc `Nasdaq.NsmEquities.MatchingEngine.Ipc.v2026`
- Engine `Nasdaq.NsmEquities.Equities.Session.Trading`
- OrderEntry `Nasdaq.NsmEquities.Orders.Ouch.v5.0`, session `SoupBin.Tcp`
- Feed `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Replay `Nasdaq.NsmEquities.TotalView.Glimpse.v5.0`
- Replay `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.Orders.Ouch.v5.0`

## Sessions

A session reads the other end's packets from standard input, holds a state, and writes the answers its chart says to write. The chart is the venue's own, the same one the generated C++ session runs, and nothing in it names a packet: an event is a marking on one, so `Receive.Login.Request` means the packet marked Login Request arriving.

**A generated session accepts every login, and that is a property of it rather than a detail.** A chart names three kinds of thing. Receive and Send are bytes; a Request is a service asking the session to do something, a Handler is the endpoint answering a question the session cannot answer itself, and an Ask is the session putting that question. A program with one input and one output has nowhere to put a question and nobody to ask it of, so those transitions cannot run at all — seven of SoupBinTcp's twelve are of that kind. Rather than refuse the chart over it, the accepting answer is taken when the program is written, and only where the chart states it without a condition: a condition reads a field of the login that asked, and deciding a login on the login's own contents is not authentication. So these demonstrate a handshake and authenticate nothing.

Each session is published with one run per transition of its chart, named for the state it rests in and the packet that arrives. A run is the shortest way into that state and then the packet itself, so the login stands at the head of every one, which is what a connection really looks like. A run the session answers nothing to is published too, with an empty answer: half of what a session does is decline to answer — a heartbeat is received and answered by doing nothing — and a check that skipped those would pass a program that replied to every one.

## Markets

A market reads a venue's own internal order stream from standard input, holds a book of price levels on each side, matches them whenever they cross, and **writes that venue's own messages back out** — an Order Rested for an order that comes to rest, a Trade for each one that happens. It reads the internal protocol rather than the venue's order entry, which is what the generated C++ engine does and for the same reason: the internal protocol is the one that states order flow as order flow, marking which field is the price, which the quantity and which the side, and which byte of the side means buying. An order entry protocol marks its handshake and leaves its order fields to be recognised by name, and recognising a field by its name is the one thing none of these generators does.

Writing the protocol rather than a report about it is what makes the output worth keeping, because it can then be read by something that was not written for it. Each message is framed by the venue's own length rule, selected by its own type byte, and laid out field by field at the widths and byte orders its model states — and the C# parser reads the whole lot back as the messages they are. Nothing agrees on that by accident. The first attempt framed every message correctly and still failed this, because a book keeps its own numbers most significant byte first where this protocol states them the other way round, so every identifier and quantity came out backwards. A gate that only compared bytes against last time's bytes would have called that fine.

**A book reaches a price level by index, and an index is one byte, so a book holds the prices that share the upper bytes of one price.** Which price is not chosen by the generator: the venue's declaration names it, as the reference its crosses are drawn towards and its own traders quote around. The band runs from there, and a price outside it is refused and reported as refused — never folded onto a level it does not belong to. That is a real limit of a book built out of eight instructions, so each program states its own band in its own notes, and the run published beside it puts one order outside that band on purpose, because a limit nothing exercises is a limit nobody knows is there.

Each market is published with a run of orders and the messages it wrote, held to three things beforehand. The orders are laid out from the model and the C# parser must read the whole run back as the messages it was built from, which is what says the program was fed the venue's protocol rather than something invented for it. The parser must then read what the program wrote, as described above. And a plain book written in C# over the same orders must agree with the program on every trade — whose order was resting, and how much changed hands. The three agree only if the program dispatched to the right level, remembered the right order there, took the smaller of the two quantities and left the right remainder behind.

**What a market reads and writes is published beside it**, as a `.messages.json` file: each message under the code that selects it, its fields in the order the wire states them, each field's width, byte order and what it is to an engine, and the names its own values carry. That is what makes a market usable here rather than only checkable. The models are not in this repository, so without it the only orders anyone could put to a program were the frames that shipped with it, and the only way to change one was to edit hexadecimal and reckon a length by hand. It is a flattening of a model and not a model; `run.py` reads it and nothing that makes a claim does, so a mistake in it could put a wrong order and could not make a wrong program look right.

A trade names the resting order and the price of the level it rested at, not the arriving order's limit, because that is where the trade happened: an order sweeping two levels trades at each of those rather than twice at its own price. **A level remembers one order, and that is a stated simplification** — a real level is a queue and this holds the last order put there, so a level two orders deep names only the second. It is kept because the venue's protocol says a trade carries the resting order's identifier, and a message carrying a made-up one would be worse than a book that admits what it remembers.

**Quantities in a published run are deliberately small, and the reason is worth stating because the obvious reading of it is wrong.** There is no addition here, only counting up, and every count up has to settle a carry through what the level already holds — which cannot be looked at without counting that down and back too. So filling a level costs by the product of what is added and what is already there: adding 1 to a level is about a thousand instructions, adding 10 is forty-five thousand, and adding 100 is four million. A run in round lots would cost a thousand times a run in tens and prove exactly the same thing.

What it does **not** cost is the size of the number. The amount added costs the sum of its bytes, each counted down once, so at most 255 a byte and 2,040 for an eight byte value however large: adding 256 is cheaper than adding 1, and adding a timestamp's worth of nanoseconds is cheaper than adding 255. No number here is unaffordable — only a middling one repeated often.

## Development

Updates are greatly appreciated; however, this entire repository is source generated...including the words you are reading right now. If you wish to suggest updates, the recommended process is to create an issue with changes and explanation. Time permitting, we will update the models and regenerate.


- Programs: 16
- Instructions: 5,649,798
- Reading every field the model states: 16 of 16
- Published with a frame they are held to: 16 of 16
- Frames, of which recorded from the wire: 150, 40
- Sessions, of which proven on a run: 1, 1
- Runs, and the packets they were answered with: 4, 4
- Markets, of which proven on a run: 2, 2
- Orders put to them, the trades those made and the orders refused: 14, 4, 4

## Testing

[![Build](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/actions/workflows/build.yml/badge.svg)](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/actions/workflows/build.yml)

`python3 check.py` makes two claims of different sizes. Every file here is held to being a program at all — a loop opened is a loop closed. Every program with a `.frame` beside it is also run on that frame and held to writing what its `.wrote` file records, which the script carries an interpreter of the stated dialect in order to do.

The second is a regression gate rather than a proof, and the difference is worth keeping straight. What makes a recorded output worth anything is that it was held against the C# parser reading the same bytes through the same model — field for field, in order, and accounting for every byte — before it was published. That comparison cannot be made here, because neither the models nor the parser are in this repository, so what the script says is that nothing has changed since. A program with no frame beside it is one that no frame could be laid out and proven for.

Please report any parsing errors as an [issue](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/issues "Omi Esoteric Issues"). Include the bytes the program was given and what it wrote, beside what the protocol says it should have.

## Open Markets Initiative

Other generated code can be found at [Omi Repositories](https://github.com/Open-Markets-Initiative/Directory/tree/main/Repositories "Open Markets Initiative Repositories"); for Omi rules and regulations, see [Omi Directory](https://github.com/Open-Markets-Initiative/Directory "Open Markets Initiative Directory").
## Disclaimer

Any similarities between existing people, places and/or protocols is purely incidental.

Enjoy.

