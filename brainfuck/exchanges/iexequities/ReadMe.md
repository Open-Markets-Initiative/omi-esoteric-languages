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
- Ipc `Iex.IexEquities.MatchingEngine.Ipc.v1.0`
- Engine `Iex.IexEquities.Equities.Open.Trading`
- Engine `Iex.IexEquities.Equities.Session.Trading`

## Market

`IexEquities.Market.bf` reads the internal order stream Investors Exchange Equities Open declares — `Iex.IexEquities.MatchingEngine.Ipc.v1.0` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out.

What was settled when the program was written rather than asked while it ran:

- the book holds the 32 prices from 9984 to 10015, which is the band of the declared reference 10000; a price outside it is refused
- an order is a quantity at a price and nothing else: the order id and the symbol are read and reported but not held, so nothing here can cancel an order or trade two securities
- packet.message.messagedata.orderrestedmessage.timestamp; packet.message.messagedata.trademessage.timestamp: marked SendTime; which asks whoever sends the message to stamp it from a clock; Brainfuck reads bytes and has no clock; so each published event carries the arriving order's timestamp instead: the time it was caused rather than the time it was sent
- the day is Simple, in the phases Closed then Continuous; it starts in Closed; a request to Open or Close moves it
- the chart answers a cancel by taking the order out of the book, and it does: the band is walked for the level remembering that identifier and the level is cleared. A level holds a summed quantity and one identifier, so this is exact while one order rests at a price and takes back both where two do

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published, and each was held to the parser and to a reference book in C# before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `IexEquities.Market.crossing` | 5 | 2 | 1 |
| `IexEquities.Market.cancelling` | 2 | 0 | 1 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `IexEquities.Market.bf` | the venue's book and the matching over it | 2 |

Beside each program is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `check.py` runs. A market also publishes a `.messages.json`, which is what it reads and writes flattened out of its model — that is what lets `run.py` build an order of your own rather than only replay what shipped.

## Running

Put a run of your own orders to the market and read back what it published, field by field:

```
python3 run.py brainfuck/exchanges/iexequities/IexEquities.Market.bf to Continuous , buy 1 7@9995 , sell 2 4@9995
```
Or replay a run that shipped with it:

```
python3 run.py brainfuck/exchanges/iexequities/IexEquities.Market.bf --frame brainfuck/exchanges/iexequities/IexEquities.Market.crossing.frame
```
Any interpreter will do that holds to the dialect these are generated for, which `brainfuck/dialect.bf` will ask yours about.

