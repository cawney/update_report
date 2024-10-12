import re
import os
from sys import argv


# Add the path to the main directory to the system path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

# Arguments
script, file_source = argv



#################################################
# Regex
#################################################

re_hip_number = re.compile(r'HIP NUMBER:(\d)+')
re_hip_withdrawn = re.compile(r'HIP NUMBER:\d+ WITHDRAWN')
re_original_source = re.compile(r'(?P<salecode>[A-Za-z]{2})\d{6}\.TXT')
re_end_horse = re.compile(r'^\s{3}[^\s].+(\.|-|ing\))$')
re_dam_number = re.compile(r'\d[stndrh]{2} dam')
re_primary_dam_end = re.compile(r'^\s{6}.+-$')



#################################################
# paths 
#################################################


p_update = os.getcwd() + "/source/update/"
# p_update_temp = os.getcwd() + "/source/update/temp/"
p_original = os.getcwd() + "/source/original/"
# p_original_temp = os.getcwd() + "/source/original/temp/"
p_reports = os.getcwd() + "/report/"
P_fasig = p_reports + 'fasig/'
p_pp = p_reports + 'pp/'




#################################################
# Functions
#################################################




def get_meta_data(file):
    '''
    Gets all the hip numbers and the original source files from the pedigree file and puts them in
    a list of dictionaries
    '''
    meta_data = []
    
    with open(file, 'r') as f:
        meta_dict = {}
        hip_number = ''
        original_source = ''
        update_file = ''
        sale_code = ''
        for line in f:
            if re_hip_number.search(line):
                if re_hip_withdrawn.search(line):
                    pass
                else:
                    hip_number = re_hip_number.search(line).group()
                    hip_number = hip_number.split(':')[1]
            if re_original_source.search(line):
                original_source = re_original_source.search(line).group()
                sale_code = original_source[:2]
            update_file = sale_code + hip_number.zfill(6) + '.TXT'
            if hip_number and original_source:
                meta_dict['hip_number'] = hip_number
                meta_dict['original_source'] = original_source
                meta_dict['update_file'] = update_file
                meta_data.append(meta_dict)
                meta_dict = {}
                hip_number = ''
                original_source = ''
                update_file = ''
    return meta_data


def seperate_lines(file_path, name):
    '''
    Seperates the lines of a file into seperate horses so each horse takes up a line by itself.
    It will output a new file where each horse is on a seperate line.
    '''
    ending_lines = []
    file = file_path + name
    with open(file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if re_dam_number.search(line):
            ending_lines.append(i)
        if re_primary_dam_end.search(line):
            ending_lines.append(i)
        elif re_end_horse.search(line):
            ending_lines.append(i)
    temp_file = file_path + 'temp/' + name
    if not os.path.exists(file_path + 'temp/'):
        os.makedirs(file_path + 'temp/')
    with open(temp_file, 'w') as f:
        for i, line in enumerate(lines):
            if i < ending_lines[0]:
                f.write(line)
            else:
                if i in ending_lines:
                    f.write(line)
                else:
                    f.write(line.rstrip() + ' ')

def get_difference(list):
    '''
    Gets the difference between the 1st number and the next number in a list until the end of the list
    returns a new list with the differences
    '''
    difference = []
    for i in range(len(list) - 1):
        difference.append(list[i + 1] - list[i])
    return difference

        



#################################################
# Main
#################################################




if __name__ == '__main__':
    meta_data = get_meta_data(file_source)
    # meta_data is a list of dictionaries that have the hip number, original source file, and the update file
    # print(meta_data)

    for item in meta_data:
        # makes a new file with each horse on a seperate line
        seperate_lines(f"{p_original}", item['original_source'])
        seperate_lines(f"{p_update}", item['update_file'])

