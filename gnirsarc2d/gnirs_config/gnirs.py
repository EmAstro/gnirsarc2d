
__all__ = ['GnirsConfiguration']

CONFIGURATION_NAMES = [None, '32/mmSB']

# 32/mmSB_G5533 setup, covering XYJHK with short blue camera
# 10/mmLBSX_G5532 setup, covering YJHK with the long blue camera and SXD prism


class GnirsConfiguration:
    """Class containing the properties of GNIRS given a configuration.

    Attributes:
        name (str): name of the GNIRS configuration
        mode (str): mode used
        grating (str): grating used
        camera (str): camera used
        order (dict): dictionary to translate the slit number into an order number
        rows (int): size of the detector in the spectral direction
        cols (int): size of the detector in the spatial direction

    """
    def __init__(self, name: str = None):
        r"""Instantiate the class GnirsConfiguration

        """
        self.name = name

    def __str__(self):
        return 'GNIRS configuration: {}'.format(self.name)

    @property
    def name(self):
        r"""Name of the GNIRS configuration
        """
        return self.__name

    @name.setter
    def name(self, name):
        if name not in CONFIGURATION_NAMES:
            raise ValueError('{} is not a configuration currently covered.'.format(name) +
                             'Possible values are: \n {}'.format(CONFIGURATION_NAMES))

        if name == '32/mmSB':
            self.__name = '32/mmSB'
            self.__mode = 'SXD'
            self.__grating = '32/mmSB_G5533'
            self.__camera = 'ShortBlue_G5540'
            self.__order = {"number": [3, 4, 5, 6, 7, 8],
                            "wavelength_nm_min": [1.869, 1.402, 1.122, 0.935, 0.802, 0.702],
                            "wavelength_nm_max": [2.531, 1.898, 1.518, 1.265, 1.084, 0.948],
                            "slit": [1, 2, 3, 4, 5, 6]
                            }
            self.__rows = 1024
            self.__cols = 1024
        elif name == '10/mmLBSX':
            self.__name = '10/mmLBSX'
            self.__mode = 'LXD'
            self.__grating = '10 l/mm'
            self.__camera = 'LongBlue'
            self.__order = {}
            self.__rows = None
            self.__cols = None
        else:
            self.__name = name
            self.__mode = None
            self.__grating = None
            self.__camera = None
            self.__order = {}
            self.__rows = None
            self.__cols = None

    @property
    def mode(self):
        r"""Mode of the GNIRS configuration"""
        return self.__mode

    @property
    def grating(self):
        r"""Grating of the GNIRS configuration"""
        return self.__grating

    @property
    def camera(self):
        r"""Camera of the GNIRS configuration"""
        return self.__camera

    @property
    def order(self):
        r"""Order dictionary of the GNIRS configuration"""
        return self.__order

    @property
    def rows(self):
        r"""Rows in the CCD of the GNIRS configuration"""
        return self.__rows

    @property
    def cols(self):
        r"""Cols in the CCD of the GNIRS configuration"""
        return self.__cols

