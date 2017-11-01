#!/usr/bin/env python3
#
# Render Markdown to HTML and place it inside an HTML file.
#
# Requires mistune.
#

import sys, os, argparse, logging
import subprocess
import tempfile
import base64
import mistune
from bs4 import BeautifulSoup

class RendererMarkdown:
    BROWSER = "firefox"

    def __init_logging(self):
        self.logger = logging.getLogger(os.path.basename(sys.argv[0]))
        lh = logging.StreamHandler()
        lh.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
        self.logger.addHandler(lh)

    def __parse_args(self):
        self.parser = argparse.ArgumentParser(
                description="Render Markdown to HTML and place it inside an HTML file.",
                epilog="--browser-open requires --outfile. If it isn't present, the output is saved to a temporary file. You can specify multiple CSS files to attach by using multiple --css-file arguments.")
        self.parser.add_argument("-v", "--verbose", help="be verbose", action="count", default=0)
        self.parser.add_argument("-q", "--quiet", help="be quiet (overrides -v)", action="count", default=0)
        self.parser.add_argument("-t", "--title",
                help="page title")
        self.parser.add_argument("--css-file", action="append",
                help="CSS file to attach",
                default=[os.path.join(os.environ["HOME"], ".assets", "style.css"),
                         os.path.join(os.environ["HOME"], ".assets", "style-pygments.css")])
        self.parser.add_argument("--favicon-file",
                help="referenced favicon file",
                default=os.path.join(os.environ["HOME"], ".assets", "favicon.png"))
        self.parser.add_argument("-o", "--outfile",
                help="write output to specified file instead of stdout")
        self.parser.add_argument("-b", "--browser-open", action="store_true",
                help="open output document in browser")
        self.parser.add_argument("-s", "--self-contained", action="store_true",
                help="create a single (portable) HTML file with all attached files in-document")
        self.parser.add_argument("files", nargs="*",
                help="Markdown files to concatenate & render")

        self.args = self.parser.parse_args()
        if self.args.verbose == 1:
            self.logger.setLevel(logging.INFO)
        elif self.args.verbose >= 2:
            self.logger.setLevel(logging.DEBUG)
        if self.args.quiet >= 1:
            self.logger.setLevel(logging.NOTSET)

        # if no title set, use a default
        if not self.args.title:
            # (but if present, set to filename of first file instead)
            if self.args.files:
                self.args.title = os.path.basename(self.args.files[0])
            else:
                self.args.title = "Rendered Markdown file"

    def run(self):
        """Run from CLI: parse arguments, run main."""
        self.__init_logging()
        self.__parse_args()
        self.main()

    def exit(self, msg, ret):
        """Exit with explanation."""
        self.logger.error(msg)
        sys.exit(ret)

    def get_shell(self, args):
        """Run a shell command and return the exit code."""
        return subprocess.run(args).returncode

    def render_md(self, markup):
        return mistune.markdown(markup).rstrip()

    def main(self):
        """Main entrypoint after program setup."""
        rendered_markup = ""

        # render markup
        if not self.args.files:
            rendered_markup = self.render_md(sys.stdin.read())
        else:
            for f in self.args.files:
                with open(f) as fp:
                    rendered_markup += self.render_md(fp.read())

        # create file around the markup
        part_css = ""
        part_favicon = ""
        if self.args.self_contained:
            with open(self.args.favicon_file, "rb") as f:
                favicon_base64 = base64.b64encode(f.read()).decode("ascii")
            part_favicon = "<link rel=\"icon\" href=\"data:image/x-icon;base64,{}\">".format(favicon_base64)
            for f in self.args.css_file:
                with open(f, "r") as fp:
                    part_css += "<style>{}</style>".format(fp.read())
        else:
            part_favicon = "<link rel=\"icon\" href=\"{}\">".format(self.args.favicon_file)
            part_css = "\n".join([ "<link rel=\"stylesheet\" type=\"text/css\" href=\"{}\">".format(f) for f in self.args.css_file ])

        page = """\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        {favicon}
        {css}
    </head>
    <body>
{content}
    </body>
</html>\
""".format(title=self.args.title, favicon=part_favicon, css=part_css, content=rendered_markup)

        soup = BeautifulSoup(page, "lxml")
        page = soup.prettify()

        # write to file/print to stdout/open in browser
        if self.args.browser_open:
            if not self.args.outfile:
                _, self.args.outfile = tempfile.mkstemp(prefix="markdown-render-", suffix=".html")
        if self.args.outfile:
            outfile = open(self.args.outfile, "w")
            outfile.write(page + "\n")
            outfile.close()
            self.get_shell([RendererMarkdown.BROWSER, self.args.outfile])
        else:
            print(page)
        print(self.args.css_file)

if __name__ == "__main__":
    program = RendererMarkdown()
    program.run()
