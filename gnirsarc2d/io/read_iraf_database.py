

def read_identify_table(path_to_file):
    # read the file and store it line by line
    with open(path_to_file, 'r') as f:
        identify_table_lines = f.readlines()
    # splitting the table into the different instances that has been run to identify lines
    identify_running_dates = [identify_running_date for identify_running_date in identify_table_lines
                              if identify_running_date.startswith('# ')]
    print(identify_running_dates)
    return identify_table_lines

