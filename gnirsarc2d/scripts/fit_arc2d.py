import argparse
import numpy as np
# from IPython import embed

from gnirsarc2d.gnirs_config import gnirs
from gnirsarc2d.fitting import arc2d
from gnirsarc2d import __version__

EXAMPLES = str(r"""EXAMPLES:""" + """\n""" + """\n""" +
               r""">>> fit_arc2d --database_directory ./database/ --root_filename idwarc_comb_SCI """ + """\n""" +
               r""" """)


def parser(options=None):
    script_parser = argparse.ArgumentParser(
        description=r"""Fit of the wavelength solution for GNIRS data""" + """\n""" + """\n""" +
                    r"""The code looks for the lines identified with IRAF in the directory: `database_directory` """ +
                    r"""and performs a 2D fit of the lines taking into account the grating equation. """ +
                    r"""This means that arc line wavelengths are determined determined using both their pixel """ +
                    r"""and their order location, making the result more robust for orders in which only few """ +
                    r"""lamp lines are detected.""" + """\n""" +
                    r"""The GNIRS configuration needs to be specified. This is necessary to translate """ +
                    r"""the slit number """ +
                    r"""provided by the GNIRS pipeline into an order number.""" + """\n""" +
                    r"""The 'root_filename' argument is in the format: `idFILENAME`. The code will """ +
                    r"""look for all the files present in the database with format: `idFILENAME_SLITNUMBER_` """ +
                    r"""that is the format in which the GNIRS IRAF pipeline.""" + """\n""" +
                    """\n""" +
                    r"""This is version {:s}""".format(__version__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES)

    script_parser.add_argument("-d", "--database_directory", nargs="+", type=str, default="./database/",
                               help=r"IRAF database directory")
    script_parser.add_argument("-f", "--root_filename", nargs="+", type=str, default=None,
                               help=r"Root filename for the result of the identify task")
    script_parser.add_argument("-c", "--configuration", nargs="+", type=str, default='32/mmSB',
                               help=r"GNIRS configuration")
    script_parser.add_argument("-ff", "--fit_function", nargs="+", type=str, default='legendre2d',
                               help=r"function to be used for fitting")
    script_parser.add_argument("-os", "--fit_order_spec", nargs="+", type=int, default=3,
                               help=r"order of the fitting along the spectral (pixel) direction for each order")
    script_parser.add_argument("-oo", "--fit_order_order", nargs="+", type=int, default=4,
                               help=r"order of the fitting in the order direction")
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
    if type(args.fit_function) == list:
        fit_function = args.fit_function[0]
    else:
        fit_function = args.fit_function
    if type(args.fit_order_spec) == list:
        fit_order_spec = args.fit_order_spec[0]
    else:
        fit_order_spec = args.fit_order_spec
    if type(args.fit_order_order) == list:
        fit_order_order = args.fit_order_order[0]
    else:
        fit_order_order = args.fit_order_order

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
                                 tot_pixel=configuration.cols, fit_function=fit_function,
                                 fit_order_spec=fit_order_spec, fit_order_order=fit_order_order)
    arc2d.plot_fit(fit2d, mask, np.array(pixel), np.array(wavelength_archive), np.array(order),
                   tot_pixel=configuration.cols)

    return
