#!/usr/bin/env python

## Copyright (C) 2023, Nicholas Carlini <nicholas@carlini.com>.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import chess
from chessllm import ChessLLM
import json

def main():

    config = json.loads(open("config.json").read())
    game = chess.pgn.Game()

    while True:
        line = input()
        log.write(f"Got line: {repr(line)}\n")
        log.flush()
        if line == "uci":
            print(f"id name chess-llm-with-{config['model']}")
            print("id author Nicholas Carlini")
            print("uciok")
        elif line == "isready":
            print("readyok")
        elif line.startswith("position"):
            parts = line.split(" ", 1)
            
            moves_list = []
            if "moves" in parts[1]:
                _, moves_str = parts[1].split("moves")
                moves_list = moves_str.strip().split()

            if parts[1].startswith("startpos"):
                board = chess.Board()
            else:
                raise

            for move_uci in moves_list:
                move = chess.Move.from_uci(move_uci)
                board.push(move)
            log.write(f"now position {repr(board)}\n")
            log.flush()


        elif line.startswith("go"):
            log.write("info string Starting search\n")
            log.flush()

            move = engine.get_best_move(board)
            try:
                log.write("Have move " + move + "\n")
                uci_move = board.push_san(move).uci()
            except:
                log.write(f"info string Invalid move: {repr(move)}\n")
                log.flush()
                
                moves = list(board.legal_moves)
                move = random.choice(moves)
                uci_move = move.uci()
            
            print(f"info pv {uci_move}")
            print(f"bestmove {uci_move}")
        elif line == "quit":
            break

        
if __name__ == "__main__":
    log = open("/tmp/log.txt", "a")
    api_key = open("OPENAI_API_KEY").read().strip()
    config = json.loads(open("config.json").read())
    engine = ChessLLM(api_key, config)
    main()

