#!/usr/bin/env python
import bin.settings as settings
import configparser
import os


from optparse import OptionParser

def _prepare_optparser():

    program_version = settings.__version__
    usage = ("usage: %prog")
    description = """ Use this script to generate the config """
    optparser = OptionParser(version=program_version, description=description,
                             usage=usage, add_help_option=False)

    optparser.add_option(
            "-d",
            "--directory",
            dest="directory",
            type="string",
            default=None,
            help="Directory of vcfs")

    optparser.add_option(
            "-o",
            "--output",
            dest="output",
            type="string",
            default=None,
            help="Directory of config file output")

    optparser.add_option(
            "-h",
            "--help",
            action="help",
            help="Show this help message and exit")

    return optparser

def main():
    optparser = _prepare_optparser()
    (options, dummy) = optparser.parse_args()

    Config = configparser.ConfigParser()
    config_file = open(os.path.join(options.output, "WARP_config.ini"), 'w')
    Config.add_section("Directories")
    Config.set("Directories", "vcf_directory", os.path.abspath(options.directory))

    Config.write(config_file)

if __name__ == "__main__":
    main()
