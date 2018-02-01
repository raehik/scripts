#!/usr/bin/env python3
#
# Play a game.
#

import sys, os, argparse, logging
from raehutils import *

class PlayPy:
    ERR_MATCH = 3

    ## __init_logging, run, exit {{{
    def __init__(self):
        retroarch_cores_dir = os.environ.get("HOME") + "/.config/retroarch/cores"
        games_dir = os.environ.get("HOME") + "/media/games-local"
        self.games = {
            "tome4": {"name": "Tales of Maj'Eyal", "cmd": ["tome4"]},
            "pokemon-emerald-jp": {"name": "Pokemon Emerald (JP)", "cmd": ["retroarch","-L",retroarch_cores_dir+"/vbam_libretro.so",games_dir+"/gba/official/Pocket Monsters - Emerald (Japan).gba"]}
        }
        self.workspace_num = "9"

    def __init_logging(self):
        self.logger = logging.getLogger(os.path.basename(sys.argv[0]))
        lh = logging.StreamHandler()
        lh.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
        self.logger.addHandler(lh)

    def run(self):
        """Run from CLI: parse arguments, run main."""
        self.__init_logging()
        self.__parse_args()
        self.main()

    def exit(self, msg, ret):
        """Exit with explanation."""
        self.logger.error(msg)
        sys.exit(ret)
    ## }}}

    def __parse_args(self):
        self.parser = argparse.ArgumentParser(description="Play a game.")
        self.parser.add_argument("-v", "--verbose", help="be verbose", action="count", default=0)
        self.parser.add_argument("-q", "--quiet", help="be quiet (overrides -v)", action="count", default=0)
        self.parser.add_argument("game", help="unique string of game to play")

        self.args = self.parser.parse_args()
        if self.args.verbose == 1:
            self.logger.setLevel(logging.INFO)
        elif self.args.verbose >= 2:
            self.logger.setLevel(logging.DEBUG)
        if self.args.quiet >= 1:
            self.logger.setLevel(logging.NOTSET)

    def main(self):
        """Main entrypoint after program setup."""
        # get all possible matches
        matches = [k for k, v in self.games.items() if k.startswith(self.args.game)]

        if len(matches) > 1:
            self.exit("query matches multiple games: {}".format(", ".join(matches), PlayPy.ERR_MATCH))
        elif len(matches) < 1:
            self.exit("no matching games for query: {}".format(self.args.game), PlayPy.ERR_MATCH)

        game = self.games[matches[0]]
        self.logger.info("matched game: {}".format(game["name"]))
        self.logger.info("game cmd: {}".format(" ".join(game["cmd"])))
        self.start_game(game)

    def start_game(self, game):
        """Start a game."""
        cmd_switch_workspace = ["i3-msg","workspace",self.workspace_num]

        run_shell_interactive(cmd_switch_workspace)
        DEVNULL = open(os.devnull, "wb")
        cmd = subprocess.Popen(game["cmd"], stdout=DEVNULL, stderr=DEVNULL)
        DEVNULL.close()
        sys.exit(cmd.returncode)

if __name__ == "__main__":
    program = PlayPy()
    program.run()
