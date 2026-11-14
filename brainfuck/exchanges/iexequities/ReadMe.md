# Investors Exchange Equities Open

The programs generated from what Investors Exchange Equities Open declares, rather than from one protocol's model. A protocol's decoder is the same program whoever speaks it and sits under `brainfuck/protocols`; what is here is this venue's — the handshake it declares, and the book its own reference price bands.

## Declared

What the venue says it speaks, read from its own declaration and not kept as a list here:

- OrderEntry `Iex.IexEquities.OrderEntry.Fix.v2.91`, session `Fix`
- Feed `Iex.IexEquities.Tops.IexTp.v1.66`
- Feed `Iex.IexEquities.Deep.IexTp.v1.08`
- Feed `Iex.IexEquities.DeepPlus.IexTp.v1.05`
- Snap `Iex.IexEquities.Deep.Snap.v1.6`
- Snap `Iex.IexEquities.Tops.Snap.v1.6`
- Snap `Iex.IexEquities.DeepPlus.Snap.v1.06`
- Ipc `Iex.IexEquities.MatchingEngine.Ipc.v2026`
- Engine `Iex.IexEquities.Equities.Open.Trading`
- Engine `Iex.IexEquities.Equities.Session.Trading`

## The venue, end to end

A venue is declared as components that talk through one internal protocol, and each of them is a program here. Each reads its input and writes its output, so they join with a pipe: what one writes is what the next reads.

| Program | Reads | Writes | What happens |
| --- | --- | --- | --- |
| `IexEquities.Market.bf` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | the venue's own orders become its own events, by the trading chart |
| `IexEquities.Tops.Feed.bf` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.Tops.IexTp.v1.66` | the venue's own events become market data, by the transforms |
| `IexEquities.Deep.Feed.bf` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.Deep.IexTp.v1.08` | the venue's own events become market data, by the transforms |
| `IexEquities.DeepPlus.Feed.bf` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.DeepPlus.IexTp.v1.05` | the venue's own events become market data, by the transforms |

From the root of the repository, one published run through all of it - `xxd` turns the hexadecimal of a published frame into bytes and back:

```
xxd -r -p < brainfuck/exchanges/iexequities/runs/market/crossing.frame \
  | bf brainfuck/exchanges/iexequities/IexEquities.Market.bf \
  | bf brainfuck/exchanges/iexequities/IexEquities.Tops.Feed.bf \
  | xxd -p
```
Every such join is stated in `manifest.json` at the root, as two files that hold the same bytes - what one program wrote and what the next was given - and `python3 check.py` holds each pair to it.

## Market

`IexEquities.Market.bf` reads the internal order stream Investors Exchange Equities Open declares — `Iex.IexEquities.MatchingEngine.Ipc.v2026` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out.

What was settled when the program was written rather than asked while it ran:

- the book holds the 32 prices from 9984 to 10015, which is the band of the declared reference 10000; a price outside it is refused
- a refusal for a limit of this engine's own - a price outside the band, a side that remembers no more orders, a cancel naming no order it holds - is written with the venue's reason for Phase, because every reason the protocol states is marked for something else and it states none for anything else: a stated simplification, and the nearest of the venue's words rather than one of its own
- the chart answers an arriving order by what the order is, and so does this: each phase's answers are tried in the order the chart states them and the first whose conditions the order meets is the one it gets, with the reason the chart gives where that is a refusal. A word the protocol has no code for is a word no order is, and a code the venue marks with no word is none of the words
- a level holds one summed quantity and remembers the identifier of the last order to rest there, so orders sharing a price are not held apart; the symbol is read and reported but not held, so one security is traded
- packet.message.messagedata.orderrestedmessage.timestamp; packet.message.messagedata.trademessage.timestamp: marked SendTime; which asks whoever sends the message to stamp it from a clock; Brainfuck reads bytes and has no clock; so each published event carries the arriving order's timestamp instead: the time it was caused rather than the time it was sent
- the day is Iex Equities Open, in the phases Continuous; it starts in Continuous; the chart states no change of phase, so it stays there and nothing asks it to move
- the chart answers a replace by crossing it, and it does: the order replaced is found by its identifier and taken back without a word, and the replacement goes into the book as an arriving order does, behind whatever already rests at its price, reported as the venue's own replace under both numbers rather than as an order resting. It is reported as it rests, before it trades, the way this engine reports any order
- each side remembers its resting orders one by one, oldest first, and 16 of them: a trade is made with the oldest order at the best price and names it, a cancel takes back the one order it names and leaves the rest of its price where it was, and an order arriving at a side that already holds 16 is refused rather than rested where it could not be found again
- the chart answers a cancel by taking the order out of the book, and it does: each side's remembered orders are walked for that identifier, and what is left of that one order comes off its price. Whatever else rests at the price stays

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published, and each was held to the parser and to a reference book in C# before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `IexEquities.Market.crossing` | 5 | 2 | 1 |
| `IexEquities.Market.cancelling` | 2 | 0 | 1 |
| `IexEquities.Market.sharing` | 4 | 2 | 0 |
| `IexEquities.Market.declining` | 3 | 1 | 1 |
| `IexEquities.Market.replacing` | 4 | 1 | 0 |

## Feeds

`IexEquities.Tops.Feed.bf` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.Tops.IexTp.v1.66`, one message to a packet. It writes 7 of the 7 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market wrote for the run of the same name, and the packets this wrote for it:

| Run | Packets |
| --- | ---: |
| `IexEquities.Tops.Feed.crossing` | 4 |
| `IexEquities.Tops.Feed.cancelling` | 2 |
| `IexEquities.Tops.Feed.sharing` | 4 |
| `IexEquities.Tops.Feed.declining` | 2 |
| `IexEquities.Tops.Feed.replacing` | 2 |

`IexEquities.Deep.Feed.bf` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.Deep.IexTp.v1.08`, one message to a packet. It writes 10 of the 10 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market wrote for the run of the same name, and the packets this wrote for it:

| Run | Packets |
| --- | ---: |
| `IexEquities.Deep.Feed.crossing` | 6 |
| `IexEquities.Deep.Feed.cancelling` | 2 |
| `IexEquities.Deep.Feed.sharing` | 6 |
| `IexEquities.Deep.Feed.declining` | 3 |
| `IexEquities.Deep.Feed.replacing` | 3 |

`IexEquities.DeepPlus.Feed.bf` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.DeepPlus.IexTp.v1.05`, one message to a packet. It writes 6 of the 6 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market wrote for the run of the same name, and the packets this wrote for it:

| Run | Packets |
| --- | ---: |
| `IexEquities.DeepPlus.Feed.crossing` | 6 |
| `IexEquities.DeepPlus.Feed.cancelling` | 2 |
| `IexEquities.DeepPlus.Feed.sharing` | 6 |
| `IexEquities.DeepPlus.Feed.declining` | 3 |
| `IexEquities.DeepPlus.Feed.replacing` | 3 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `IexEquities.Market.bf` | the venue's book and the matching over it | 5 |
| `IexEquities.Tops.Feed.bf` | the venue's Tops feed | 5 |
| `IexEquities.Deep.Feed.bf` | the venue's Deep feed | 5 |
| `IexEquities.DeepPlus.Feed.bf` | the venue's DeepPlus feed | 5 |

Under `runs/`, in a folder named for each program, is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `check.py` runs. A market also publishes a `.messages.json`, which is what it reads and writes flattened out of its model — that is what lets `run.py` build an order of your own rather than only replay what shipped.

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

