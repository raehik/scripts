#!/usr/bin/env python3
#
# Short description of the program/script's operation/function.
#

import sys
import argparse
import json
import requests

FILENAME = sys.argv[0]

"""Argparse override to print usage to stderr on argument error."""
class ArgumentParserUsage(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s\n" % message)
        self.print_help(sys.stderr)
        sys.exit(2)

"""Print usage and exit depending on given exit code."""
def usage(exit_code):
    if exit_code == 0:
        pipe = sys.stdout
    else:
        # if argument was non-zero, print to STDERR instead
        pipe = sys.stderr

    parser.print_help(pipe)
    sys.exit(exit_code)

"""Log a message to a specific pipe (defaulting to stdout)."""
def log_message(message, pipe=sys.stdout):
    print(FILENAME + ": " + message, file=pipe)

"""If verbose, log an event."""
def log(message):
    if not args.verbose:
        return
    log_message(message)

"""Log an error. If given a 2nd argument, exit using that error code."""
def error(message, exit_code=None):
    log_message("error: " + message, sys.stderr)
    if exit_code:
        sys.exit(exit_code)



parser = ArgumentParserUsage(description="Description of the program's function (identical if you'd like).")

# add arguments
parser.add_argument("-d", "--description", help="prediction statement (what you think will/won't happen)",
                    action="store", required=True)
parser.add_argument("-e", "--deadline", help="when you'll know the prediction's outcome",
                    action="store", required=True)
parser.add_argument("-c", "--probability", help="your estimate of your prediction occurring, as a percentage",
                    action="store", required=True)
parser.add_argument("-p", "--private", help="make the prediction private",
                    action="store_true")
parser.add_argument("-t", "--dry-run", help="don't submit the request",
                    action="store_true")
parser.add_argument("-v", "--verbose", help="be verbose",
                    action="store_true")

# parse arguments
args = parser.parse_args()



host = "http://predictionbook.com"
api_call_url = "/api/predictions"
request_url = host + api_call_url

#login = "raehik"
api_key = ""

data = {
    "api_token": api_key,
    "prediction[description]": args.description,
    "prediction[deadline]": args.deadline,
    "prediction[initial_confidence]": args.probability,
    }

if args.private:
    data["prediction[private]"] = "true"

print(data)

if not args.dry_run:
    req = requests.post(request_url, data=data)
    print(req.text)
