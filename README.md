# ChessLLM

This is a project to play chess against Large Language Models (LLMs).
Currently it only supports the OpenAI text completion API,
and has only been tested on GPT-3.5-turbo-instruct.
(Because this is the only model I've seen that plays chess well.)

This code is very bare-bones. It's just enough to make things run.
Maybe in the future I'll extend it to make it better.

If you're reading this and this message is still here,
you can play a version of this bot running under my API key
[by clicking here](https://lichess.org/?user=gpt35-turbo-instruct#friend).


## What is this?

This is a chess engine that plays chess by prompting GPT-3.5-turbo-instruct.
To do this it passes the entire game state as a PGN, and the model plays
whatever move the language model responds with. So in order to respond to
a standard King's pawn opening I prompt the model with

    [White "Garry Kasparov"]
    [Black "Magnus Carlsen"]
    [Result "1/2-1/2"]
    [WhiteElo "2900"]
    [BlackElo "2800"]
    
    1. e4

And then it responds `e5` which means my engine should return the move `e5`.


## Installing

This project has minimal dependencies: just python-chess and requests to
run the UCI engine, or some additional dependencies to the lichess bot
in the lichess-bot folder.

    pip install -r requirements.txt
    pip install -r lichess-bot/requirements.txt # if you want to run the bot


## Getting Started

### Add your OpenAI key

Put your key in a file called `OPENAI_API_KEY`.

### UCI engine

If you already have a UCI-compliant chess engine downloaded and want to play
against the model you can pass `./uci_engine.py`.


### Lichess bot

The lichess-bot directory is a fork of the [lichess-bot](https://github.com/lichess-bot-devs/lichess-bot) project with a few hacks so that my bot talks a bit more and explains what it's doing.
If you want to make a lichess bot, you'll first need to create a new account,
then get an API key, and turn it into a bot. The steps to do this are
described: [in the lichess-bot README](lichess-bot/README.md).

Once you've done that put your API key as the first line of `config.yml`.


## Next steps

I highly doubt I'll do any of these things, but here are some things
I may want to do. (Or you can do!)

- Search: what happens if instead of predicting the top-1 move you predict
different moves and take the "best"? How do you choose "best"?

- Resign if lost: how can you detect if the game is lost and then just
resign if it's obviously over?

- Other models: right now this works for just OpenAI's text completion models.
It would be great to hook this up to other models if any of them
become reasonably good at chess.


## License: GPL v3

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.