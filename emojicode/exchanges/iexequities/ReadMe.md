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
- Ipc `Iex.IexEquities.MatchingEngine.Ipc.v1.0`
- Engine `Iex.IexEquities.Equities.Open.Trading`
- Engine `Iex.IexEquities.Equities.Session.Trading`

## Market

`IexEquities.Market.emojic` reads the internal order stream Investors Exchange Equities Open declares — `Iex.IexEquities.MatchingEngine.Ipc.v1.0` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out. It runs the `Simple` day, and stamps every message it publishes with the security that day is declared for.

**Its book holds whatever price arrives.** A level is reached by its price rather than by an index into a tape, so nothing here is banded around a declared reference and no order is refused for being far from one. What this market does refuse, it refuses because the day it runs says to.

What was settled when the program was written rather than asked while it ran:

- the day is Simple, in the phases Closed then Continuous; it starts in Closed
- an order is a quantity at a price: the book holds whatever price arrives, because a list reaches a level by value and not by an index that has to fit in a byte

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published. Each was held to the C# parser on both halves, and to a second book in C# that must agree on every trade, before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `IexEquities.Market.refusing` | 1 | 0 | 1 |
| `IexEquities.Market.crossing` | 3 | 1 | 0 |
| `IexEquities.Market.sweeping` | 3 | 2 | 0 |
| `IexEquities.Market.selling` | 2 | 1 | 0 |
| `IexEquities.Market.cancelling` | 2 | 0 | 0 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `IexEquities.Market.emojic` | the venue's book and the matching over it | 5 |

Beside each program is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `replay.py` compiles each program against. They are written as hexadecimal because a frame holds any byte a protocol can carry and so does a program's output, so neither is text.

## Running

A program here is **compiled first, and then takes two paths**: the file to read and the file to write. Emojicode 1.0 beta 2 has no standard input — the file package is the only way in or out — so nothing here is piped.

The compiler looks for its own packages in the directory it is run from, so that directory is where one of these is built and run — which is this one, and the lines below change to it from the root of the repository rather than leaving where you are standing to be guessed at. It is the directory it is run from and not the one the program is in, so the packages have to be reachable from here too; `emojicode/ReadMe.md` says how, and the line that does it is the one line below that is not about this venue.

Compile one of these, and run it on a frame published beside it. A published frame is hexadecimal, so it is turned back into bytes first, and so is the output it is held to:

```
cd emojicode/exchanges/iexequities
ln -s /path/to/Emojicode-1.0-beta.2-Linux-x86_64/packages packages
emojicodec IexEquities.Market.emojic
xxd -r -p < IexEquities.Market.refusing.frame > frame.bin
./IexEquities.Market frame.bin wrote.bin
xxd -r -p < IexEquities.Market.refusing.wrote > want.bin
cmp want.bin wrote.bin
```
`replay.py` at the root does that for every program in this language and holds what each writes to the `.wrote` beside it, so a change here is caught without anybody running one by hand:

```
export EMOJICODEC=/path/to/emojicodec
python3 replay.py
```
The repository's `run.py`, which builds a stream of orders of your own and reads back what a market published, does **not** drive these. It carries an interpreter for a language of eight instructions, and no script carries a 56 megabyte compiler; it works on the other language's markets, whose layouts are published beside them.

