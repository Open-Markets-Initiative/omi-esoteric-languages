# Investors Exchange Equities Open

The Emojicode programs generated from what Investors Exchange Equities Open declares, rather than from one protocol's model. A protocol's decoder is the same program whoever speaks it and sits under `emojicode/protocols`; what is here is this venue's own — the book over its own internal order stream.

The same venue's programs in the repository's other language sit at the same path under that language's directory. They are not these with the emoji changed: each was generated from the models by its own backend, and the two do not come to the same program. Where they agree, what they agree on is the model.

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

A venue is declared as components that talk through one internal protocol, and each of them is a program here. Each reads one file and writes another, so they join by a file: what one is told to write is what the next is told to read.

| Program | Reads | Writes | What happens |
| --- | --- | --- | --- |
| `IexEquities.Market.emojic` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | the venue's own orders become its own events, by the trading chart |
| `IexEquities.Tops.Feed.emojic` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.Tops.IexTp.v1.66` | the venue's own events become market data, by the transforms |
| `IexEquities.Deep.Feed.emojic` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.Deep.IexTp.v1.08` | the venue's own events become market data, by the transforms |
| `IexEquities.DeepPlus.Feed.emojic` | `Iex.IexEquities.MatchingEngine.Ipc.v2026` | `Iex.IexEquities.DeepPlus.IexTp.v1.05` | the venue's own events become market data, by the transforms |

## Market

`IexEquities.Market.emojic` reads the internal order stream Investors Exchange Equities Open declares — `Iex.IexEquities.MatchingEngine.Ipc.v2026` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out. It runs the `Iex Equities Open` day, and stamps every message it publishes with the security that day is declared for.

**Its book holds whatever price arrives.** A level is reached by its price rather than by an index into a tape, so nothing here is banded around a declared reference and no order is refused for being far from one. What this market does refuse, it refuses because the day it runs says to.

What was settled when the program was written rather than asked while it ran:

- the day is Iex Equities Open, in the phases Continuous; it starts in Continuous
- an order is a quantity at a price: the book holds whatever price arrives, because a list reaches a level by value and not by an index that has to fit in a byte

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published. Each was held to the C# parser on both halves, and to a second book in C# that must agree on every trade, before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `IexEquities.Market.crossing` | 3 | 1 | 0 |
| `IexEquities.Market.sweeping` | 3 | 2 | 0 |
| `IexEquities.Market.selling` | 2 | 1 | 0 |
| `IexEquities.Market.cancelling` | 2 | 0 | 0 |
| `IexEquities.Market.replacing` | 6 | 2 | 0 |
| `IexEquities.Market.declining` | 3 | 1 | 1 |

## Feeds

`IexEquities.Tops.Feed.emojic` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.Tops.IexTp.v1.66`, one message to a packet. It writes 7 of the 7 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market should write for the run of the same name, and the packets this should write for it:

| Run | Packets |
| --- | ---: |
| `IexEquities.Tops.Feed.crossing` | 3 |
| `IexEquities.Tops.Feed.sweeping` | 3 |
| `IexEquities.Tops.Feed.selling` | 1 |
| `IexEquities.Tops.Feed.cancelling` | 2 |
| `IexEquities.Tops.Feed.replacing` | 3 |
| `IexEquities.Tops.Feed.declining` | 1 |

`IexEquities.Deep.Feed.emojic` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.Deep.IexTp.v1.08`, one message to a packet. It writes 10 of the 10 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market should write for the run of the same name, and the packets this should write for it:

| Run | Packets |
| --- | ---: |
| `IexEquities.Deep.Feed.crossing` | 4 |
| `IexEquities.Deep.Feed.sweeping` | 5 |
| `IexEquities.Deep.Feed.selling` | 2 |
| `IexEquities.Deep.Feed.cancelling` | 2 |
| `IexEquities.Deep.Feed.replacing` | 5 |
| `IexEquities.Deep.Feed.declining` | 2 |

`IexEquities.DeepPlus.Feed.emojic` reads the venue's own events and writes each one the venue's transforms name as a packet of `Iex.IexEquities.DeepPlus.IexTp.v1.05`, one message to a packet. It writes 6 of the 6 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.iextpheader.sessionid names the session, and the venue declares none for it, so it is written as nothing
- packet.iextpheader.sendtime asks when the packet was sent, and a program reading one file and writing another has no clock, so it carries the time of the event it publishes

Each run is what the market should write for the run of the same name, and the packets this should write for it:

| Run | Packets |
| --- | ---: |
| `IexEquities.DeepPlus.Feed.crossing` | 4 |
| `IexEquities.DeepPlus.Feed.sweeping` | 5 |
| `IexEquities.DeepPlus.Feed.selling` | 2 |
| `IexEquities.DeepPlus.Feed.cancelling` | 2 |
| `IexEquities.DeepPlus.Feed.replacing` | 5 |
| `IexEquities.DeepPlus.Feed.declining` | 2 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `IexEquities.Market.emojic` | the venue's book and the matching over it | 6 |
| `IexEquities.Tops.Feed.emojic` | the venue's Tops feed | 6 |
| `IexEquities.Deep.Feed.emojic` | the venue's Deep feed | 6 |
| `IexEquities.DeepPlus.Feed.emojic` | the venue's DeepPlus feed | 6 |

Under `runs/`, in a folder named for each program, is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `replay.py` compiles each program against. They are written as hexadecimal because a frame holds any byte a protocol can carry and so does a program's output, so neither is text.

## Running

A program here is **compiled first, and then takes two paths**: the file to read and the file to write. Emojicode 1.0 beta 2 has no standard input — the file package is the only way in or out — so nothing here is piped.

The compiler looks for its own packages in the directory it is run from, so that directory is where one of these is built and run — which is this one, and the lines below change to it from the root of the repository rather than leaving where you are standing to be guessed at. It is the directory it is run from and not the one the program is in, so the packages have to be reachable from here too; `emojicode/ReadMe.md` says how, and the line that does it is the one line below that is not about this venue.

Compile one of these, and run it on a frame published beside it. A published frame is hexadecimal, so it is turned back into bytes first, and so is the output it is held to:

```
cd emojicode/exchanges/iexequities
ln -s /path/to/Emojicode-1.0-beta.2-Linux-x86_64/packages packages
emojicodec IexEquities.Market.emojic
xxd -r -p < runs/market/crossing.frame > frame.bin
./IexEquities.Market frame.bin wrote.bin
xxd -r -p < runs/market/crossing.wrote > want.bin
cmp want.bin wrote.bin
```
`replay.py` at the root does that for every program in this language and holds what each writes to the `.wrote` beside it, so a change here is caught without anybody running one by hand:

```
export EMOJICODEC=/path/to/emojicodec
python3 replay.py
```
The repository's `run.py`, which builds a stream of orders of your own and reads back what a market published, does **not** drive these. It carries an interpreter for a language of eight instructions, and no script carries a 56 megabyte compiler; it works on the other language's markets, whose layouts are published beside them.

