#!/usr/bin/env python

"""Word frequency list generator

This script takes a folder containing compressed xml files and returns a list of occurences
"""

import os
import sys
import argparse
from lxml import etree
import operator

_VERBOSE = 1

class ReadableDir(argparse.Action):
    """
    Check that the given argument is a readable directory
    """
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))


def count_occ_in_dir(indir, outfilename):
    """
    core function. Count the word frequency in files.

    Args:
        indir (str): Directory containing compressed xml files
        outfilename (str): Filename where word frequencies will be written
    """
    if _VERBOSE:
        print("Walk '{0}' and write into '{1}'".format(indir, outfilename))

    occ = {}

    for dirpath, _, fnames in os.walk(indir):
        for comp_xml_file in fnames:
            if comp_xml_file.lower().endswith('.xml.gz'):
                if _VERBOSE:
                    print(" Processing {0} at {1}".format(comp_xml_file, dirpath))
                tree = etree.parse(os.path.join(dirpath, comp_xml_file))
                for word in tree.xpath("/document/s/w"):
                    lower_case_word = word.text.lower()
                    occ[lower_case_word] = occ.get(lower_case_word, 0) + 1

    if occ:
        sorted_occ = sorted(occ.items(), key=operator.itemgetter(1), reverse=True)

        with open(outfilename, 'w') as outfile:
            gen_occ = (e for e in sorted_occ if e[0].isalpha())
            for e in gen_occ:
                outputline = (e[0]+' '+str(e[1])+'\n').encode('utf8')
                outfile.write(outputline)
    else:
        if _VERBOSE:
            print(" Nothing found, {0} will not be written".format(outfilename))


def main(arguments):
    """
    'main' function is a wrapper around count_occ_in_dir
    """

    global _VERBOSE

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i', '--indir', help="Input directory", action=ReadableDir,
                        default="./")
    parser.add_argument('-o', '--outfilename', help="Output filename", default="Out.log")
    parser.add_argument('-q', '--quiet', help="Quiet mode", action="store_true")
    args = parser.parse_args(arguments)

    if args.quiet:
        _VERBOSE = 0

    count_occ_in_dir(args.indir, args.outfilename)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
