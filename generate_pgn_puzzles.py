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
import time
import chess
import chess.pgn
import io
import csv
import os
import re
import pickle


def download_and_decompress(url):
    os.popen("wget " + url).read()
    compressed_filename = os.path.basename(url)
    time.sleep(1)
    os.popen("zstd -d " + compressed_filename).read()
    os.remove(compressed_filename)

    
def get_data():
    download_and_decompress("https://database.lichess.org/standard/lichess_db_standard_rated_2016-02.pgn.zst")
    download_and_decompress("https://database.lichess.org/lichess_db_puzzle.csv.zst")


import re

def generate_mapping(filename):
    mapping = {}

    # Regular expression pattern to match the game ID from the Site URL
    site_pattern = re.compile(r'\[Site "https://lichess.org/([a-zA-Z0-9]+)"]')

    # Open the file in binary mode to compute byte offsets
    with open(filename, 'rb') as f:
        line = f.readline()
        while line:
            match = site_pattern.search(line.decode('utf-8'))
            if match:
                current_game_id = match.group(1)
                mapping[current_game_id] = f.tell() - len(line)  # Get the starting byte offset of this line
            line = f.readline()

    return mapping

def fetch_game_moves(filename, game_id, offset):
    moves = []
    with open(filename, 'r') as f:
        f.seek(offset)
        pgn = f.read(10000).split("[Event")[0]
        

    return pgn

def convert_pgn_to_game(pgn_moves):
    pgn = io.StringIO(pgn_moves)
    game = chess.pgn.read_game(pgn)
    if len(game.errors) > 0:
        return None
    return game

def process_puzzles(csv_filename, games_filename, mapping):

    extracted_puzzles = []

    with open(csv_filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            game_url, uci_moves = row[8], row[2].split()
            game_id = game_url.split('.org/')[1]

            move_num = game_url.split('#')[-1]
            if 'Some' in move_num:
                move_num = move_num.split("(")[1][:-1]
            move_num = int(move_num)

            game_id = game_id.split("/")[0].split("#")[0]
            rating = int(row[3])

            if game_id in mapping:
                pgn = fetch_game_moves(games_filename, game_id, mapping[game_id])
                game = convert_pgn_to_game(pgn)
                if game is None: continue

                board = game.board()

                for move in list(game.mainline_moves())[:move_num]:
                    board.push(move)

                new_board = board.copy()

                try:
                    solution = []
                    for move in uci_moves:
                        m = chess.Move.from_uci(move)
                        solution.append(new_board.san(m))
                        new_board.push(m)
                except:
                    print("Board import failed")
                    continue

                extracted_puzzles.append((row[0],
                                          rating,
                                         board,
                                         solution,
                ))
                print(len(extracted_puzzles))

    with open("pgn_puzzles.csv", "w") as f:
        writer = csv.writer(f)
        for uid, rating, board, solution in extracted_puzzles:
            writer.writerow((uid, rating,
                             str(chess.pgn.Game().from_board(board)).split("\n")[-1][:-2],
                             " ".join(solution)))



if __name__ == "__main__":
    get_data()

    filename = "lichess_db_standard_rated_2016-02.pgn"
    mapping = generate_mapping(filename)

    with open('mapping.pickle', 'wb') as f:
        pickle.dump(mapping, f)

    process_puzzles("lichess_db_puzzle.csv", filename, pickle.load(open("mapping.pickle","rb")))
