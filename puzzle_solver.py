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
import numpy as np
import io
import json
import chessllm
import csv

def convert_pgn_to_game(pgn_moves):
    pgn = io.StringIO(pgn_moves)
    game = chess.pgn.read_game(pgn)
    if len(game.errors) > 0:
        return None
    return game

def solve_puzzle(board, solution):
    solution = solution.split()
    while True:
        if len(solution) > 0:
            opponent_move, *solution = solution
            board.push_san(opponent_move)
        else:
            break

        guess_next_move = engine.get_best_move(board)

        real_next_move, *solution = solution
        if guess_next_move != real_next_move:
            try:
                board.push_san(guess_next_move)
                if board.is_checkmate():
                    # Lichess puzzles allow multiple mate-in-1 solutions
                    return True
            except:
                pass
            return False
        board.push_san(guess_next_move)
    return True

def main():

    ok = [[] for _ in range(30)]
    
    with open("pgn_puzzles.csv", 'r') as f:
        reader = csv.reader(f)
        for puzzleid, rating, pgn, solution in list(reader):
            rating = int(rating)//200
            if len(ok[rating]) >= 20: continue
            
            board = chess.Board()

            # Iterate over the moves and apply them to the board
            for move in convert_pgn_to_game(pgn).mainline_moves():
                board.push(move)

            is_right = solve_puzzle(board, solution)

            ok[rating].append(is_right)
    for i,x in enumerate(ok):
        print('rating',i*200, 'acc',np.mean(x))

    if True:
        import matplotlib.pyplot as plt
        # Remove nan values and get their indices
        ratings = [np.mean(x) for x in ok]
        non_nan_indices = [i for i, val in enumerate(ratings) if not np.isnan(val)]
        non_nan_values = [ratings[i] for i in non_nan_indices]
        
        # Create bucket ranges
        bucket_ranges = [(i*200, (i+1)*200) for i in non_nan_indices]
        bucket_labels = [f"{low}-{high}" for low, high in bucket_ranges]
        
        # Plotting
        plt.figure(figsize=(8, 4))
        plt.bar(bucket_labels, non_nan_values)
        plt.xlabel('Puzzle Rating (Elo)')
        plt.ylabel('Probability correct')
        plt.title('Ratings vs. Buckets')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("/tmp/a.png", dpi=600)


if __name__ == "__main__":
    api_key = open("OPENAI_API_KEY").read().strip()
    config = json.loads(open("config.json").read())
    engine = chessllm.ChessLLM(api_key, config, num_lookahead_tokens=30)
    main()
    
