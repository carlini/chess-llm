#!/usr/bin/env python3

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

import requests
import json

import os
import chess
import chess.engine
import chess.pgn
import random
import pickle
import sys

class ChessLLM:
    def __init__(self, api_key, config, **override):
        self.config = config
        for k,v in override.items():
            config[k] = v
        if os.path.exists("cache.p"):
            with open("cache.p", "rb") as f:
                self.cache = pickle.load(f)
        else:
            self.cache = {}
        print("Loading cache with", len(self.cache), "entries")
        self.api_key = api_key

    def get_query_pgn(self, board):
        pgn = str(chess.pgn.Game().from_board(board))

        if board.outcome() is None:
            pgn = pgn[:-1].strip()
        else:
            print("Game is over; no moves valid")
            return None

        if board.turn == chess.WHITE:
            if board.fullmove_number == 1:
                pgn = pgn + "\n\n1."
            else:
                pgn += ' '+str(board.fullmove_number)+"."

        with_header = f"""[White "Magnus Carlsen"]\n[Black "Garry Kasparov"]\n[WhiteElo "2900"]\n[BlackElo "2800"]\n\n"""+pgn.split("\n\n")[1]

        return with_header

    def try_moves(self, board, next_text):
        board = board.copy()
        moves = next_text.split()
        ok_moves = []
        for move in moves:
            if '.' in move:
                continue
            try:
                board.push_san(move)
                ok_moves.append(move)
            except:
                break

        return ok_moves
    
    def get_best_move(self, board, num_tokens=None, conversation=None):
        if num_tokens is None:
            num_tokens = self.config['num_lookahead_tokens']
        assert num_tokens >= 9, "A single move might take as many as 9 tokens (3 for the number + 6 for, e.g., 'N3xg5+)."

        if board.fen() in self.cache:
            out = self.cache[board.fen()]
            if conversation:
                if board.ply() > 0:
                    conversation.send_message("player", f"You played a move already in my cache (because I predicted it or someone already played it)! Returning {out}.")
                    conversation.send_message("spectator", f"Player played a move already in my cache (because I predicted it or someone already played it). Returning {out}.")
            return out

        pgn_to_query = self.get_query_pgn(board)

        if conversation:
            conversation.send_message("player", f"Querying {self.config['model']} with ... {pgn_to_query.split(']')[-1][-90:]}")
            conversation.send_message("spectator", f"Querying {self.config['model']} with ... {pgn_to_query.split(']')[-1][-90:]}")
        
        next_text = self.make_request(pgn_to_query, num_tokens)
        if next_text[:2] == "-O":
            next_text = self.make_request(pgn_to_query+" ", num_tokens)

        if conversation:
            conversation.send_message("spectator", f"Received reply of '{next_text}'")

        next_moves = self.try_moves(board, next_text)

        if len(next_moves) == 0:
            conversation.send_message("player", f"Tried to make an invalid move.")
            conversation.send_message("spectator", f"Tried to make an invalid move.")
            return None

        if conversation:
            conversation.send_message("player", f"Received reply and making move {next_moves[0]}.")
        
        new_board = board.copy()
        for move in next_moves:
            self.cache[new_board.fen()] = move
            new_board.push_san(move)

        with open("cache.p", "wb") as f:
            pickle.dump(self.cache, f)
        return next_moves[0]

    def make_request(self, content, num_tokens):
        url = "https://api.openai.com/v1/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.config['model'],
            "prompt": content,
            "temperature": self.config['temperature'],
            "max_tokens": num_tokens,
        }
    

        #sys.stderr.write(repr(data)+"\n")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response = response.json()['choices'][0]['text']
        #sys.stderr.write(response+"\n")

        return response
    

