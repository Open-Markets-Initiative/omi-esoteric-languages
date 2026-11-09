# Nasdaq Stock Market Day

The programs generated from what Nasdaq Stock Market Day declares, rather than from one protocol's model. A protocol's decoder is the same program whoever speaks it and sits under `brainfuck/protocols`; what is here is this venue's — the handshake it declares, and the book its own reference price bands.

## Declared

What the venue says it speaks, read from its own declaration and not kept as a list here:

- Ipc `Nasdaq.NsmEquities.MatchingEngine.Ipc.v2026`
- Engine `Nasdaq.NsmEquities.Equities.Session.Trading`
- OrderEntry `Nasdaq.NsmEquities.Orders.Ouch.v5.0`, session `SoupBin.Tcp`
- Feed `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Replay `Nasdaq.NsmEquities.TotalView.Glimpse.v5.0`
- Replay `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.Orders.Ouch.v5.0`
- Engine `Nasdaq.NsmEquities.Equities.Open.Trading`

## Market

`NsmEquities.Market.bf` reads the internal order stream Nasdaq Stock Market Day declares — `Nasdaq.NsmEquities.MatchingEngine.Ipc.v2026` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out.

What was settled when the program was written rather than asked while it ran:

- the book holds the 32 prices from 9984 to 10015, which is the band of the declared reference 10000; a price outside it is refused
- an order is a quantity at a price and nothing else: the order id and the symbol are read and reported but not held, so nothing here can cancel an order or trade two securities
- packet.message.messagedata.orderrestedmessage.timestamp; packet.message.messagedata.trademessage.timestamp: marked SendTime; which asks whoever sends the message to stamp it from a clock; Brainfuck reads bytes and has no clock; so each published event carries the arriving order's timestamp instead: the time it was caused rather than the time it was sent
- the day is Simple, in the phases Closed then Continuous; it starts in Closed; a request to Open or Close moves it
- the chart answers a cancel by taking the order out of the book, and it does: the band is walked for the level remembering that identifier and the level is cleared. A level holds a summed quantity and one identifier, so this is exact while one order rests at a price and takes back both where two do

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published, and each was held to the parser and to a reference book in C# before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `NsmEquities.Market.crossing` | 5 | 2 | 1 |
| `NsmEquities.Market.cancelling` | 2 | 0 | 1 |

## Session

`NsmEquities.SoupBin.bf` runs the chart `Nasdaq.SoupBinTcp` over `Nasdaq.NsmEquities.Orders.Ouch.v5.0`: it reads the other end's packets from standard input, holds a state, and writes the answers the chart says to write.

What was settled when the program was written rather than asked while it ran:

- Authenticating: Handler.Login.Accepted is taken as the chart writes it, so the program never asks
- 'Accepted Session' answers the opening SessionId, which the chart states no value for, so it is written as a venue pads an unset field

Transitions of the chart no program with one input and one output can run, because a Request, a Handler or an Ask has nowhere to put a question and nobody to ask it of:

- Request.ResumeFrom answers something that is not bytes, so no program with one input and one output can reach it
- Request.Sequenced answers something that is not bytes, so no program with one input and one output can reach it
- Request.Heartbeat answers something that is not bytes, so no program with one input and one output can reach it
- Request.EndOfSession answers something that is not bytes, so no program with one input and one output can reach it
- entering Authenticating: Send Ask.Login goes somewhere that is not the wire
- nothing dispatches to 'Client Soup Bin Tcp Packet', so Receive.Payload.Application arrives as a packet this state has no arm for, and is read and dropped like any other

One run per transition of the chart, named for the state it rests in and the packet that arrives. A run the session answers nothing to is published too, with an empty answer, because half of what a session does is decline to answer:

| Run | Packets answered |
| --- | ---: |
| `NsmEquities.SoupBin.NotLoggedIn.LoginRequest` | 1 |
| `NsmEquities.SoupBin.LoggedIn.SessionLogout` | 1 |
| `NsmEquities.SoupBin.LoggedIn.SessionHeartbeat` | 1 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `NsmEquities.SoupBin.bf` | the venue's handshake | 3 |
| `NsmEquities.Market.bf` | the venue's book and the matching over it | 2 |

Beside each program is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `check.py` runs. A market also publishes a `.messages.json`, which is what it reads and writes flattened out of its model — that is what lets `run.py` build an order of your own rather than only replay what shipped.

## Running

Put a run of your own orders to the market and read back what it published, field by field:

```
python3 run.py brainfuck/exchanges/nsmequities/NsmEquities.Market.bf to Continuous , buy 1 7@9995 , sell 2 4@9995
```
Or replay a run that shipped with it:

```
python3 run.py brainfuck/exchanges/nsmequities/NsmEquities.Market.bf --frame brainfuck/exchanges/nsmequities/NsmEquities.Market.crossing.frame
```
A session is replayed rather than driven, because what it answers is decided by its chart and the packet that arrives:

```
bf brainfuck/exchanges/nsmequities/NsmEquities.SoupBin.bf < frame.bin
```
Any interpreter will do that holds to the dialect these are generated for, which `brainfuck/dialect.bf` will ask yours about.

