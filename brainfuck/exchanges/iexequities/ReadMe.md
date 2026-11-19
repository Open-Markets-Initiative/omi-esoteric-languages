# Investors Exchange Equities Basic

The programs generated from what Investors Exchange Equities Basic declares, rather than from one protocol's model. A protocol's decoder is the same program whoever speaks it and sits under `brainfuck/protocols`; what is here is this venue's — the handshake it declares, and the book its own reference price bands.

## The venue, end to end

A venue is declared as components that talk through one internal protocol, and each of them is a program here. Each reads its input and writes its output, so they join with a pipe: what one writes is what the next reads.

| Program | Reads | Writes | What happens |
| --- | --- | --- | --- |
| `IexEquities.Market.bf` | `Iex.IexEquities.BasicMatchingEngine.Ipc.v2026` | `Iex.IexEquities.BasicMatchingEngine.Ipc.v2026` | the venue's own orders become its own events, by the trading chart |
| `IexEquities.Tops.Feed.bf` | `Iex.IexEquities.BasicMatchingEngine.Ipc.v2026` | `Iex.IexEquities.Tops.IexTp.v1.66` | the venue's own events become market data, by the transforms |
| `IexEquities.Deep.Feed.bf` | `Iex.IexEquities.BasicMatchingEngine.Ipc.v2026` | `Iex.IexEquities.Deep.IexTp.v1.08` | the venue's own events become market data, by the transforms |
| `IexEquities.DeepPlus.Feed.bf` | `Iex.IexEquities.BasicMatchingEngine.Ipc.v2026` | `Iex.IexEquities.DeepPlus.IexTp.v1.05` | the venue's own events become market data, by the transforms |

**To watch it happen**, from the root of the repository:

```
python3 demo.py IexEquities
```
That runs every program in the table on the venue's `day` run and says in words what each read and wrote, step by step, with the book drawn after every step that changed it. Nothing it shows was recorded: each program is run there and then, by the interpreter `check.py` carries, and what it wrote is held to what is published for the run. It takes some tens of seconds, nearly all of it the market.

From the root of the repository, one published run through all of it - `xxd` turns the hexadecimal of a published frame into bytes and back:

```
xxd -r -p < brainfuck/exchanges/iexequities/runs/market/crossing.frame \
  | bf brainfuck/exchanges/iexequities/IexEquities.Market.bf \
  | bf brainfuck/exchanges/iexequities/IexEquities.Tops.Feed.bf \
  | xxd -p
```
Every such join is stated in `manifest.json` at the root, as two files that hold the same bytes - what one program wrote and what the next was given - and `python3 check.py` holds each pair to it.

## Declared

What the venue says it speaks, read from its own declaration and not kept as a list here:

- OrderEntry `Iex.IexEquities.OrderEntry.Fix.v2.91`, session `Fix`
- Feed `Iex.IexEquities.Tops.IexTp.v1.66`
- Feed `Iex.IexEquities.Deep.IexTp.v1.08`
- Feed `Iex.IexEquities.DeepPlus.IexTp.v1.05`
- Snap `Iex.IexEquities.Deep.Snap.v1.6`
- Snap `Iex.IexEquities.Tops.Snap.v1.6`
- Snap `Iex.IexEquities.DeepPlus.Snap.v1.06`
- Ipc `Iex.IexEquities.BasicMatchingEngine.Ipc.v2026`
- Engine `Iex.IexEquities.Equities.Basic.TradingSession`

## Market

`IexEquities.Market.bf` reads the internal order stream Investors Exchange Equities Basic declares — `Iex.IexEquities.BasicMatchingEngine.Ipc.v2026` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out.

What was settled when the program was written rather than asked while it ran:

- the book holds the 32 prices from 9984 to 10015, which is the band of the declared reference 10000; a price outside it is refused
- a refusal for a limit of this engine's own - a price outside the band, a side that remembers no more orders, a cancel naming no order it holds - is written with the venue's reason for Phase, because every reason the protocol states is marked for something else and it states none for anything else: a stated simplification, and the nearest of the venue's words rather than one of its own
- a level holds one summed quantity and remembers the identifier of the last order to rest there, so orders sharing a price are not held apart; the symbol is read and reported but not held, so one security is traded
- packet.message.messagedata.orderrestedmessage.timestamp; packet.message.messagedata.trademessage.timestamp: marked SendTime; which asks whoever sends the message to stamp it from a clock; Brainfuck reads bytes and has no clock; so each published event carries the arriving order's timestamp instead: the time it was caused rather than the time it was sent
- the day is Iex Equities Basic, in the phases Continuous then Closed; it starts in Continuous; a request to Close or Open moves it
- each side remembers its resting orders one by one, oldest first, and 16 of them: a trade is made with the oldest order at the best price and names it, a cancel takes back the one order it names and leaves the rest of its price where it was, and an order arriving at a side that already holds 16 is refused rather than rested where it could not be found again
- the chart answers a cancel by taking the order out of the book, and it does: each side's remembered orders are walked for that identifier, and what is left of that one order comes off its price. Whatever else rests at the price stays

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published, and each was held to the parser and to a reference book in C# before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `crossing` | 5 | 2 | 1 |
| `cancelling` | 2 | 0 | 1 |
| `sharing` | 4 | 2 | 0 |
| `day` | 7 | 4 | 0 |

## Feeds

`IexEquities.Tops.Feed.bf` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.Tops.IexTp.v1.66`, one message to a packet. It writes 2 of the 2 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market wrote for the run of the same name, and the packets this wrote for it:

| Run | Packets |
| --- | ---: |
| `crossing` | 3 |
| `cancelling` | 2 |
| `sharing` | 3 |
| `day` | 5 |

`IexEquities.Deep.Feed.bf` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.Deep.IexTp.v1.08`, one message to a packet. It writes 3 of the 3 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market wrote for the run of the same name, and the packets this wrote for it:

| Run | Packets |
| --- | ---: |
| `crossing` | 5 |
| `cancelling` | 2 |
| `sharing` | 5 |
| `day` | 9 |

`IexEquities.DeepPlus.Feed.bf` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.DeepPlus.IexTp.v1.05`, one message to a packet. It writes 2 of the 2 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market wrote for the run of the same name, and the packets this wrote for it:

| Run | Packets |
| --- | ---: |
| `crossing` | 5 |
| `cancelling` | 2 |
| `sharing` | 5 |
| `day` | 9 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `IexEquities.Market.bf` | the venue's book and the matching over it | 4 |
| `IexEquities.Tops.Feed.bf` | the venue's Tops feed | 4 |
| `IexEquities.Deep.Feed.bf` | the venue's Deep feed | 4 |
| `IexEquities.DeepPlus.Feed.bf` | the venue's DeepPlus feed | 4 |

Under `runs/`, in a folder named for each program, is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `check.py` runs. A market also publishes a `.messages.json`, which is what it reads and writes flattened out of its model — that is what lets `run.py` build an order of your own rather than only replay what shipped.

## What the programs are made of

| Program | `+` | `-` | `<` | `>` | `[` | `]` | `.` | `,` | All |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `IexEquities.Market.bf` | 400,111 | 112,157 | 13,046,698 | 13,047,597 | 129,795 | 129,795 | 248 | 103 | 26,866,504 |
| `IexEquities.Tops.Feed.bf` | 2,963 | 3,414 | 33,178 | 33,196 | 3,751 | 3,751 | 168 | 48 | 80,469 |
| `IexEquities.Deep.Feed.bf` | 4,575 | 5,669 | 70,239 | 70,257 | 6,281 | 6,281 | 224 | 103 | 163,629 |
| `IexEquities.DeepPlus.Feed.bf` | 3,753 | 4,646 | 42,947 | 42,965 | 5,122 | 5,122 | 160 | 103 | 104,818 |

## Running

Put a run of your own orders to the market and read back what it published, field by field:

```
python3 run.py brainfuck/exchanges/iexequities/IexEquities.Market.bf to Continuous , buy 1 7@9995 , sell 2 4@9995
```
Or replay a run that shipped with it:

```
python3 run.py brainfuck/exchanges/iexequities/IexEquities.Market.bf --frame brainfuck/exchanges/iexequities/runs/market/crossing.frame
```
Any interpreter will do that holds to the dialect these are generated for, which `brainfuck/dialect.bf` will ask yours about.

