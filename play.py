#!/usr/bin/env python3
#
# Short description of the program/script's operation/function.
#

import sys
import argparse
import subprocess
import os

FILENAME = sys.argv[0]

class ArgumentParserUsage(argparse.ArgumentParser):
    """Argparse override to print usage to stderr on argument error."""
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help(sys.stderr)
        sys.exit(2)

def usage(exit_code):
    """Print usage and exit depending on given exit code."""
    if exit_code == 0:
        pipe = sys.stdout
    else:
        # if argument was non-zero, print to STDERR instead
        pipe = sys.stderr

    parser.print_help(pipe)
    sys.exit(exit_code)

def log_message(message, pipe=sys.stdout):
    """Log a message to a specific pipe (defaulting to stdout)."""
    print(FILENAME + ": " + message, file=pipe)

def log(message):
    """If verbose, log an event."""
    if not args.verbose:
        return
    log_message(message)

def error(message, exit_code=None):
    """Log an error. If given a 2nd argument, exit using it as the error
    code."""
    log_message("error: " + message, sys.stderr)
    if exit_code:
        sys.exit(exit_code)

def run_command(args):
    """Run a command, returning the output and a boolean value
    indicating whether the command failed or not."""
    was_successful = True

    # execute using a shell so we can use piping & redirecting
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
    out, err = proc.communicate()

    if proc.returncode != 0:
        was_successful = False

    return out.decode("utf-8").strip(), was_successful

def start_game(command):
    cmd_switch_workspace = 'i3-msg "workspace 10"'
    cmd_start_game = "nohup %s &> /dev/null &" % command

    log("Full game command: " + cmd_start_game)

    run_command(cmd_switch_workspace)
    run_command(cmd_start_game)



parser = ArgumentParserUsage(description="Description of the program's function (identical if you'd like).")

# add arguments
parser.add_argument("-v", "--verbose", help="be verbose",
                    action="store_true")
parser.add_argument("game", help="unique string of game to play")

# parse arguments
args = parser.parse_args()



game_commands = {
    "higurashi": "wine %s/media/games/higurashi-when-they-cry/BGI.exe" % os.environ.get("HOME"),
    "tome4": "tome4",
}

game = args.game

# get possible matches
matches = [k for k, v in game_commands.items() if k.startswith(game)]

if len(matches) > 1:
    error("query '%s' not specific enough (more than 1 match)", 3)
elif len(matches) < 1:
    error("no matching games for query '%s'" % game, 4)
else:
    matched_game = matches[0]

log("Game matched: " + matched_game)
log("Game command: " + game_commands[matched_game])

start_game(game_commands[matched_game])