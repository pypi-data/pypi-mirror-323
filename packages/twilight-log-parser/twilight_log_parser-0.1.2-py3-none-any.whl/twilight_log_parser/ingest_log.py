import argparse
import traceback
from pathlib import Path
from typing import NoReturn

from . import log_parser


def main() -> NoReturn:
    """Main function that parses command line arguments and processes a Twilight
    Struggle game log.

    Reads the log file, parses it into game data, and outputs results to CSV. Prints
    game summary information and handles errors.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Parse a Twilight Struggle game log")
    parser.add_argument("log_file", type=str, help="Path to the game log file")
    parser.add_argument(
        "--output",
        type=str,
        default="output_files/plays.csv",
        help="Path for output CSV file (default: output_files/plays.csv)",
    )

    args = parser.parse_args()

    # Convert to Path objects
    log_path: Path = Path(args.log_file)
    output_csv: Path = Path(args.output)

    # Ensure the output directory exists
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Parse the game log
        parser = log_parser.LogParser()
        game = parser.parse_game_log(
            log_location=str(log_path),
            output_csv=str(output_csv),
            write_on_failure=True,
        )

        # Print some basic game information
        print("Game parsed successfully!")
        print(f"Players: USSR={game.ussr_player}, US={game.us_player}")
        if game.win_type in ("final_scoring", "vp_20"):
            print(f"Final Score: {game.score}")
        print(f"Winner: {game.winning_side} ({game.win_type})")
        print(f"Output written to: {output_csv}")

    except FileNotFoundError:
        print(f"Error: Could not find log file at {log_path}")
    except Exception:
        print("Error parsing game log:")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
