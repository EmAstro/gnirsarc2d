import argparse
import numpy as np
from IPython import embed

from gnirsarc2d.gnirs_config import gnirs
from gnirsarc2d.fitting import arc2d
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
    script_parser.add_argument("-c", "--configuration", nargs="+", type=str, default='32/mmSB',
                               help=r"GNIRS configuration")
    if options is None:
        args = script_parser.parse_args()
    else:
        args = script_parser.parse_args(options)
    return args


def main(args):
    from gnirsarc2d.io import read_iraf_database
    if type(args.database_directory) == list:
        database_directory = args.database_directory[0]
    else:
        database_directory = args.database_directory
    if type(args.root_filename) == list:
        root_filename = args.root_filename[0]
    else:
        root_filename = args.root_filename
    if type(args.configuration) == list:
        configuration = gnirs.GnirsConfiguration(name=args.configuration[0])
    else:
        configuration = gnirs.GnirsConfiguration(name=args.configuration)
    pixel, wavelength_iraf, wavelength_archive, order = [], [], [], []
    for slit in configuration.order["slit"]:
        pixel_slit, wavelength_iraf_slit, wavelength_archive_slit = read_iraf_database.get_features_from_identify_table(
            database_directory + root_filename + "_" + str(slit) + "_")
        order_number = configuration.order['number'][configuration.order['slit'].index(int(slit))]
        order_slit = [order_number] * len(pixel_slit)
        pixel.extend(pixel_slit)
        wavelength_iraf.extend(wavelength_iraf_slit)
        wavelength_archive.extend(wavelength_archive_slit)
        order.extend(order_slit)
    fit2d, mask = arc2d.full_fit(np.array(pixel), np.array(wavelength_archive), np.array(order),
                                 tot_pixel=configuration.cols)
    arc2d.plot_fit(fit2d, mask, np.array(pixel), np.array(wavelength_archive), np.array(order),
                   tot_pixel=configuration.cols)
    embed()
    return
