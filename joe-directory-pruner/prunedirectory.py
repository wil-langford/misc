#!/usr/bin/env python

"""
"""
from __future__ import print_function

import argparse
import os
import os.path as path
import sys
import time
import shutil

DEFAULT_NUM_TO_KEEP=10
DEFAULT_MINIMUM_AGE_IN_DAYS=3
DEFAULT_DESTINATION=None

# This is a default.  Probably best not to change it.
VERBOSE=False

__author__ = 'wil-langford'


class VerbosePrinter(object):
    def __init__(self, VERBOSE):
        self._verbose = VERBOSE

    def __call__(self, *args, **kwargs):
        if self._verbose:
            print(*args, **kwargs)

class Pruner(object):
    def __init__(self, TEST_RUN, verbose_printer=None, verbose=False, dest_dir=None):
        self._test_run = TEST_RUN
        if verbose_printer is None:
            self._vp=VerbosePrinter(verbose)
        else:
            self._vp=verbose_printer
        self._dest_dir = dest_dir

    def __call__(self, full_path):
        if not self._test_run:
            if self._dest_dir is None:
                os.remove(full_path)
                self._vp("Deleted file: {}".format(full_path))
            else:
                shutil.move(full_path, self._dest_dir)
                self._vp("Moved file: {}".format(full_path))
        else:
            if self._dest_dir is None:
                self._vp("TEST RUN: Would have DELETED file: " +
                         "{}".format(full_path))
            else:
                self._vp("TEST RUN: Would have MOVED file: " +
                         "{}".format(full_path))



def main():
    parser = argparse.ArgumentParser(description="Prune a directory, keeping either the " +
                                                 "N most recent files or anything newer " +
                                                 "than DAYS old, optionally moving the " +
                                                 "pruned files to a directory instead of " +
                                                 "deleting them..")

    parser.add_argument(
        'directory',
        type=str,
        help="the directory to prune"
    )
    parser.add_argument(
        '--how-many-recent-to-keep', '-n',
        type=int,
        dest='num_to_keep',
        default=DEFAULT_NUM_TO_KEEP,
        metavar="NUM",
        help='the pruner will keep NUM of the most recent files (default:10)'
    )
    parser.add_argument(
        '--only-prune-older-than', '-d',
        type=float,
        dest='only_older_than',
        default=DEFAULT_MINIMUM_AGE_IN_DAYS,
        metavar='DAYS',
        help='only prune files that are at least DAYS old (default:3.0)'
    )
    parser.add_argument(
        '--extension', '-x',
        dest='extension',
        type=str,
        default=None,
        metavar='EXT',
        help="if specified, only files with extension EXT will " +
             "be pruned (default:all files)"
    )
    parser.add_argument(
        '--move-pruned-files-to', '-m',
        dest='destination_directory',
        type=str,
        default=DEFAULT_DESTINATION,
        metavar='DEST_DIR',
        help="if specified, the pruner will move files into the DEST_DIR directory " +
             "instead of deleting them."
    )
    parser.add_argument(
        '--verbose','-v',
        dest='verbose',
        default=False,
        action='store_true',
        help="print detailed information about program actions"
    )
    parser.add_argument(
        '--test-run','-t',
        dest='test_run',
        default=False,
        action='store_true',
        help="print detailed information about program actions, but don't actually " +
        "prune any files"
    )

    args = parser.parse_args()

    DIR = args.directory
    NUM = args.num_to_keep
    DAYS = args.only_older_than
    DEST = args.destination_directory
    TEST = args.test_run
    EXT = args.extension

    if not path.isdir(DIR):
        raise Exception("You must specify a directory to prune.")

    if NUM < 1:
        raise Exception("NUM must be at least 1.")

    if DAYS < 0:
        raise Exception("DAYS must be non-negative.")

    if DEST is not None and not path.isdir(DEST):
        raise Exception("DEST_DIR must be a directory.")

    if EXT is not None:
        if not EXT[0]=='.':
            EXT = '.' + EXT
        LEXT = len(EXT)
    else:
        LEXT = 0

    vp = VerbosePrinter(args.verbose or TEST)
    prune = Pruner(TEST, verbose_printer=vp, dest_dir=DEST)

    vp("Getting list of files in directory.")

    dir_list = os.listdir(DIR)

    vp("Found {} files total.".format(len(dir_list)))

    if EXT is not None:
        ext_filtered_list = [x for x in dir_list if x[-LEXT:]==EXT]
        vp("{} files remain after extension filtering.".format(
            len(ext_filtered_list))
        )
    else:
        ext_filtered_list = dir_list

    if len(ext_filtered_list) < NUM:
        vp("Not enough files to prune after filtering by extension.")
        sys.exit(0)

    now = time.time()
    last_mod_list = [(now-path.getmtime(x)) / (24.0*60*60)
                     for x in ext_filtered_list]

    if DAYS:
        filtered_by_age_list = [
            (mtime, ext_filtered_list[i])
            for i,mtime in enumerate(last_mod_list)
            if mtime > DAYS
        ]
        vp("{} files remain after age filtering.".format(
            len(filtered_by_age_list))
        )
    else:
        filtered_by_age_list = zip(last_mod_list, ext_filtered_list)

    if len(filtered_by_age_list) <= NUM:
        vp("Not enough files to prune after filtering by age.")
        sys.exit(0)

    prune_list = [y for x,y in sorted(filtered_by_age_list)[NUM:]]

    vp("Pruning:\n{}\nFrom directory: {}".format(prune_list, DIR))

    for file_name in prune_list:
        full_path = path.join(DIR,file_name)
        prune(full_path)


if __name__ == '__main__':
    main()