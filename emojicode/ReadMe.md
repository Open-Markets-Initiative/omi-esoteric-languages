# Emojicode

🏁 🍇 🍉

Programs in Emojicode that read common binary exchange protocols, generated from the same compiled data models every other Omi repository is generated from.

## Why

A generator that only ever targets languages built for the job is never told when its model is incomplete. Emojicode will do arithmetic and hold a variable and take a slice of bytes, and it will not do a single thing a protocol expects: there is no struct, no cast, no pointer into a buffer, and a byte is signed. What survives that is a reading expressed in the model's own terms rather than in a language's.

These are also slow, and that is not the point of them. This is a demonstration and a test, not something to run a venue on.

One thing is worth saying about the company it keeps. This repository publishes the same protocols in more than one esoteric language, each generated independently and each holding its own frames; where two of them read the same bytes into the same fields, what they agree on is the model rather than either language. Nothing in this directory depends on another, and nothing here was checked against another's output.

## Usage

A program is compiled first, and then takes **two arguments**: the frame to read, and the file to write. Emojicode 1.0 beta 2 has no standard input — the file package is the only way in or out — so the paths are arguments rather than a pipe.

**The compiler wants its own packages in the directory it is run from**, which is the one thing that is easy to get wrong and says nothing useful when it is: it reports a package it could not find and lists the two places it looked, neither of them where the program is. Its `install.sh` puts them in `/usr/local/EmojicodePackages`, and short of installing anything, linking them into the directory you build in does as well. That directory is also where the compiled program is written, named for the source without its extension.

So the working directory is load-bearing here in a way it is not for a language that reads a pipe. Most programs also have a frame published beside them, as hexadecimal in a `.frame` file, with what the program should write for it in a `.wrote` file — hexadecimal because a frame holds any byte a protocol can carry, so it is turned back into bytes to be given to a program and the output is held to the same. All of that is one block, pasteable from the root of this repository, because a block that only compiles and a block that only runs would each be wrong about where it was standing:

```
cd emojicode/protocols/iex/iexequities/deep
ln -s /path/to/Emojicode-1.0-beta.2-Linux-x86_64/packages packages
emojicodec IexEquities.Deep.v1.08.emojic
xxd -r -p < IexEquities.Deep.v1.08.AuctionInformationMessage.frame > frame.bin
./IexEquities.Deep.v1.08 frame.bin wrote.bin
xxd -r -p < IexEquities.Deep.v1.08.AuctionInformationMessage.wrote > want.bin
cmp want.bin wrote.bin
```
A silent `cmp` is the whole of the result: what the compiled program wrote is what this repository published for that frame. Six files are left in that directory and none of them is published here — the link, the program and its `.o`, and the three `.bin` files — so they are safe to delete.

What the program writes is a line per field: the field's own name, an equals, then the bytes that field held. Which message it was is said by the order the lines come in, because only one arm of a dispatch ever runs. Padding is read and not reported.

**One compiler, and no dialect to choose between.** Emojicode 1.0 beta 2 is the only implementation, its last release was February 2020 and the last commit to the project was August 2023, so a program here is correct against that build rather than against a standard. There is nothing to ask an implementation about, because there is no second one to disagree with it.

## The language, where it bites

Two things about Emojicode shape every program here, and both were found by compiling and running rather than by reading the reference.

**A byte is signed.** Converting `0xFF` gives -1 rather than 255, and a two byte little endian field of `FF FF` reads as -257 rather than 65535. Every place a generated program turns a byte into a number it masks it first, and that masking is not decoration.

**Binary data can be built from a string or from raw memory, and from nothing else.** That matters wherever a protocol packs several fields into bytes none of them owns: such a field's value is worked out rather than cut out of the frame, and there is no way to turn a number into the byte it stands for. A string will not do it — data made from one is that string's utf8, so a byte above 127 comes out as two, and `0xC0`, `0xC1` and `0xF5` through `0xFF` are not the encoding of anything and cannot be written at any length. So a program that reads packed fields builds every byte there is, once, in a `☣️` block at the top, and afterwards cuts the byte it wants out of that like any other slice. A dozen lines in one place, and nothing the rest of the program does.

## Layout

Where these sit, written from the repository root rather than from here, because the root is where the script that checks them is:

```
emojicode/
  protocols/<organization>/<division>/<protocol>/<protocol>.emojic
  protocols/<organization>/<division>/<protocol>/<protocol>.<message>.frame
  protocols/<organization>/<division>/<protocol>/<protocol>.<message>.wrote
  exchanges/<venue>/ReadMe.md
  exchanges/<venue>/<venue>.Gateway.emojic
  exchanges/<venue>/<venue>.Market.emojic
  exchanges/<venue>/<venue>.<feed>.Feed.emojic
  exchanges/<venue>/<venue>.Market.<run>.frame
  exchanges/<venue>/<venue>.Market.<run>.wrote
  exchanges/<venue>/<venue>.<session>.emojic
  exchanges/<venue>/<venue>.<session>.<run>.frame
  exchanges/<venue>/<venue>.<session>.<run>.wrote
```
A decoder sits under `protocols` because it is the same program whoever speaks the protocol; a market and a session sit under `exchanges` because they are the venue's own — a venue is what declares which chart runs over which protocol and which security its book is for. A model stating more than one framing — a client's stream and a server's are different programs, because they read different bytes — writes one decoder for each.

**A venue is a gateway, a market and its feeds, and they join.** The gateway reads the venue's order entry and writes its own orders, under the session the venue's chart states; the market reads those and writes the venue's own events, by its trading chart; each feed reads those and writes market data, by the venue's transforms. What one writes is what the next reads, so a run can begin where a participant begins and end with what a subscriber is sent. Each venue's own readme says which of these it has, what each was held to, and the lines that run them joined; `manifest.json` at the root lists every program, run and join for anything that would rather read that than a file's name.

Each venue keeps a readme of its own beside its programs, saying what that venue declared, what was settled to build its market and its session, the runs published beside each, and the lines that compile and run them. This readme is about the language; those are about what one venue's programs do.

## Sessions

A session is a venue's handshake: it reads the other end's packets off one file, holds the state the connection is in and the data the chart says it keeps, and writes the venue's own answers to the other file. The chart it runs is the same definition the generated C++ session runs, and nothing in that chart names a packet — an event is a marking on one, so `Receive.Login.Request` means the packet marked Login Request arriving, and one chart serves every protocol marked the same way.

**It admits every login, and that is not a detail.** A chart names six kinds of event. Receive and Send are bytes; Request is a service asking the session to do something, Ask and Handler are the endpoint putting a question it cannot answer itself and hearing the answer, and Timer is a clock. A program reading one file and writing another has no service, nobody to ask and no clock, so of a handshake's transitions only the ones answering bytes can run at all. Rather than refuse the chart over it, the handler's answer is decided when the program is written and the accepting one is taken. So this is a demonstration of a handshake and never an authenticator, and every transition that cannot run is reported by the generator rather than passed over.

**What it does run, a session written in constants cannot.** A program whose answers are all known before it starts cannot fill a reply field from a field of the packet that arrived, and cannot run a guard on one. SoupBin states two accepting answers told apart by exactly that: a guard on the arriving login's requested sequence number, deciding whether the connection resumes where the client asked or where the session already was. Both are published as runs, and their answers differ in the twenty bytes that say where the stream is numbered from — one carries the sequence the client asked for, the other the value the chart opens with. A session that could not read the arriving packet would answer both the same way, and both answers would parse.

**What it keeps, it keeps as bytes.** A session's data is answered in a field, and the field is what says how wide that is and how a value sits in it, so the program holds it already laid out and answering with it is appending it. SoupBin numbers its stream in twenty ascii digits, which is more than any integer in this language carries; held as bytes there is no number in it to overflow, and the guard on it is a count of the bytes that agree rather than a conversion the language could not do exactly. A datum the chart opens with no value is written as a venue pads an unset field, which is what the chart says it is.

Each session is published with the runs it was proven on: one per way the chart states of answering a packet, each being the shortest walk that reaches the state holding that way and then the packet it waits for, laid out so that way is the one taken. A run that answers nothing is published too — half of what a session does is decline to answer, a heartbeat is answered by nothing at all, and a program that replied to one would be wrong in a way no amount of reading its login would show.

A run is held to three things before it is published. What is put to the session must be the protocol, which **the C# parser** reading those bytes is what says. The session must take every byte, or it has lost its place in the connection and everything after is read out of the middle of a packet. And what it answers must be readable by that parser as packets of the answering end, accounting for every byte — which says it framed the answer, stated the length the venue's own rule reckons, and put the right code in front of it. Then the same handshake is answered a second time in C#, mirroring the program step for step, and the two are held against each other: a parser reading a well formed Login Accepted says nothing about whether it carried the sequence the client asked for.

## Markets

A market reads a venue's own internal order stream, holds a book of price levels on each side, matches them whenever they cross, and **writes that venue's own messages back out** — an Order Rested for an order that comes to rest, a Trade for each one that happens, a Phase Announced as the day moves. It reads the internal protocol rather than the venue's order entry, which is what the generated C++ engine does and for the same reason: the internal protocol states order flow as order flow, marking which field is the price, which the quantity and which the side, and which byte of the side means buying. An order entry protocol marks its handshake and leaves its order fields to be recognised by name, and recognising a field by its name is the one thing none of these generators does.

**The book holds whatever price arrives**, and that is the clearest thing this language lends over a tape. A book here is a list, so a level is reached by its price; a book on a tape reaches one by an index, an index is one byte, so such a book is a band of prices around a declared reference and an order outside it is refused. Nothing here is banded — a run published beside a market puts an order hundreds of ticks away from the rest, and the book simply holds it.

What the day does with an arriving order is the venue's own chart and not a decision taken here: a phase that crosses crosses, a phase that collects rests without matching, and a phase that takes nothing refuses and says so in the venue's own words. The changes between them are the chart's, asked for by the byte the venue's protocol states and announced with the value it names.

Each market is published with the runs it was proven on. A run is laid out from the model and walked into a trading phase through the chart's own changes, and it is held to two things before it is published. **The C# parser** must read the orders back as the messages they were built from, and must read what the market published back as the venue's own messages, accounting for every byte — which says the market framed each one, stated the length the venue's own rule reckons, put the right type byte in front of it, and laid every field at the width and byte order the model states.

**And a second book over the same orders must agree with it on every trade** — whose order was resting, how much changed hands, and at what price. That check exists because the first one cannot make it: a wrong trade inside a well formed Trade message reads perfectly. The second book is kept deliberately unlike the market's, holding one list of resting orders where the market holds lists of levels, and reading the run's own steps rather than the bytes they were encoded to — so where the two agree, the encoding and the decoding agreed as well. A market failing any of it is published without a run, and the reason is reported instead.

The runs cover an order crossing one level and resting the remainder, **an order crossing two levels at once** — which a book taking only the best level once would get wrong while looking right — a sell aggressing into a resting bid, a cancel taking an order back out, orders collected in a phase that does not cross and then crossed when the day reaches one that does, and an order arriving where the day takes nothing at all. A trade names the resting order and the price of the level it rested at rather than the arriving order's limit, because that is where the trade happened: an order sweeping two levels trades at each of those rather than twice at its own price.

## Testing

[![Build](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/actions/workflows/build.yml/badge.svg)](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/actions/workflows/build.yml)

**What a published frame here is worth, stated exactly, because the obvious reading of it is too generous.**

Each frame is laid out from the model for these programs — not for a reader in general, which is not a thing: one language acts on a rule stating a record's size and another does not, so a frame that proves one proves nothing about the other. Captures the corpus holds for a protocol are offered too, and those are bytes an exchange really sent.

A frame is then published only where two independent readings of it agree. The C# parser must read the bytes through the model and account for every one. A second reading, walking the same model over the same bytes, must report the same fields, by the same names, in the same order, and consume the frame exactly. Where they part company the frame is not published and the reason is reported instead — so a wrong frame cannot ship, only a missing one. The `.wrote` published beside a frame is what that second reading produced.

**What this does not say is that the program was run.** Nothing in the process that writes these programs can run one: there is no Emojicode interpreter to carry, only a compiler, and it is not there. So the reading the frame was held to and the program written from the same model are two readings by one author, and their agreeing with each other would prove little. What carries the weight is the parser — other people's code, reading the same bytes by its own route — and what settles the rest is compiling the program and running it on the frames published beside it, which is done where the compiler is rather than here.

`python3 check.py` therefore makes a smaller claim about these than it makes about a language it can interpret. Every file here is held to being a program at all — a block opened is a block closed — and every frame is held to having its recorded output beside it, because a frame nothing can ever check is not evidence. It does not run them: that needs `emojicodec`, and a program needing a 56 megabyte compiler cannot be checked by a script that carries its own interpreter in two hundred lines.

**`python3 replay.py` is where they are actually run**, and it is what this repository's own build does on every push. It finds `emojicodec` on the path or takes it from the environment, compiles each program here, and runs it on every frame published beside it, holding what it writes to what the `.wrote` file records. So the claim above — that the compiled program reproduces these frames — is one this repository makes on itself rather than one a reader has to take on trust:

```
export EMOJICODEC=/path/to/emojicodec
python3 replay.py
```
Please report any parsing errors as an [issue](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/issues "Omi Esoteric Issues"). Include the bytes the program was given and what it wrote, beside what the protocol says it should have.

## Development

Updates are greatly appreciated; however, this entire repository is source generated...including the words you are reading right now. If you wish to suggest updates, the recommended process is to create an issue with changes and explanation. Time permitting, we will update the models and regenerate.

| Programs | Characters | Reading every field the model states | Frames | Recorded from the wire |
| --- | --- | --- | --- | --- |
| 16 | 511,863 | 16 of 16 | 166 | 50 |

## Open Markets Initiative

[![Omi](https://github.com/Open-Markets-Initiative/Open-Markets-Initiative/raw/main/About/Images/Logo.png)](https://github.com/Open-Markets-Initiative/Directory)  The Open Markets Initiative (Omi) is a group of technologists dedicated to enhancing the stability of electronic financial markets using modern development methods.

Other generated code can be found at [Omi Repositories](https://github.com/Open-Markets-Initiative/Directory/tree/main/Repositories "Open Markets Initiative Repositories"); for Omi rules and regulations, see [Omi Directory](https://github.com/Open-Markets-Initiative/Directory "Open Markets Initiative Directory").
## Disclaimer

Any similarities between existing people, places and/or protocols is purely incidental.

Enjoy.

