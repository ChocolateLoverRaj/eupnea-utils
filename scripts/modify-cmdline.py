#!/usr/bin/env python3

import argparse
import os.path
from os import system as bash
import subprocess as sp


# parse arguments from the cli.
def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--append', action="store_true", dest="append", default=False,
                        help="Append a flag rather than replacing the whole command line")
    parser.add_argument(dest='cmdline', type=str, nargs=1,
                        help="New, full kernel command line, example: \n"
                             + r'change-kernel-parameters "console=tty1 root=PARTUUID=7d83c214-289e-4e8b-93cc-685aea502'
                               r'f59 i915.modeset=1 rootwait rw fbcon=logo-pos:center,logo-count:1 loglevel=0 splash"')
    return parser.parse_args()


def install_packages() -> None:
    if not os.path.exists('/usr/bin/futility'):
        if os.path.exists('/usr/bin/apt'):
            os.system('sudo apt install -y vboot-kernel-utils')
        elif os.path.exists("/usr/bin/pacman"):
            bash("pacman -S vboot-kernel-utils --noconfirm")
        elif os.path.exists("/usr/bin/dnf"):
            bash("dnf install vboot-kernel-utils --assumeyes")
        else:
            print("Vboot-kernel-utils not found. Please install vboot-kernel-utils or vboot-utils using your distros" +
                  " package manager.")
            exit(1)


if __name__ == '__main__':
    args = process_args()
    new_cmdline = args.cmdline.strip()
    install_packages()

    # Get the root device
    kernel_partition = sp.run("mount | grep ' / ' | cut -d' ' -f 1", shell=True, capture_output=True).stdout.decode(
        "utf-8").strip() + "1"
    # Get the current kernel's command line
    current_cmdline = sp.run("cat /proc/cmdline", shell=True, capture_output=True).stdout.decode("utf-8").strip()
    # Write the new kernel commandline to a file
    with open('cmdline', 'w') as file:
        if args.append:
            file.write(f"{current_cmdline} {new_cmdline}")  # space needed as both args have no spaces before and after
        else:
            file.write(new_cmdline)
    # Copy old kernel partition
    bash(f"dd if={kernel_partition} of=kernel_part")
    # Sign new kernel partition
    bash("futility vbutil_kernel --repack new_kernel_part --version 1 --keyblock " +
         "/usr/share/vboot/devkeys/kernel.keyblock --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk " +
         "--oldblob kernel_part --config cmdline")
    # Flash new kernel partition
    bash(f'sudo dd if=new_kernel_part of={kernel_partition}')
