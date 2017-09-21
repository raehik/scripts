#!/usr/bin/env python3
#
# Create backgrounds for applications.
#

import sys, os, argparse, logging
import subprocess
import random
import glob

class BGCycler:
    BACKGROUNDS = ["desktop", "grub"]
    VALID_IMG_EXTS = ["png", "jpg"]
    GRUB_BG_IMG = "/boot/grub/background-image.png"

    DEF_BG_DIR = os.path.join(os.environ.get("HOME"), ".assets", "backgrounds")
    DEF_WIDTH = "1366"
    DEF_HEIGHT = "768"
    DEF_BRIGHTNESS = "-81"
    DEF_CONTRAST = "-91"

    ERR_IMG_CONVERSION = 1

    def __init_logging(self):
        self.logger = logging.getLogger(os.path.basename(sys.argv[0]))
        lh = logging.StreamHandler()
        lh.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
        self.logger.addHandler(lh)

    def __parse_args(self):
        self.parser = argparse.ArgumentParser(
                description="Create backgrounds for applications.",
                epilog="I use a rule of contrast = brightness-10 for a nice image.")
        self.parser.add_argument("-v", "--verbose", help="be verbose", action="count", default=0)
        self.parser.add_argument("-q", "--quiet", help="be quiet (overrides -v)", action="count", default=0)
        self.parser.add_argument("-d", "--bg-dir",
                help="directory to read for images",
                default=BGCycler.DEF_BG_DIR)
        self.parser.add_argument("-w", "--width",
                help="width to resize images to (when required)",
                default=BGCycler.DEF_WIDTH)
        self.parser.add_argument("-u", "--height",
                help="height to resize images to (when required)",
                default=BGCycler.DEF_HEIGHT)
        self.parser.add_argument("-b", "--brightness",
                help="converted image brightness",
                default=BGCycler.DEF_BRIGHTNESS)
        self.parser.add_argument("-c", "--contrast",
                help="converted image contrast",
                default=BGCycler.DEF_CONTRAST)
        self.parser.add_argument("images", nargs="*",
                help="images to use (instead of picking randomly)")

        self.args = self.parser.parse_args()
        if self.args.verbose == 0:
            self.logger.setLevel(logging.INFO)
        elif self.args.verbose >= 1:
            self.logger.setLevel(logging.DEBUG)
        if self.args.quiet >= 1:
            self.logger.setLevel(logging.NOTSET)

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

    def convert_image(self, img, img_converted, brightness, contrast, width="0", height="0"):
        ret = 0
        if width == "0" or height == "0":
            ret = self.get_shell([
                "convert", img,
                "-brightness-contrast", "{}x{}".format(brightness, contrast),
                img_converted])
        else:
            ret = self.get_shell([
                "convert", img,
                "-brightness-contrast", "{}x{}".format(brightness, contrast),
                "-crop", "{}x{}+0+0".format(width, height),
                "-gravity", "center",
                img_converted])
        if ret != 0:
            self.exit("couldn't convert image {}".format(img), BGCycler.ERR_IMG_CONVERSION)

    def get_shuffled_images(self, d):
        """Fills an array with images in a specified directory, shuffles it,
        then prepends user-provided images."""
        imgs = []

        # get all backgrounds
        for ext in BGCycler.VALID_IMG_EXTS:
            imgs.extend(glob.glob(os.path.join(d, "original", "*." + ext)))

        random.shuffle(imgs)

        # now insert user images at the start of the list
        if self.args.images:
            # reverse since we're inserting at index 0 every time
            for img in reversed(self.args.images):
                if img == "":
                    # not giving file for this background: skip
                    continue
                else:
                    # assume images are provided relative to the given dir
                    imgs.insert(0, os.path.join(d, "original", img))
        return imgs

    def main(self):
        """Main entrypoint after program setup."""
        imgs = self.get_shuffled_images(self.args.bg_dir)

        if len(BGCycler.BACKGROUNDS) > len(imgs):
            self.exit("not enough images for the backgrounds required", BGCycler.ERR_IMG_CONVERSION)

        for bg, img in zip(BGCycler.BACKGROUNDS, imgs):
            # get outfile
            img_converted = os.path.join(
                self.args.bg_dir,
                "converted",
                os.path.basename(os.path.splitext(img)[0]) + ".png")

            # convert
            self.logger.info(os.path.basename(img))
            if bg == "grub":
                # special override: resize, copy to GRUB background image
                self.convert_image(img, img_converted, self.args.brightness,
                    self.args.contrast, self.args.width, self.args.height)
                self.get_shell(["sudo", "cp", img_converted, BGCycler.GRUB_BG_IMG])
            else:
                self.convert_image(img, img_converted, self.args.brightness,
                    self.args.contrast)

            # make symlink
            bg_out_symlink = os.path.join(self.args.bg_dir, bg)
            try:
                # remove symlink if it already exists
                os.remove(bg_out_symlink)
            except FileNotFoundError:
                pass
            os.symlink(
                os.path.join("converted", os.path.basename(img_converted)),
                bg_out_symlink)

        # now set the background
        self.get_shell([os.path.join(self.args.bg_dir, "set-desktop-background")])

if __name__ == "__main__":
    program = BGCycler()
    program.run()
