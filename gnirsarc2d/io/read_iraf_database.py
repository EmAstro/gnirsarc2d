import numpy as np
import re

NUMBER_PATTERN = '[+\-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)|-?\d+(?:\.\d+)?'


def _clean_string(string_to_be_cleaned: str) -> int:
    return re.sub('\s+', ' ', string_to_be_cleaned).strip()


def get_features_from_identify_table(path_to_file: str, select_column: int = None) -> tuple:
    identify_table = IrafIdentify()
    identify_table.from_iraf_id_lines(_select_identify_table(path_to_file, select_column=select_column))
    return identify_table.feature_pixel, identify_table.feature_measured_wavelength, \
        identify_table.feature_archive_wavelength


def _select_identify_table(path_to_file: str, select_column: int = None) -> list:
    # read the file and store it line by line
    with open(path_to_file, 'r') as f:
        identify_table_lines = f.readlines()

    # splitting the table into the different instances that has been run to identify lines
    start_id_block, end_id_block, columns_id_block = [], [], []
    for index_line, identify_table_line in enumerate(identify_table_lines):
        if identify_table_line.startswith('# '):
            start_id_block.append(index_line)
        if identify_table_line == '\n':
            end_id_block.append(index_line)
        if identify_table_line.startswith('begin'):
            columns_id_block.append(identify_table_line.split("][")[1].split(",")[0])

    # this is to deal with the case that there are multiple newlines at the end of the file
    if len(start_id_block) < len(end_id_block):
        end_id_block = end_id_block[:len(start_id_block)]

    index_median_block = _get_central_column(columns_id_block, select_column)
    index_start_id_block, index_end_id_block = start_id_block[index_median_block], end_id_block[index_median_block]
    return identify_table_lines[index_start_id_block:index_end_id_block]


def _get_central_column(columns_id_block: list, select_column: int) -> int:
    if select_column is None:
        # getting the "central" column where the lines have been identified
        array_columns_id_block = np.sort(np.array(columns_id_block.copy(), dtype=int))
        median_columns_id_block = array_columns_id_block[1 + (len(array_columns_id_block) // 2)]
    else:
        # ToDo fix in case the value is not present in the list
        median_columns_id_block = select_column
    index_median_columns_id_block = columns_id_block.index(str(median_columns_id_block))
    return index_median_columns_id_block


class IrafIdentify:
    """

    """

    def __init__(self, date: str = None, column: str = None, units: str = None,
                 feature_pixel: list = None, feature_measured_wavelength: list = None,
                 feature_archive_wavelength: list = None, feature_fwhm: list = None):
        self.date = date
        self.column = column
        self.units = units
        if feature_pixel is None:
            self.feature_pixel = []
        else:
            self.feature_pixel = feature_pixel
        if feature_measured_wavelength is None:
            self.feature_measured_wavelength = []
        else:
            self.feature_measured_wavelength = feature_measured_wavelength
        if feature_archive_wavelength is None:
            self.feature_archive_wavelength = []
        else:
            self.feature_archive_wavelength = feature_archive_wavelength
        if feature_fwhm is None:
            self.feature_fwhm = []
        else:
            self.feature_fwhm = feature_fwhm

    def from_iraf_id_lines(self, id_table_lines: list):
        for index_line, identify_table_line in enumerate(id_table_lines):
            if '# ' in identify_table_line:
                self.date = _clean_string(identify_table_line.replace("# ", "").replace("\n", ""))
            if 'begin' in identify_table_line:
                self.column = _clean_string(identify_table_line.split("][")[1].split(",")[0])
            if 'units' in identify_table_line:
                self.units = _clean_string(identify_table_line.replace("units", ""))
            if 'features' in identify_table_line:
                features_start = index_line + 1
                features_end = features_start + int(_clean_string(identify_table_line.replace("features", "")))
        for index_line, identify_table_line in enumerate(id_table_lines[features_start:features_end]):
            table_line = re.split('\s+', identify_table_line.strip())
            self.feature_pixel.append(float(table_line[0]))
            self.feature_measured_wavelength.append(float(table_line[1]))
            self.feature_archive_wavelength.append(float(table_line[2]))
            self.feature_fwhm.append(float(table_line[3]))
