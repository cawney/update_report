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
re_end_horse = re.compile(r'(\.|-)$')
re_dam_number = re.compile(r'\d[stndrh]{2} dam')



#################################################
# paths 
#################################################


p_update = os.getcwd() + "/source/update/"
p_original = os.getcwd() + "/source/original/"
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
                print(original_source)
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


def seperate_lines(file):
    '''
    Seperates the lines of a file into seperate horses so each horse takes up a line by itself.
    It will output a new file where each horse is on a seperate line.
    '''
    ending_lines = []
    with open(file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if re_dam_number.search(line):
            ending_lines.append(i)
        if re_end_horse.search(line):
            ending_lines.append(i)
    print(ending_lines)
    difference = get_difference(ending_lines)
    print(difference)
    # remove the \n on the lines between the horses
    for i in range(len(difference)):
        lines[ending_lines[i]] = lines[ending_lines[i]].strip('\n') + ' '
    with open(file, 'w') as f:
        for i, line in enumerate(lines):
            # if i is less than the first ending line then write the line to the file
            if i < ending_lines[0]:
                f.write(line)
            
        f.writelines(lines)
    

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
    print(meta_data)

    for item in meta_data:
        print(item['hip_number'])
        print(item['original_source'])
        seperate_lines(f"{p_original}" + item['original_source'])
        print(item['update_file'])

