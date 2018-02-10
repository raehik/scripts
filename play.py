#!/usr/bin/env python3
#
# Play a game.
#

import raehutils
import sys, os, argparse

class PlayPy(raehutils.RaehBaseClass):
    ERR_MATCH = 1

    def __init__(self):
        retroarch_cores_dir = os.environ.get("HOME") + "/.config/retroarch/cores"
        games_dir = os.environ.get("HOME") + "/media/games-local"

        self.games = {
            "tome4": {"name": "Tales of Maj'Eyal", "cmd": ["tome4"]},
            "pokemon-emerald-jp": {"name": "Pokemon Emerald (JP)", "cmd": ["retroarch","-L",retroarch_cores_dir+"/vbam_libretro.so",games_dir+"/gba/official/Pocket Monsters - Emerald (Japan).gba"]}
        }

        self.workspace_num = "10"

    ## CLI-related {{{
    def _parse_args(self):
        self.parser = argparse.ArgumentParser(description="Play a game.")
        self.parser.add_argument("-v", "--verbose", help="be verbose", action="count", default=0)
        self.parser.add_argument("-q", "--quiet", help="be quiet (overrides -v)", action="count", default=0)
        self.parser.add_argument("game", help="unique string of game to play")

        self.args = self.parser.parse_args()
        self._parse_verbosity()
    ## }}}

    def main(self):
        """Main entrypoint after program initialisation."""
        # get all possible matches
        matches = [k for k, v in self.games.items() if k.startswith(self.args.game)]

        if len(matches) > 1:
            self.fail("query matches multiple games: {}".format(", ".join(matches), PlayPy.ERR_MATCH))
        elif len(matches) < 1:
            self.fail("no matching games for query: {}".format(self.args.game), PlayPy.ERR_MATCH)

        game = self.games[matches[0]]
        self.logger.info("matched game: {}".format(game["name"]))
        self.logger.info("game cmd: {}".format(" ".join(game["cmd"])))
        self.start_game(game)

    def start_game(self, game):
        """Start a game."""
        self.switch_workspace(self.workspace_num)
        self.run_game_cmd(game["cmd"])
        self.float_game_window()

    def switch_workspace(self, workspace_num):
        """Switch i3 workspace to the given worksapce."""
        cmd_switch_workspace = ["i3-msg", "workspace", workspace_num]
        raehutils.get_shell(cmd_switch_workspace)

    def float_game_window(self):
        """Float the game window (i3)."""
        cmd_float_window = ["i3-msg", "floating", "enable"]

        # sleep for a bit first to wait for the window to come up
        raehutils.get_shell(["sleep", "1"])
        raehutils.get_shell(cmd_float_window)

    def run_game_cmd(self, cmd):
        """Run a shell command to start a game and detach."""
        raehutils.run_shell_detached(cmd)
        # alternative: don't detach, return return code
        # maybe useful as a switch
        #return raehutils.drop_to_shell(cmd)

if __name__ == "__main__":
    program = PlayPy()
    program.run()
