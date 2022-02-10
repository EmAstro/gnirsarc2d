import argparse

from IPython import embed

from gnirsarc2d import __version__

EXAMPLES = str(r"""EXAMPLES:""" + """\n""" + """\n""" +
               r"""TBD """ +
               r""" """)


def parser(options=None):
    script_parser = argparse.ArgumentParser(
        description=r"""TBD""" + """\n""" + """\n""" +
                    r"""This is version {:s}""".format(__version__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES)

    script_parser.add_argument("-d", "--database_directory", nargs="+", type=str, default="./database/",
                               help=r"IRAF database directory")
    script_parser.add_argument("-f", "--root_filename", nargs="+", type=str, default=None,
                               help=r"Root filename for the result of the identify task")
    if options is None:
        args = script_parser.parse_args()
    else:
        args = script_parser.parse_args(options)
    return args


def main(args):
    from gnirsarc2d.io import read_iraf_database
    database_directory = args.database_directory
    root_filename = args.root_filename
    embed()
    read_iraf_database.read_identify_table(database_directory + root_filename)
    return
