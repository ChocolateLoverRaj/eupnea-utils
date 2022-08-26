#!/usr/bin/env python3

import argparse
import subprocess as sp
from pathlib import Path


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-pulseaudio", "--no-pa",
        action="store_true",
        dest="no_pa",
        default=False,
        help="Do not install pulseaudio"
    )
    parser.add_argument(
        "--offline", "--local-files",
        action="store_true",
        dest="local_files",
        default=False,
        help="Use local files instead of downloading from github"
    )
    return parser.parse_args()


def download_files() -> None:
    print("Removing old files")
    sp.run(["sudo", "rm", "-rf", str(Path.home()) + "/.config/eupnea/audio"])
    sp.run(["mkdir", "-p", str(Path.home()) + "/.config/eupnea/audio"])
    sp.run("rm -rf /tmp/eupnea* /tmp/sof*", shell=True)
    print("Downloading files from github")
    sp.run("git clone --depth 1 https://github.com/eupnea-linux/python-scripts /tmp/eupnea-audio", shell=True)
    sp.run("git clone --depth 1 https://github.com/thesofproject/sof-bin /tmp/sof-audio", shell=True)
    print("Copying files from tmp")
    sp.run("cp /tmp/eupnea-audio/configs/* " + home_path, shell=True)


def install_pa(local_files: bool, sof_version="v2.2.x", sof_subversion="v2.2") -> None:
    print("Installing pulseaudio")
    print("Removing old files")
    sp.run("sudo rm -f /etc/systemd/system/alsa-reload.service", shell=True)
    sp.run("sudo rm -f /etc/pulse/default.pa", shell=True)
    sp.run("sudo rm -f /etc/modprobe.d/alsa-breath.conf", shell=True)
    sp.run("sudo rm -f /etc/asound.conf", shell=True)
    if not local_files:
        sp.run(["sudo", "rm", "-f", "/lib/firmware/intel/sof*"])
        print("Installing sof-audio")
        sp.run("sudo cp -r /tmp/sof-audio/" + sof_version + "/sof-" + sof_subversion + " /lib/firmware/intel/sof",
               shell=True)
        sp.run("sudo cp -r /tmp/sof-audio/"
               + sof_version + "/sof-tplg-" + sof_subversion + " /lib/firmware/intel/sof-tplg",
               shell=True)
        sp.run("sudo cp /tmp/sof-audio/" + sof_version + "/tools-" + sof_subversion + "* /usr/local/bin/", shell=True)
    print("Installing audio services")
    sp.run("sudo cp " + home_path + "alsa-reload.service /etc/systemd/system/", shell=True)
    sp.run("sudo systemctl enable alsa-reload", shell=True)
    print("Copying pa config")
    sp.run("sudo cp " + home_path + "default.pa /etc/pulse/", shell=True)
    print("Config old drivers")
    sp.run("sudo cp " + home_path + "alsa-breath.conf /etc/modprobe.d/", shell=True)
    print("Installing asound.conf")
    sp.run("sudo cp " + home_path + "asound.conf /etc/", shell=True)


if __name__ == "__main__":
    print("Processing args")
    args = process_args()
    home_path = str(Path.home()) + "/.config/eupnea/audio/"
    if not args.local_files:
        download_files()
    if not args.no_pa:
        install_pa(args.local_files)