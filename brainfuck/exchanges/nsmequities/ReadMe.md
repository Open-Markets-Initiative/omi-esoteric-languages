# Nasdaq Stock Market Basic

The programs generated from what Nasdaq Stock Market Basic declares, rather than from one protocol's model. A protocol's decoder is the same program whoever speaks it and sits under `brainfuck/protocols`; what is here is this venue's — the handshake it declares, and the book its own reference price bands.

## The venue, end to end

A venue is declared as components that talk through one internal protocol, and each of them is a program here. Each reads its input and writes its output, so they join with a pipe: what one writes is what the next reads.

| Program | Reads | Writes | What happens |
| --- | --- | --- | --- |
| `NsmEquities.Gateway.bf` | `Nasdaq.NsmEquities.Orders.Ouch.v5.0` | `Nasdaq.NsmEquities.BasicMatchingEngine.Ipc.v2026` | a client's requests become the venue's own orders, under the session chart |
| `NsmEquities.Market.bf` | `Nasdaq.NsmEquities.BasicMatchingEngine.Ipc.v2026` | `Nasdaq.NsmEquities.BasicMatchingEngine.Ipc.v2026` | the venue's own orders become its own events, by the trading chart |
| `NsmEquities.Responder.bf` | `Nasdaq.NsmEquities.Orders.Ouch.v5.0` then `Nasdaq.NsmEquities.BasicMatchingEngine.Ipc.v2026` | `Nasdaq.NsmEquities.Orders.Ouch.v5.0` | the client's requests and the venue's own events become the client's answers, by the transforms |
| `NsmEquities.TotalView.Feed.bf` | `Nasdaq.NsmEquities.BasicMatchingEngine.Ipc.v2026` | `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026` | the venue's own events become market data, by the transforms |

**To watch it happen**, from the root of the repository:

```
python3 demo.py NsmEquities
```
That runs every program in the table on the venue's `day` run and says in words what each read and wrote, step by step, with the book drawn after every step that changed it. Nothing it shows was recorded: each program is run there and then, by the interpreter `check.py` carries, and what it wrote is held to what is published for the run. It takes some tens of seconds, nearly all of it the market.

From the root of the repository, one published run through all of it - `xxd` turns the hexadecimal of a published frame into bytes and back:

```
xxd -r -p < brainfuck/exchanges/nsmequities/runs/gateway/crossing.frame \
  | bf brainfuck/exchanges/nsmequities/NsmEquities.Gateway.bf \
  | bf brainfuck/exchanges/nsmequities/NsmEquities.Market.bf \
  | bf brainfuck/exchanges/nsmequities/NsmEquities.TotalView.Feed.bf \
  | xxd -p
```
Every such join is stated in `manifest.json` at the root, as two files that hold the same bytes - what one program wrote and what the next was given - and `python3 check.py` holds each pair to it.

## Declared

What the venue says it speaks, read from its own declaration and not kept as a list here:

- Ipc `Nasdaq.NsmEquities.BasicMatchingEngine.Ipc.v2026`
- Engine `Nasdaq.NsmEquities.Equities.Basic.TradingSession`
- OrderEntry `Nasdaq.NsmEquities.Orders.Ouch.v5.0`, session `SoupBin.Tcp`
- Feed `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Replay `Nasdaq.NsmEquities.TotalView.Glimpse.v5.0.2026`
- Replay `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.Orders.Ouch.v5.0`

## Gateway

`NsmEquities.Gateway.bf` reads a client's packets in `Nasdaq.NsmEquities.Orders.Ouch.v5.0` and writes each request the venue's transforms name as one of the venue's own messages, which is what the market reads. It follows the session the venue's chart states, so a request is admitted only where that chart receives one.

What was settled when the program was written rather than asked while it ran:

- timestamp is when the sequencer took the message, and a program reading one file and writing another has no clock and is given no time by the request, so it is written as nought
- sequence is a message's place in the order the engine is sent them, which the venue's sequencer states; with one gateway and nothing between it and the engine, this counts them itself, from one
- the session is SoupBin Tcp: a connection opens in NotLoggedIn, and a request is admitted only while it rests in LoggedIn, which is where the chart receives the other end's own data. A login moves the connection as the chart says an accepted one does; whether to accept it is the session program's to say and was settled there
- it remembers the first 16 orders of a connection by the reference each came with, because a tape cannot grow; an order admitted after those is still admitted and numbered, and a later cancel naming it finds nothing

What the venue declares of its order entry that this program does not run, and why:

- the 10 responses it declares: each answers a client from an event of the engine and what the gateway remembers of the order, and a program reading one stream and writing one has the client's requests to read and the engine to write to, and neither the engine's events nor the client the other way round

Each run is a client's packets and what the gateway wrote for them. A run nobody logged in for is published with nothing written, because declining is half of what a gate does:

| Run | Requests | Bytes written |
| --- | ---: | ---: |
| `crossing` | 3 | 144 |
| `cancelling` | 3 | 123 |
| `unadmitted` | 3 | 0 |
| `day` | 8 | 363 |

## Market

`NsmEquities.Market.bf` reads the internal order stream Nasdaq Stock Market Basic declares — `Nasdaq.NsmEquities.BasicMatchingEngine.Ipc.v2026` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out.

What was settled when the program was written rather than asked while it ran:

- the book holds the 32 prices from 9984 to 10015, which is the band of the declared reference 10000; a price outside it is refused
- a refusal for a limit of this engine's own - a price outside the band, a side that remembers no more orders, a cancel naming no order it holds - is written with the venue's reason for Phase, because every reason the protocol states is marked for something else and it states none for anything else: a stated simplification, and the nearest of the venue's words rather than one of its own
- a level holds one summed quantity and remembers the identifier of the last order to rest there, so orders sharing a price are not held apart; the symbol is read and reported but not held, so one security is traded
- packet.message.messagedata.orderrestedmessage.timestamp; packet.message.messagedata.trademessage.timestamp: marked SendTime; which asks whoever sends the message to stamp it from a clock; Brainfuck reads bytes and has no clock; so each published event carries the arriving order's timestamp instead: the time it was caused rather than the time it was sent
- the day is Nasdaq Equities Basic, in the phases Continuous then Closed; it starts in Continuous; a request to Close or Open moves it
- each side remembers its resting orders one by one, oldest first, and 16 of them: a trade is made with the oldest order at the best price and names it, a cancel takes back the one order it names and leaves the rest of its price where it was, and an order arriving at a side that already holds 16 is refused rather than rested where it could not be found again
- the chart answers a cancel by taking the order out of the book, and it does: each side's remembered orders are walked for that identifier, and what is left of that one order comes off its price. Whatever else rests at the price stays

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published, and each was held to the parser and to a reference book in C# before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `crossing` | 5 | 2 | 1 |
| `cancelling` | 2 | 0 | 1 |
| `sharing` | 4 | 2 | 0 |
| `day` | 7 | 4 | 0 |
| `entered-crossing` | 3 | 1 | 0 |
| `entered-cancelling` | 3 | 0 | 0 |
| `entered-day` | 8 | 4 | 0 |

## Responder

`NsmEquities.Responder.bf` writes what a client is answered with, in `Nasdaq.NsmEquities.Orders.Ouch.v5.0`: each event of the engine's the venue's transforms declare an answer for, as that answer. An answer is written from two things at once - the engine's event, and what the client entered of the order it is about - and a program reads one input, so its input is the two joined: the client's packets exactly as the gateway read them, a packet stating no length, and then the venue's own events exactly as the market wrote them. It writes nothing for the requests; it reads them to remember each order entered, numbered as the gateway numbers them, which is how an event naming an order by its number finds what the client called it.

What was settled when the program was written rather than asked while it ran:

- timestamp is when an answer is sent where the engine's event does not say, and a program reading one file and writing another has no clock, so it is written as nought
- it reads the client's requests first and the engine's events after them, in one input: the requests end at a packet stating no length, which is where the gateway beside it stops reading too, and everything after that is the engine's
- an answer is written as its event is read, so every answer follows the last request; answers to one event are written in the order the venue's transforms declare them
- it remembers the first 16 orders of a connection, as the gateway beside it does and because a tape cannot grow; an event naming a later order is read and not answered

What the venue declares of its answers that this program does not write, and why:

- ouch_rejected_quantity: it turns a request away for its fields.quantity as the request arrives, and the gateway beside this admits every request its transforms name, so the engine is sent the order and answers for it
- ouch_rejected_price: it turns a request away for its fields.price as the request arrives, and the gateway beside this admits every request its transforms name, so the engine is sent the order and answers for it
- ouch_rejected_side: it turns a request away for its fields.side as the request arrives, and the gateway beside this admits every request its transforms name, so the engine is sent the order and answers for it
- ouch_rejected_symbol: it turns a request away for its fields.symbol as the request arrives, and the gateway beside this admits every request its transforms name, so the engine is sent the order and answers for it

Each run is the gateway's run of the same name and what the market wrote for it, joined, and the answers this wrote:

| Run | Bytes of requests | Bytes of events | Answers | Bytes written |
| --- | ---: | ---: | ---: | ---: |
| `crossing` | 202 | 232 | 5 | 279 |
| `cancelling` | 166 | 137 | 3 | 157 |
| `day` | 416 | 572 | 16 | 804 |

From the root of the repository, the same join made by hand - the client's requests, the packet stating no length, and what the gateway and the market make of those requests:

```
xxd -r -p < brainfuck/exchanges/nsmequities/runs/gateway/crossing.frame > requests
( cat requests; printf '\0\0'; bf brainfuck/exchanges/nsmequities/NsmEquities.Gateway.bf < requests | bf brainfuck/exchanges/nsmequities/NsmEquities.Market.bf ) \
  | bf brainfuck/exchanges/nsmequities/NsmEquities.Responder.bf | xxd -p
```
## Feeds

`NsmEquities.TotalView.Feed.bf` reads the venue's own events and writes each one the venue's transforms name as a packet of `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`, one message to a packet. It writes 3 of the 3 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- its times count from midnight in America/New_York, and a program with no clock library cannot ask when that zone changes, so the 260 changes from 1970 to the end of 2099 were read when it was written and are carried in it; a time past the last keeps the last offset

Each run is what the market wrote for the run of the same name, and the packets this wrote for it:

| Run | Packets |
| --- | ---: |
| `crossing` | 5 |
| `cancelling` | 3 |
| `sharing` | 6 |
| `day` | 10 |
| `entered-crossing` | 4 |
| `entered-cancelling` | 3 |
| `entered-day` | 10 |

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
- Timer.Heartbeat answers something that is not bytes, so no program with one input and one output can reach it
- Timer.Silence answers something that is not bytes, so no program with one input and one output can reach it
- entering Authenticating: Send Ask.Login goes somewhere that is not the wire
- entering LoggedIn: Send Timer.Heartbeat after State:HeartbeatInterval goes somewhere that is not the wire
- entering LoggedIn: Send Timer.Silence after State:SilenceInterval goes somewhere that is not the wire
- nothing dispatches to 'Client Soup Bin Tcp Packet', so Receive.Payload.Application arrives as a packet this state has no arm for, and is read and dropped like any other

One run per transition of the chart, named for the state it rests in and the packet that arrives. A run the session answers nothing to is published too, with an empty answer, because half of what a session does is decline to answer:

| Run | Packets answered |
| --- | ---: |
| `NotLoggedIn.LoginRequest` | 1 |
| `LoggedIn.SessionLogout` | 1 |
| `LoggedIn.SessionHeartbeat` | 1 |
| `LoggedIn.LoginRequest` | 1 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `NsmEquities.SoupBin.bf` | the venue's handshake | 4 |
| `NsmEquities.Gateway.bf` | the venue's order entry, under its session chart | 4 |
| `NsmEquities.Market.bf` | the venue's book and the matching over it | 7 |
| `NsmEquities.TotalView.Feed.bf` | the venue's TotalView feed | 7 |

Under `runs/`, in a folder named for each program, is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `check.py` runs. A market also publishes a `.messages.json`, which is what it reads and writes flattened out of its model — that is what lets `run.py` build an order of your own rather than only replay what shipped.

## Running

Put a run of your own orders to the market and read back what it published, field by field:

```
python3 run.py brainfuck/exchanges/nsmequities/NsmEquities.Market.bf to Continuous , buy 1 7@9995 , sell 2 4@9995
```
Or replay a run that shipped with it:

```
python3 run.py brainfuck/exchanges/nsmequities/NsmEquities.Market.bf --frame brainfuck/exchanges/nsmequities/runs/market/crossing.frame
```
A session is replayed rather than driven, because what it answers is decided by its chart and the packet that arrives:

```
bf brainfuck/exchanges/nsmequities/NsmEquities.SoupBin.bf < frame.bin
```
Any interpreter will do that holds to the dialect these are generated for, which `brainfuck/dialect.bf` will ask yours about.

