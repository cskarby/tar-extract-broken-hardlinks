#!/usr/bin/env python
"""I had some trouble with tar files from BackupPC, where hard links in the
tar file were missing in the trailing path. Files that were supposed to start
with ./path started with just .path. My solution was to write this script
and run it after extracting the tar file.

Example
root@some-server:/mnt$ tar tpvvf ../restore-root.tar | grep bunzip2
hrwxr-xr-x root/root         0 1970-01-01 00:00 ./bin/bunzip2 link to .bin/bzcat
root@some-server:/mnt# tar xpf /tmp/restore.tar
tar: ./bin/bunzip2: Cannot hard link to `.bin/bzcat': No such file or directory
tar: Exiting with failure status due to previous errors
root@some-server:/mnt# /tmp/tar_extract_broken_hardlinks.py /tmp/restore.tar
ln ./bin/bzcat ./bin/bunzip2
"""

from __future__ import print_function

import os
import sys
import tarfile


def usage(appname):
    """Shows usage on stderr"""
    print(
        "Extract all hardlinks that starts with .path instead of ./path",
        "Outputs ln statements for each hard link it creates.",
        "\nUsage: %s archive.tar" % appname,
        file=sys.stderr
    )

def main(appname, archive=None):
    """Pass path to tar archive as argument when invoking the program.
    Finding any hardlinks where target starts with .path instead of ./path
    and create those hardlinks."""
    if archive is None:
        usage(appname)
        return 1

    try:
        tar = tarfile.open(archive)
    except IOError as error:
        print("ERROR:", error, file=sys.stderr)
        return 2

    for info in tar:
        if info.islnk():  # True if it is a hardlink
            if info.linkname.startswith(".") \
            and not info.linkname.startswith("./"):
                linkname = "./%s" % info.linkname[1:]
                print("ln", linkname, info.name)
                os.link(linkname, info.name)

    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv))  # pylint: disable=W0142
