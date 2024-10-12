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
re_start_horse = re.compile(r'((\(\d{4} )|^([\dA-Z]))')
re_dam_number = re.compile(r'\d[stndrh]{2} dam')
re_primary_dam_end = re.compile(r'^\s{6}.+-$')

re_begin_bold = re.compile(r'\[1m')
re_end_bold = re.compile(r'\[22m')
re_extra_space = re.compile(r'\S(?P<space>\s|\.){3,}\S')


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
    
    print("starting seperating lines")
    horse_start_lines = []
    file = file_path + name
    
    with open(file, 'r') as f:
        lines = f.readlines()
    
    first_dam_line = 0

    for i, line in enumerate(lines):
        if re_dam_number.search(line):
            first_dam_line = i
            break

    for i, line in enumerate(lines):
        if i < first_dam_line:
            pass
        elif re_start_horse.search(line):
            horse_start_lines.append(i)
        elif re_dam_number.search(line):
            horse_start_lines.append(i)
    
    temp_file = file_path + 'temp/' + name
    if not os.path.exists(file_path + 'temp/'):
        os.makedirs(file_path + 'temp/')
    
    with open(temp_file, 'w') as f:
        for i, line in enumerate(range(len(horse_start_lines)-1)):
            print(horse_start_lines[i])
            if i <= horse_start_lines[0]:
                f.write(lines[i])
            else:
                if i in range(len(horse_start_lines)-1):
                    if re_dam_number.search(lines[i]):
                        f.write('\n')
                        f.write(lines[i])
                    elif i + 1 in horse_start_lines:
                        f.write(lines[i])
                    else:
                        f.write(lines[i].rstrip() + ' ')
                # else:
                #     f.write(lines[i])            


def clean_file(file_path, name):
    '''
    Cleans up the file by removing the extra spaces and making sure the horses are on seperate lines.
    '''
    file = file_path + name
    with open(file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        # search for bold characters
        if re_begin_bold.search(line):
            line = re_begin_bold.sub('**', line)
        if re_end_bold.search(line):
            line = re_end_bold.sub('**', line)
        # remove extra spaces
        if i > 28:
            if re_extra_space.search(line):
                match = re_extra_space.search(line).group()
                match = match[1:-1]
                line = line.replace(match, ' ')
        lines[i] = line
    with open(file, 'w') as f:
        for line in lines:
            f.write(line)
        



#################################################
# Main
#################################################




if __name__ == '__main__':
    meta_data = get_meta_data(file_source)
    # meta_data is a list of dictionaries that have the hip number, original source file, and the update file

    for item in meta_data:
        # makes a new file with each horse on a seperate line
        print("seperating file: " + item['hip_number'])
        print("File: " + item['original_source'])
        print("update file: " + item['update_file'])
        seperate_lines(f"{p_original}", item['original_source'])
        seperate_lines(f"{p_update}", item['update_file'])
        print(f"cleaning file: {item['original_source']}")
        clean_file(f"{p_original}temp/", item['original_source'])
        clean_file(f"{p_update}temp/", item['update_file'])

