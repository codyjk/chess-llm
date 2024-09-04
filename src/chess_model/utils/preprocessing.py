import csv
import random

from tqdm import tqdm

from .count_lines import count_lines_fast


def process_game(game, max_context_length):
    moves = game.split()
    outcome = moves[-1]
    moves = moves[:-1]  # Remove the outcome from the move list

    for i in range(min(len(moves), max_context_length)):
        context = " ".join(moves[:i])
        next_move = moves[i]
        is_checkmate = "1" if next_move.endswith("#") else "0"

        # For the last move, we know the outcome
        if i == len(moves) - 1:
            yield context, next_move, is_checkmate, outcome
        else:
            yield context, next_move, is_checkmate, ""


def prepare_training_data(
    input_reduced_pgn_file,
    output_training_data_file,
    output_validation_data_file,
    max_context_length,
    validation_split,
):
    with open(output_training_data_file, "w", newline="") as train_outfile, open(
        output_validation_data_file, "w", newline=""
    ) as val_outfile:
        train_writer = csv.writer(train_outfile)
        val_writer = csv.writer(val_outfile)

        headers = ["context", "next_move", "is_checkmate", "outcome"]
        train_writer.writerow(headers)
        val_writer.writerow(headers)

        # Count total lines for progress bar
        total_lines = sum(1 for _ in open(input_reduced_pgn_file, "r"))

        with open(input_reduced_pgn_file, "r") as infile:
            for line in tqdm(infile, total=total_lines, desc="Processing games"):
                game = line.strip()
                for context, next_move, is_checkmate, outcome in process_game(
                    game, max_context_length
                ):
                    # Decide whether to write to train or val file
                    row = [context, next_move, is_checkmate, outcome]
                    if random.random() < validation_split:
                        val_writer.writerow(row)
                    else:
                        train_writer.writerow(row)
