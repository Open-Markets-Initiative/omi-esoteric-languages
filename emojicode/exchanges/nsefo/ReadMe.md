# Nse Futures and Options Basic

The Emojicode programs generated from what Nse Futures and Options Basic declares, rather than from one protocol's model. A protocol's decoder is the same program whoever speaks it and sits under `emojicode/protocols`; what is here is this venue's own — the handshake it declares, and the book over its own internal order stream.

The same venue's programs in the repository's other language sit at the same path under that language's directory. They are not these with the emoji changed: each was generated from the models by its own backend, and the two do not come to the same program. Where they agree, what they agree on is the model.

## Declared

What the venue says it speaks, read from its own declaration and not kept as a list here:

- Ipc `Nse.NseFo.BasicMatchingEngine.Ipc.v2026`
- Engine `Nse.NseFo.FuturesAndOptions.Basic.TradingSession`
- OrderEntry `Nse.NseFo.OrderEntry.Nnf.v9.50`, session `Nse.Nnf`
- Feed `Nse.NseFo.Mtbt.Tbt.v7.1`

## The venue, end to end

A venue is declared as components that talk through one internal protocol, and each of them is a program here. Each reads one file and writes another, so they join by a file: what one is told to write is what the next is told to read.

| Program | Reads | Writes | What happens |
| --- | --- | --- | --- |
| `NseFo.Gateway.emojic` | `Nse.NseFo.OrderEntry.Nnf.v9.50` | `Nse.NseFo.BasicMatchingEngine.Ipc.v2026` | a client's requests become the venue's own orders, under the session chart |
| `NseFo.Market.emojic` | `Nse.NseFo.BasicMatchingEngine.Ipc.v2026` | `Nse.NseFo.BasicMatchingEngine.Ipc.v2026` | the venue's own orders become its own events, by the trading chart |
| `NseFo.Responder.emojic` | `Nse.NseFo.OrderEntry.Nnf.v9.50` then `Nse.NseFo.BasicMatchingEngine.Ipc.v2026` | `Nse.NseFo.OrderEntry.Nnf.v9.50` | the client's requests and the venue's own events become the client's answers, by the transforms |
| `NseFo.Mtbt.Feed.emojic` | `Nse.NseFo.BasicMatchingEngine.Ipc.v2026` | `Nse.NseFo.Mtbt.Tbt.v7.1` | the venue's own events become market data, by the transforms |

From the root of the repository, one published run through all of it. The compiler wants its packages in the directory it is run from, and a published frame is hexadecimal, so it is turned back into bytes first and what comes out of the last program is held to the run published beside it:

```
cd emojicode/exchanges/nsefo
ln -s /path/to/Emojicode-1.0-beta.2-Linux-x86_64/packages packages
emojicodec NseFo.Gateway.emojic
emojicodec NseFo.Market.emojic
emojicodec NseFo.Mtbt.Feed.emojic
xxd -r -p < runs/gateway/crossing.frame > requests.bin
./NseFo.Gateway requests.bin orders.bin
./NseFo.Market orders.bin events.bin
./NseFo.Mtbt.Feed events.bin packets.bin
xxd -r -p < runs/mtbt.feed/entered-crossing.wrote > want.bin
cmp want.bin packets.bin
```
Every such join is stated in `manifest.json` at the root, as two files that hold the same bytes - what one program should write and what the next is given - and `python3 check.py` holds each pair to it.

## Gateway

`NseFo.Gateway.emojic` reads a client's packets in `Nse.NseFo.OrderEntry.Nnf.v9.50` and writes each request the venue's transforms name as one of the venue's own messages, which is what the market reads. It follows the session the venue's chart states, so a request is admitted only where that chart receives one.

What was settled when the program was written rather than asked while it ran:

- timestamp is when the sequencer took the message, and a program reading one file and writing another has no clock and is given no time by the request, so it is written as 09:15 on 2 January 2026, 5:30 ahead of UTC, the venue's open on a day chosen for its published runs rather than read from anything
- the session is Nse Nnf: a connection opens in NotSignedOn, and a request is admitted only while it rests in SignedOn, which is where the chart receives the other end's own data. A login moves the connection as the chart says an accepted one does; whether to accept it is the session program's to say and was settled there

What the venue declares of its order entry that this program does not run, and why:

- the 4 responses it declares: each answers a client from an event of the engine and what the gateway remembers of the order, and a program reading one stream and writing one has the client's requests to read and the engine to write to, and neither the engine's events nor the client the other way round

Each run is a client's packets and what the gateway should write for them. A run nobody logged in for is published with nothing to write, because declining is half of what a gate does:

| Run | Requests | Bytes written |
| --- | ---: | ---: |
| `NseFo.Gateway.crossing` | 3 | 108 |
| `NseFo.Gateway.unadmitted` | 3 | 0 |
| `NseFo.Gateway.sweeping` | 3 | 108 |
| `NseFo.Gateway.selling` | 2 | 72 |
| `NseFo.Gateway.cancelling` | 3 | 91 |
| `NseFo.Gateway.day` | 8 | 271 |

## Market

`NseFo.Market.emojic` reads the internal order stream Nse Futures and Options Basic declares — `Nse.NseFo.BasicMatchingEngine.Ipc.v2026` — holds a book of price levels on each side, matches them whenever they cross, and writes the venue's own messages back out. It runs the `Nse Futures and Options Basic` day, and stamps every message it publishes with the security that day is declared for.

**Its book holds whatever price arrives.** A level is reached by its price rather than by an index into a tape, so nothing here is banded around a declared reference and no order is refused for being far from one. What this market does refuse, it refuses because the day it runs says to.

What was settled when the program was written rather than asked while it ran:

- the day is Nse Futures and Options Basic, in the phases Continuous then Closed; it starts in Continuous
- an order is a quantity at a price: the book holds whatever price arrives, because a list reaches a level by value and not by an index that has to fit in a byte

Each run below is published as a `.frame` of the orders put to it and a `.wrote` of what the market published. Each was held to the C# parser on both halves, and to a second book in C# that must agree on every trade, before it was published:

| Run | Orders | Trades | Refused |
| --- | ---: | ---: | ---: |
| `NseFo.Market.crossing` | 3 | 1 | 0 |
| `NseFo.Market.sweeping` | 3 | 2 | 0 |
| `NseFo.Market.selling` | 2 | 1 | 0 |
| `NseFo.Market.cancelling` | 2 | 0 | 0 |
| `NseFo.Market.day` | 7 | 4 | 0 |
| `NseFo.Market.entered-crossing` | 3 | 1 | 0 |
| `NseFo.Market.entered-sweeping` | 3 | 2 | 0 |
| `NseFo.Market.entered-selling` | 2 | 1 | 0 |
| `NseFo.Market.entered-cancelling` | 2 | 0 | 0 |
| `NseFo.Market.entered-day` | 7 | 4 | 0 |

## Responder

`NseFo.Responder.emojic` writes what a client is answered with, in `Nse.NseFo.OrderEntry.Nnf.v9.50`: each event of the engine's that the venue's transforms declare an answer for, as that answer. An answer is written from two things at once - the engine's event, and what the client entered of the order it is about - and a program reads one file, so its input is the two joined: the client's packets exactly as the gateway read them, a packet stating no length, and then the venue's own events exactly as the market wrote them. A request is answered as it is read only where the venue answers one as it arrives - a reject for an order the gateway turns away, or a confirmation where the venue confirms an order as the gateway takes it. Otherwise the requests are read to remember where each order was entered, numbered as the gateway numbers them, which is how an event naming an order by its number finds what the client called it and whatever else of what it entered the answer carries back.

What was settled when the program was written rather than asked while it ran:

- serverpacket.servermessage.messageheader.alphachar is in every packet and nothing says what it holds, so it is written holding nothing, which for text is its padding all the way
- serverpacket.servermessage.messageheader.traderid names the user, and is written as the client the venue declares, 10001
- serverpacket.servermessage.messageheader.errorcode is in every packet and nothing says what it holds, so it is written as the value its model states for a field left unset, No Error
- serverpacket.servermessage.servermessagepayload.orderconfirmationmessage.orderentrybody.traderid names the user, and is written as the client the venue declares, 10001
- serverpacket.servermessage.servermessagepayload.ordercancellationconfirmationmessage.cancellationconfirmationbody.orderentrybody.traderid names the user, and is written as the client the venue declares, 10001
- it reads the client's requests first and the engine's events after them, in one file: the requests end at a packet stating no length, and everything after that is the engine's
- an answer is written as what it answers is read: a reject, or the answer to an order as the gateway takes it, as its request is, and so ahead of every answer to an event, and an answer to an event after the last request; answers to one event are written in the order the venue's transforms declare them

Each run is the gateway's run of the same name and what the market should write for it, joined, and the answers this should write. Each was held to the C# parser reading the answers back through the order entry's own model before it was published:

| Run | Bytes of requests | Bytes of events | Answers | Bytes written |
| --- | ---: | ---: | ---: | ---: |
| `crossing` | 3,770 | 159 | 5 | 1,540 |
| `sweeping` | 3,770 | 210 | 7 | 2,132 |
| `selling` | 3,454 | 87 | 4 | 1,224 |
| `cancelling` | 3,770 | 108 | 3 | 948 |
| `day` | 5,350 | 420 | 16 | 4,896 |

From the root of the repository, the same join made by hand - the client's requests, the packet stating no length, and what the gateway and the market make of those requests - and what the responder writes for it held to the run published beside it:

```
cd emojicode/exchanges/nsefo
ln -s /path/to/Emojicode-1.0-beta.2-Linux-x86_64/packages packages
emojicodec NseFo.Gateway.emojic
emojicodec NseFo.Market.emojic
emojicodec NseFo.Responder.emojic
xxd -r -p < runs/gateway/crossing.frame > requests.bin
./NseFo.Gateway requests.bin orders.bin
./NseFo.Market orders.bin events.bin
( cat requests.bin; printf '\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'; cat events.bin ) > joined.bin
./NseFo.Responder joined.bin answers.bin
xxd -r -p < runs/responder/crossing.wrote > want.bin
cmp want.bin answers.bin
```
## Feeds

`NseFo.Mtbt.Feed.emojic` reads the venue's own events and writes each one the venue's transforms name as a packet of `Nse.NseFo.Mtbt.Tbt.v7.1`, one message to a packet. It writes 3 of the 3 events the venue declares for this feed.

What was settled when the program was written rather than asked while it ran:

- packet.message.payload.newordermessage.timestamp counts from Dos in Asia/Kolkata, which has kept one offset from 1970 to the end of 2099, so a time is moved there by adding -315513000000000000 nanoseconds
- packet.message.payload.ordercancellationmessage.timestamp counts from Dos in Asia/Kolkata, which has kept one offset from 1970 to the end of 2099, so a time is moved there by adding -315513000000000000 nanoseconds
- packet.message.payload.trademessage.timestamp counts from Dos in Asia/Kolkata, which has kept one offset from 1970 to the end of 2099, so a time is moved there by adding -315513000000000000 nanoseconds

Each run is what the market should write for the run of the same name, and the packets this should write for it:

| Run | Packets |
| --- | ---: |
| `NseFo.Mtbt.Feed.crossing` | 4 |
| `NseFo.Mtbt.Feed.sweeping` | 5 |
| `NseFo.Mtbt.Feed.selling` | 2 |
| `NseFo.Mtbt.Feed.cancelling` | 3 |
| `NseFo.Mtbt.Feed.day` | 10 |
| `NseFo.Mtbt.Feed.entered-crossing` | 4 |
| `NseFo.Mtbt.Feed.entered-sweeping` | 5 |
| `NseFo.Mtbt.Feed.entered-selling` | 2 |
| `NseFo.Mtbt.Feed.entered-cancelling` | 3 |
| `NseFo.Mtbt.Feed.entered-day` | 10 |

## Session

`NseFo.Nnf.emojic` runs the chart `Nse.Nnf` over `Nse.NseFo.OrderEntry.Nnf.v9.50`: it reads the other end's packets out of the file named by its first argument, holds the state the connection is in and the data the chart says it keeps, and writes the venue's own answers to the file named by its second.

**It reads the packet that arrived.** A reply field can be filled from a field of the packet that asked for it, and a guard can be run on one — so where the chart tells two answers apart by what the other end asked for, the program runs that guard rather than having it settled before it started. The runs below are named for the way each one takes, so a chart that states more than one way of answering a packet publishes a run for each.

What was settled when the program was written rather than asked while it ran:

- Authenticating: Handler.Login.Accepted is taken as the chart writes it, so the program never asks

Transitions of the chart no program reading one file and writing another can run, because a Request, an Ask, a Handler or a Timer has nowhere to put a question, nobody to ask it of and no clock to read:

- Ask.Login is put to a handler, and a program reading one file and writing another has nobody to put it to
- Receive.Payload.Application is the other end's own data rather than one packet this protocol names, so nothing in the frame tells it apart from the session's own packets
- Handler.Logout is put to a handler, and a program reading one file and writing another has nobody to put it to
- Request.Message answers something that is not bytes, so no program reading one file and writing another can reach it
- Request.Logout answers something that is not bytes, so no program reading one file and writing another can reach it

One run per way the chart states of answering a packet, named for the state it rests in, the packet that arrives and the way taken. A run the session answers nothing to is published too, with an empty `.wrote`, because half of what a session does is decline to answer:

| Run | Packets answered |
| --- | ---: |
| `NseFo.Nnf.NotSignedOn.LoginRequest` | 1 |
| `NseFo.Nnf.SignedOn.SessionLogout` | 1 |
| `NseFo.Nnf.SignedOn.SessionHeartbeat` | 1 |

## Files

| Program | What it is | Runs published |
| --- | --- | ---: |
| `NseFo.Nnf.emojic` | the venue's handshake | 3 |
| `NseFo.Gateway.emojic` | the venue's order entry, under its session chart | 6 |
| `NseFo.Market.emojic` | the venue's book and the matching over it | 10 |
| `NseFo.Responder.emojic` | the venue's answers to a client | 5 |
| `NseFo.Mtbt.Feed.emojic` | the venue's Mtbt feed | 10 |

Under `runs/`, in a folder named for each program, is a `.frame` per run, holding the bytes it was given as hexadecimal, and a `.wrote` holding what it wrote for them. Those are what `replay.py` compiles each program against. They are written as hexadecimal because a frame holds any byte a protocol can carry and so does a program's output, so neither is text.

## What the programs are made of

| Program | Emoji | Different | Most used |
| --- | ---: | ---: | --- |
| `NseFo.Nnf.emojic` | 1,003 | 42 | ❗️ 195 ➕ 187 🔪 137 ➡️ 104 🖍 98 |
| `NseFo.Gateway.emojic` | 1,586 | 44 | ➡️ 389 🖍 383 ❗️ 154 ➕ 149 ⭕ 71 |
| `NseFo.Market.emojic` | 3,676 | 46 | ➡️ 965 🖍 955 ❗️ 350 ➕ 311 ⭕ 235 |
| `NseFo.Responder.emojic` | 8,416 | 46 | ➕ 1,639 ❗️ 1,632 ➡️ 1,197 🖍 1,189 🔪 1,131 |
| `NseFo.Mtbt.Feed.emojic` | 3,698 | 43 | ➡️ 995 🖍 989 ➕ 373 ❗️ 357 ⭕ 215 |

## Running

A program here is **compiled first, and then takes two paths**: the file to read and the file to write. Emojicode 1.0 beta 2 has no standard input — the file package is the only way in or out — so nothing here is piped.

The compiler looks for its own packages in the directory it is run from, so that directory is where one of these is built and run — which is this one, and the lines below change to it from the root of the repository rather than leaving where you are standing to be guessed at. It is the directory it is run from and not the one the program is in, so the packages have to be reachable from here too; `emojicode/ReadMe.md` says how, and the line that does it is the one line below that is not about this venue.

Compile one of these, and run it on a frame published beside it. A published frame is hexadecimal, so it is turned back into bytes first, and so is the output it is held to:

```
cd emojicode/exchanges/nsefo
ln -s /path/to/Emojicode-1.0-beta.2-Linux-x86_64/packages packages
emojicodec NseFo.Nnf.emojic
xxd -r -p < runs/nnf/NotSignedOn.LoginRequest.frame > frame.bin
./NseFo.Nnf frame.bin wrote.bin
xxd -r -p < runs/nnf/NotSignedOn.LoginRequest.wrote > want.bin
cmp want.bin wrote.bin
```
`replay.py` at the root does that for every program in this language and holds what each writes to the `.wrote` beside it, so a change here is caught without anybody running one by hand:

```
export EMOJICODEC=/path/to/emojicodec
python3 replay.py
```
The repository's `run.py`, which builds a stream of orders of your own and reads back what a market published, does **not** drive these. It carries an interpreter for a language of eight instructions, and no script carries a 56 megabyte compiler; it works on the other language's markets, whose layouts are published beside them.

