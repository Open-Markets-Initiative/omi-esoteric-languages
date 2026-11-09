# Omi Esoteric Languages

Programs in esoteric languages that read common binary exchange protocols, generated from the same compiled data models every other Omi repository is generated from.

## Languages

One directory per language, and a readme in each saying what that language's programs are, how to run them, and what they were held to before they were published:

| Language | Directory | What it lends the generator |
| --- | --- | --- |
| [Brainfuck](brainfuck/ReadMe.md "Brainfuck ReadMe") | `brainfuck` | Nothing: eight instructions and one tape of bytes |

A second language is a sibling directory rather than a second repository, because what differs between them is a directory and not a protocol. The models are the same, the venues are the same, and a program in any of them is held to the same thing before it is published: what it decodes must agree with what the C# parser decodes from the same bytes, and what it encodes must parse back.

## Why

Every other generated language lends its generator something: arithmetic, addressing, variables, functions. A language that lends nothing leaves the generator nowhere to hide a gap, so whatever cannot be expressed in it is a gap in the protocol model rather than in the language. These programs are a conformance test of the models as much as they are code.

They are also slow, by some six orders of magnitude against the generated C++. This is a demonstration and a test, not something to run a venue on.

## Running

Both scripts sit here at the root and are run from here, so a path given to either of them starts with the directory of the language it is in. `check.py` is what the build runs. `run.py` puts a stream of a venue's own orders to one of the published markets and reads back what it wrote, field by field.

What a language's programs read, what they write when they read it, and the exact commands that run them are in that language's own readme, written from this directory.

## Testing

[![Build](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/actions/workflows/build.yml/badge.svg)](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/actions/workflows/build.yml)

`python3 check.py` runs over every program in the repository. Each is held to being a program at all — a loop opened is a loop closed. Each with a `.frame` published beside it is also run on that frame and held to writing what its `.wrote` file records, which the script carries an interpreter of the stated dialect in order to do.

That second claim is a regression gate rather than a proof, and the difference is worth keeping straight. What makes a recorded output worth anything is that it was held against the C# parser reading the same bytes through the same model — field for field, in order, and accounting for every byte — before it was published. That comparison cannot be made here, because neither the models nor the parser are in this repository, so what the script says is that nothing has changed since.

Please report any parsing errors as an [issue](https://github.com/Open-Markets-Initiative/omi-esoteric-languages/issues "Omi Esoteric Issues"). Include the bytes the program was given and what it wrote, beside what the protocol says it should have.

## Development

Updates are greatly appreciated; however, this entire repository is source generated...including the words you are reading right now. If you wish to suggest updates, the recommended process is to create an issue with changes and explanation. Time permitting, we will update the models and regenerate.

## Open Markets Initiative

Other generated code can be found at [Omi Repositories](https://github.com/Open-Markets-Initiative/Directory/tree/main/Repositories "Open Markets Initiative Repositories"); for Omi rules and regulations, see [Omi Directory](https://github.com/Open-Markets-Initiative/Directory "Open Markets Initiative Directory").
## Disclaimer

Any similarities between existing people, places and/or protocols is purely incidental.

Enjoy.

