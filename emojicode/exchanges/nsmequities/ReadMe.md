# Nasdaq Stock Market Open

The Emojicode programs generated from what Nasdaq Stock Market Open declares, rather than from one protocol's model. A protocol's decoder is the same program whoever speaks it and sits under `emojicode/protocols`; what is here is this venue's own — the handshake it declares, and the book over its own internal order stream.

The same venue's programs in the repository's other language sit at the same path under that language's directory. They are not these with the emoji changed: each was generated from the models by its own backend, and the two do not come to the same program. Where they agree, what they agree on is the model.

## Declared

What the venue says it speaks, read from its own declaration and not kept as a list here:

- Ipc `Nasdaq.NsmEquities.MatchingEngine.Ipc.v2026`
- Engine `Nasdaq.NsmEquities.Equities.Open.Trading`
- OrderEntry `Nasdaq.NsmEquities.Orders.Ouch.v5.0`, session `SoupBin.Tcp`
- Feed `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Replay `Nasdaq.NsmEquities.TotalView.Glimpse.v5.0`
- Replay `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.TotalView.Itch.v5.0.2026`
- Trader `Nasdaq.NsmEquities.Orders.Ouch.v5.0`
- Engine `Nasdaq.NsmEquities.Equities.Session.Trading`

## Market

`NsmEquities.Market.emojic` reads the internal order stream Nasdaq Stock Market Open declares — `Nasdaq.NsmEquities.MatchingEngine.Ipc.v2026` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out. It runs the `Simple` day, and stamps every message it publishes with the security that day is declared for.

**Its book holds whatever price arrives.** A level is reached by its price rather than by an index into a tape, so nothing here is banded around a declared reference and no order is refused for being far from one. What this market does refuse, it refuses because the day it runs says to.

What was settled when the program was written rather than asked while it ran:

- the day is Simple, in the phases Closed then Continuous; it starts in Closed
- an order is a quantity at a price: the book holds whatever price arrives, because a list reaches a level by value and not by an index that has to fit in a byte

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published. Each was held to the C# parser on both halves, and to a second book in C# that must agree on every trade, before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `NsmEquities.Market.refusing` | 1 | 0 | 1 |
| `NsmEquities.Market.crossing` | 3 | 1 | 0 |
| `NsmEquities.Market.sweeping` | 3 | 2 | 0 |
| `NsmEquities.Market.selling` | 2 | 1 | 0 |
| `NsmEquities.Market.cancelling` | 2 | 0 | 0 |

## Session

`NsmEquities.SoupBin.emojic` runs the chart `Nasdaq.SoupBinTcp` over `Nasdaq.NsmEquities.Orders.Ouch.v5.0`: it reads the other end's packets out of the file named by its first argument, holds the state the connection is in and the data the chart says it keeps, and writes the venue's own answers to the file named by its second.

**It reads the packet that arrived.** A reply field can be filled from a field of the packet that asked for it, and a guard can be run on one — so where the chart tells two answers apart by what the other end asked for, the program runs that guard rather than having it settled before it started. The runs below are named for the way each one takes, so a chart that states more than one way of answering a packet publishes a run for each.

What was settled when the program was written rather than asked while it ran:

- SessionId is answered in 'Accepted Session', and the chart states no value it opens with, so it is written as a venue pads an unset field
- Authenticating: Handler.Login.Accepted is taken as the chart writes it, so the program never asks; the 2 ways the chart tells that answer apart are guards on the arriving packet, and those are run

Transitions of the chart no program reading one file and writing another can run, because a Request, an Ask, a Handler or a Timer has nowhere to put a question, nobody to ask it of and no clock to read:

- Ask.Login is put to a handler, and a program reading one file and writing another has nobody to put it to
- Timer.Heartbeat is armed to fire after a wait, and a program reading one file and writing another has no clock to wait on
- Timer.Silence is armed to fire after a wait, and a program reading one file and writing another has no clock to wait on
- Request.ResumeFrom answers something that is not bytes, so no program reading one file and writing another can reach it
- Receive.Payload.Application is the other end's own data rather than one packet this protocol names, so nothing in the frame tells it apart from the session's own packets
- Handler.Logout is put to a handler, and a program reading one file and writing another has nobody to put it to
- Request.Sequenced answers something that is not bytes, so no program reading one file and writing another can reach it
- Request.Heartbeat answers something that is not bytes, so no program reading one file and writing another can reach it
- Request.EndOfSession answers something that is not bytes, so no program reading one file and writing another can reach it
- Timer.Heartbeat answers something that is not bytes, so no program reading one file and writing another can reach it
- Timer.Silence answers something that is not bytes, so no program reading one file and writing another can reach it

One run per way the chart states of answering a packet, named for the state it rests in, the packet that arrives and the way taken. A run the session answers nothing to is published too, with an empty `.wrote`, because half of what a session does is decline to answer:

| Run | Packets answered |
| --- | ---: |
| `NsmEquities.SoupBin.NotLoggedIn.LoginRequest.RequestedSequenceNumber` | 1 |
| `NsmEquities.SoupBin.NotLoggedIn.LoginRequest` | 1 |
| `NsmEquities.SoupBin.LoggedIn.SessionLogout` | 1 |
| `NsmEquities.SoupBin.LoggedIn.SessionHeartbeat` | 1 |
| `NsmEquities.SoupBin.LoggedIn.LoginRequest` | 1 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `NsmEquities.SoupBin.emojic` | the venue's handshake | 5 |
| `NsmEquities.Market.emojic` | the venue's book and the matching over it | 5 |

Beside each program is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `replay.py` compiles each program against. They are written as hexadecimal because a frame holds any byte a protocol can carry and so does a program's output, so neither is text.

## Running

A program here is **compiled first, and then takes two paths**: the file to read and the file to write. Emojicode 1.0 beta 2 has no standard input — the file package is the only way in or out — so nothing here is piped.

The compiler looks for its own packages in the directory it is run from, so that directory is where one of these is built and run — which is this one, and the lines below change to it from the root of the repository rather than leaving where you are standing to be guessed at. It is the directory it is run from and not the one the program is in, so the packages have to be reachable from here too; `emojicode/ReadMe.md` says how, and the line that does it is the one line below that is not about this venue.

Compile one of these, and run it on a frame published beside it. A published frame is hexadecimal, so it is turned back into bytes first, and so is the output it is held to:

```
cd emojicode/exchanges/nsmequities
ln -s /path/to/Emojicode-1.0-beta.2-Linux-x86_64/packages packages
emojicodec NsmEquities.SoupBin.emojic
xxd -r -p < NsmEquities.SoupBin.NotLoggedIn.LoginRequest.RequestedSequenceNumber.frame > frame.bin
./NsmEquities.SoupBin frame.bin wrote.bin
xxd -r -p < NsmEquities.SoupBin.NotLoggedIn.LoginRequest.RequestedSequenceNumber.wrote > want.bin
cmp want.bin wrote.bin
```
`replay.py` at the root does that for every program in this language and holds what each writes to the `.wrote` beside it, so a change here is caught without anybody running one by hand:

```
export EMOJICODEC=/path/to/emojicodec
python3 replay.py
```
The repository's `run.py`, which builds a stream of orders of your own and reads back what a market published, does **not** drive these. It carries an interpreter for a language of eight instructions, and no script carries a 56 megabyte compiler; it works on the other language's markets, whose layouts are published beside them.

