"""
"""

import numpy as np
from matplotlib import gridspec
from matplotlib import pyplot as plt

from astropy.modeling import models, fitting
from astropy.stats import sigma_clip

from IPython import embed

FIT_FUNCTIONS = ['legendre2d', 'chebyshev2d']


def full_fit(all_pixel: np.array, all_wavelength: np.array, all_orders: np.array,
             tot_pixel: float, fit_order_spec: int = 3, fit_order_order: int = 4,
             fit_function: str = 'legendre2d', sigma: float = 3.0,
             niter: int = 100):
    r"""Obtain the 2D wavelength solution for an Echelle spectrograph.

    This is calculated from the pixel centroid and the order number of identified arc lines. The fit is a simple
    linear least-squares with rejections.

    .. note::
        The plotting assumes that the input wavelengths are in Angstrom

    .. note::
        This is a direct port of the XIDL code: `x_fit2darc.pro` which inspired also the
        `Pypeit <https://github.com/pypeit>`_ implementation of the algorithm:

    Args:
        all_pixel (np.array): centroid position in pixels of the identified lines
        all_wavelength (np.array): true wavelength of the identified lines
        all_orders (np.array): order number where the line are identified lines
        tot_pixel (int): size of the image in the spectral direction
        fit_order_spec (int): order of the fitting along the spectral (pixel) direction for each order
        fit_order_order (int): order of the fitting in the order direction
        fit_function (str): 2D function to be used
        sigma (float): sigma level for the rejection algorithm
        niter (int): number of iterations for the rejection algorithm

    Returns:
        fit2d, mask

    """
    # Normalize for pixels.
    # Fits are performed in normalized units (pixels/(tot_pixel-1)
    # This allows to perform the fitting independently from the binning
    tot_pixel_minus_1 = float(tot_pixel - 1)
    norm_pixel = all_pixel / tot_pixel_minus_1
    min_norm_pixel = 0.0
    max_norm_pixel = 1.0
    # Normalize for orders
    min_order = np.min(all_orders)
    max_order = np.max(all_orders)
    # Fit the product of wavelength and order number with a 2d legendre polynomial
    all_wavelength_order = all_wavelength * all_orders

    # Define fitting function
    if fit_function == 'legendre2d':
        model_function2d = models.Legendre2D(x_degree=fit_order_spec, y_degree=fit_order_order,
                                             x_domain=(min_norm_pixel, max_norm_pixel), y_domain=(min_order, max_order))
    elif fit_function == 'chebyshev2d':
        model_function2d = models.Chebyshev2D(x_degree=fit_order_spec, y_degree=fit_order_order,
                                              x_domain=(min_norm_pixel, max_norm_pixel), y_domain=(min_order, max_order))
    else:
        raise ValueError(r"fitting function not defined. Current possibilities are: {}".format(FIT_FUNCTIONS))
    fit_function2d = fitting.FittingWithOutlierRemoval(fitting.LinearLSQFitter(), sigma_clip, niter=niter,
                                                       sigma=sigma)

    # run the fit
    fit2d, mask = fit_function2d(model_function2d, norm_pixel, all_orders, all_wavelength_order)
    return fit2d, mask


def plot_fit(fit2d: object, mask: object, all_pixel: np.array, all_wavelength: np.array, all_orders: np.array,
             tot_pixel: float):

    # define the different orders
    orders = np.unique(all_orders)
    # define the normalizations for the pixels
    tot_pixel_minus_1 = float(tot_pixel - 1)

    # Define pixels array
    spec_vec_norm = np.arange(tot_pixel) / tot_pixel_minus_1

    resid_wl_global = []

    # set the size of the plot
    nrow = np.int(2)
    ncol = np.int(np.ceil(len(orders) / 2.))
    fig = plt.figure(figsize=(2 * ncol, 3 * nrow))

    outer = gridspec.GridSpec(nrow, ncol, wspace=0.3, hspace=0.2)

    for ii_row in range(nrow):
        for ii_col in range(ncol):
            if (ii_row * ncol + ii_col) < len(orders):
                inner = gridspec.GridSpecFromSubplotSpec(2, 1,
                                                         height_ratios=[2, 1], width_ratios=[1],
                                                         subplot_spec=outer[ii_row * ncol + ii_col],
                                                         wspace=0.1, hspace=0.0)
                ax0 = plt.Subplot(fig, inner[0])
                ax1 = plt.Subplot(fig, inner[1], sharex=ax0)
                plt.setp(ax0.get_xticklabels(), visible=False)

                ii = orders[ii_row * ncol + ii_col]

                # define the color
                rr = (ii - np.max(orders)) / (np.min(orders) - np.max(orders))
                gg = 0.0
                bb = (ii - np.min(orders)) / (np.max(orders) - np.min(orders))

                # Evaluate function
                wv_order_mod = fit2d(spec_vec_norm, ii * np.ones_like(spec_vec_norm))

                # Evaluate delta lambda
                dwl = (wv_order_mod[-1] - wv_order_mod[0]) / ii / tot_pixel_minus_1 / (spec_vec_norm[-1] - spec_vec_norm[0])

                # Estimate the residuals
                on_order = all_orders == ii
                this_order = all_orders[on_order]
                this_pix = all_pixel[on_order]
                this_wv = all_wavelength[on_order]
                this_msk = mask[on_order]

                wv_order_mod_resid = fit2d(this_pix / tot_pixel_minus_1, this_order)
                resid_wl = (wv_order_mod_resid / ii - this_wv)
                resid_wl_global = np.append(resid_wl_global, resid_wl[this_msk])

                # Plot the fit
                ax0.set_title('Order = {0:0.0f}'.format(ii))
                ax0.plot(spec_vec_norm * tot_pixel_minus_1, wv_order_mod / ii / 10000., color=(rr, gg, bb),
                         linestyle='-', linewidth=2.5)
                ax0.scatter(this_pix[~this_msk], (wv_order_mod_resid[~this_msk] / ii / 10000.) + \
                            100. * resid_wl[~this_msk] / 10000., marker='x', color='black', \
                            linewidth=2.5, s=16.)
                ax0.scatter(this_pix[this_msk], (wv_order_mod_resid[this_msk] / ii / 10000.) + \
                            100. * resid_wl[this_msk] / 10000., color=(rr, gg, bb), \
                            linewidth=2.5, s=16.)

                ax0.set_ylabel(r'Wavelength [$\mu$m]')

                # Plot the residuals
                ax1.scatter(this_pix[~this_msk], (resid_wl[~this_msk] / dwl), marker='x', color='black', \
                            linewidth=2.5, s=16.)
                ax1.scatter(this_pix[this_msk], (resid_wl[this_msk] / dwl), color=(rr, gg, bb), \
                            linewidth=2.5, s=16.)
                ax1.axhline(y=0., color=(rr, gg, bb), linestyle=':', linewidth=2.5)
                ax1.get_yaxis().set_label_coords(-0.15, 0.5)

                rms_order = np.std(resid_wl[this_msk])

                ax1.set_ylabel(r'Res. [pix]')

                ax0.text(0.1, 0.9, r'RMS={0:.3f} Pixel'.format(rms_order / np.abs(dwl)), ha="left", va="top",
                         transform=ax0.transAxes)
                ax0.text(0.1, 0.8, r'$\Delta\lambda$={0:.3f} Pixel/$\AA$'.format(np.abs(dwl)), ha="left", va="top",
                         transform=ax0.transAxes)
                ax0.get_yaxis().set_label_coords(-0.15, 0.5)

                fig.add_subplot(ax0)
                fig.add_subplot(ax1)

    rms_global = np.std(resid_wl_global)

    fig.text(0.5, 0.04, r'Row [pixel]', ha='center', size='large')
    fig.suptitle(
        r'Arc 2D FIT, RMS={:5.3f} Ang*Order#, residuals $\times$100'.format(rms_global))
    plt.show()



    """    
    pypeitFit = fitting.robust_fit(all_pix / xnspecmin1, all_wv_order, (nspec_coeff, fit_order_order), x2=all_orders,
                                   function=func2d, maxiter=100, lower=sigrej, upper=sigrej, minx=min_spec,
                                   maxx=max_spec,
                                   minx2=min_order, maxx2=max_order, use_mad=True, sticky=False)
    """

    """
    fin_rms = pypeitFit.calc_fit_rms(x2=all_orders, apply_mask=True)
    msgs.info("RMS: {0:.5f} Ang*Order#".format(fin_rms))

    if debug:
        fit2darc_global_qa(pypeitFit, nspec)
        fit2darc_orders_qa(pypeitFit, nspec)

    return pypeitFit
    """

'''

def fit2darc_global_qa(pypeitFit, nspec, outfile=None):
    """ QA on 2D fit of the wavelength solution.

    Parameters
    ----------
    pypeitFit: :class:`pypeit.gnirsarc2d.fitting.PypeItFit`:
      Fit object for the 2D arc solution
    nspec: int
    outfile: str
      parameter for QA

    """

    msgs.info("Creating QA for 2D wavelength solution")

    utils.pyplot_rcparams()

    # Extract info from pypeitFit
    xnspecmin1 = float(nspec - 1)
    all_orders = pypeitFit['x2']
    orders = np.unique(pypeitFit['x2'])
    all_wv = pypeitFit['yval'] / pypeitFit['x2']
    all_pix = pypeitFit['xval'] * xnspecmin1
    gpm = pypeitFit.bool_gpm
    nspec_coeff = pypeitFit['order'][0]
    fit_order_order = pypeitFit['order'][1]
    resid_wl_global = []

    # Define pixels array
    spec_vec_norm = np.arange(nspec) / xnspecmin1

    # Define figure properties
    plt.figure(figsize=(8, 5))

    # Variable where to store the max wavelength covered by the
    # spectrum
    mx = 0.

    # Loop over orders
    for ii in orders:

        # define the color
        rr = (ii - np.max(orders)) / (np.min(orders) - np.max(orders))
        gg = 0.0
        bb = (ii - np.min(orders)) / (np.max(orders) - np.min(orders))

        # evaluate solution
        wv_order_mod = pypeitFit.eval(spec_vec_norm, x2=np.ones_like(spec_vec_norm) * ii)
        # Plot solution
        plt.plot(wv_order_mod / ii, spec_vec_norm * xnspecmin1, color=(rr, gg, bb), linestyle='-', linewidth=2.5)

        # Evaluate residuals at each order
        on_order = all_orders == ii
        this_pix = all_pix[on_order]
        this_wv = all_wv[on_order]
        this_msk = gpm[on_order]
        this_order = all_orders[on_order]
        wv_order_mod_resid = pypeitFit.eval(this_pix / xnspecmin1, x2=this_order)
        resid_wl = (wv_order_mod_resid / ii - this_wv)
        resid_wl_global = np.append(resid_wl_global, resid_wl[this_msk])
        plt.scatter((wv_order_mod_resid[~this_msk] / ii) + \
                    100. * resid_wl[~this_msk], this_pix[~this_msk], \
                    marker='x', color='black', linewidths=2.5, s=16.)
        plt.scatter((wv_order_mod_resid[this_msk] / ii) + \
                    100. * resid_wl[this_msk], this_pix[this_msk], \
                    color=(rr, gg, bb), linewidth=2.5, s=16.)
        if np.max(wv_order_mod_resid / ii) > mx:
            mx = np.max(wv_order_mod_resid / ii)

    rms_global = np.std(resid_wl_global)

    plt.text(mx, np.max(spec_vec_norm * xnspecmin1), r'residuals $\times$100', \
             ha="right", va="top")
    plt.title(r'Arc 2D FIT, fit_order_order={:d}, nspec_coeff={:d}, RMS={:5.3f} Ang*Order#'.format(
        fit_order_order, nspec_coeff, rms_global))
    plt.xlabel(r'Wavelength [$\AA$]')
    plt.ylabel(r'Row [pixel]')

    # Finish
    if outfile is not None:
        plt.savefig(outfile, dpi=800)
        plt.close()
    else:
        plt.show()

    # restore default rcparams
    utils.pyplot_rcparams_default()


def fit2darc_orders_qa(pypeitFit, nspec, outfile=None):
    """ QA on 2D fit of the wavelength solution of an Echelle spectrograph.
    Each panel contains a single order with the global fit and the
    residuals.

    Parameters
    ----------
    pypeitFit: :class:`pypeit.gnirsarc2d.fitting.PypeItFit`:
      Fit object for the 2D arc solution
    outfile:
      parameter for QA

    Returns
    -------
    """

    msgs.info("Creating QA for 2D wavelength solution")

    utils.pyplot_rcparams()

    # Extract info from pypeitFit

    # Finish
    if outfile is not None:
        plt.savefig(outfile, dpi=800)
        plt.close()
    else:
        plt.show()

'''