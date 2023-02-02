import os # for file paths
# import shutil # for copying files
from sys import argv # for command line arguments, getting hipped file name
import re # for regex
import difflib # for diffing files
import glob # for finding files in a directory
import itertools # for iterating through lists

def main():
    script, file_name = argv

    ############################################################
    # Regex
    ############################################################

    hip_number_re = re.compile(r"(HIP NUMBER:)(?P<hip>\d{1,4})")
    source_file_re = re.compile(r"[A-Z]{2}\d{6}\.\w{3}")
    one_dam_re = re.compile(r'1st dam\n')
    three_dam_re = re.compile(r'3rd dam\n')
    sex_sire_re = re.compile(r'\(\d{4}\s')
    race_record_re = re.compile(r'RACE RECORD')


    ############################################################
    # Lists I'll need globally
    ############################################################

    hip_list = []
    source_list = []

    ############################################################
    # Paths
    ############################################################

    p_source = os.getcwd() + r"/source"
    p_original = p_source + r"/original"
    p_update = p_source + r"/update"
    p_report =  os.getcwd() + r"/report"

    ############################################################
    # Initializing difflib
    ############################################################

    # d = difflib.Differ()


    ############################################################
    # Functions
    ############################################################


    def read_file_lines(file_name):
        '''Reads the file line by line and returns a list of lines'''
        with open(file_name, 'r') as f:
            global f1
            f1 = f.readlines()
            return f1
    f1 = read_file_lines(file_name)


    def get_meta_data():
        '''Gets the hip number and source file name from the list of lines, ignores hips with withdrawn status'''
        hip_list = []
        source_list = []
        for line in f1:
            if hip_number_re.search(line):
                if "WITHDRAWN" in line:
                    pass
                else:
                    hip_list.append(hip_number_re.search(line).group('hip'))
            elif source_file_re.search(line):
                source_list.append(source_file_re.search(line).group())
            else:
                pass
        source_list = [x.replace('.TXT', '') for x in source_list]
        return hip_list, source_list


    def seperate_lines(folder, status):
        '''Puts each horse on its own line'''

        for horse in zip(hip_list, source_list):
            print("HIP:\tHORSE:\n",horse[0], '\t', horse[1])
            if status == 'original':
                fn = horse[1] + "_short.txt"
            elif status == 'update':
                fn = "PH" + horse[0].zfill(6)
            # if fn 
            with open(f"{folder}/{fn}", "r") as f, open(f"{folder}/{fn}_string.txt", "w") as f2:
                list_sex_sire = get_line_number(f"{folder}/" + fn, sex_sire_re)
                list_sex_sire_diff = get_difference(list_sex_sire)
                # line_three_dam = get_line_number(f"{folder}/" + fn, three_dam_re)
                # line_race_record = get_line_number(f"{folder}/" + fn, race_record_re)
                # print(f"3rd Dam list: {line_three_dam}")
                # print(f"Race Record: {line_race_record}")
                # print(f"Sex Sire list: {list_sex_sire}")
                # print(f"Sex Sire diff: {list_sex_sire_diff}")
                # # print(len(list_sex_sire_diff))
                # three_dam_line = None
                # three_dam_line = 0
                # race_line = 0
                # flines = f.readlines()
                # if len(line_three_dam) != 0:
                #     three_dam_line = line_three_dam[0]
                #     f2.writelines(flines[:three_dam_line])
                # if len(line_race_record) != 0:
                #     race_line = line_race_record[0]
                #     f2.writelines(flines[race_line:])
                # f is the original file, f2 is the cleaned up file
                flines = f.readlines() # read lines of file.
                # falt = open(f"{folder}/{fn}_allt.txt", "w")
                # flines2 = f2.writelines(flines[0:three_dam_line])
                # print(flines2)
                i = 0
                n = 0
                # print("Horse number: \n", horse[0], "of", horse[0][-1])
                # i += 1
                for n, m in enumerate(list_sex_sire, start=0): # n is index of list, m is value of list.
                    if n < len(list_sex_sire_diff): # if the index is less than the length of the list
                        group = flines[m:m+list_sex_sire_diff[n]] # group the lines between the value of the first index and
                    # elif n == three_dam:
                    #     pass
                    # elif n == line_race_record:
                    #     pass
                    # elif n >= three_dam_line and n < race_line:
                    #     pass
                    else:
                        group = flines[m:m+list_sex_sire_diff[n-1]]
                    string_group = ''.join(group)
                    string_group = string_group.replace('\n', '')
                    if '2nd dam' in string_group:
                        string_group = string_group[:string_group.find("2nd dam")]
                    f2.write(string_group + '\n')
                
                # This code is looping through a list of strings (list_sex_sire) 
                # and writing the values to a file. The enumerate function is used
                # to keep track of the loop index and assign it to the variable n.
                # The start parameter is set to 0 so the loop index starts at 0.
                # Inside the loop, an if-else statement is used to determine the
                # group of strings to write to the file. The group is determined
                # by slicing the list_sex_sire_diff list with the loop index. If
                # the loop index is less than the length of the list_sex_sire_diff
                # list, the group is set to the slice of list_sex_sire_diff with
                # the loop index. Otherwise, the group is set to the slice of
                # list_sex_sire_diff with the loop index minus 1. The next two lines
                # of code join the strings in the group into one string, remove newline
                # characters, and look for the string "2nd dam". If the string is
                # found, the string is shortened to the index at which it was found.
                # Finally, the string is written to the file.


    def shorten_file(og_file, new_file, num1, num2):
        f = open(og_file, 'r')
        f2 = open(new_file, 'w')
        lines = f.readlines()
        n1 = 0
        n2 = 0
        if len(num1) != 0:
            n1 = num1[0]
        if len(num2) != 0:
            n2 = num2[0]
        for i, line in enumerate(lines, start=0):
            if i < n1:
                f2.writelines(line)
            elif i >= n1 and i < n2:
                pass
            elif i >= n2:
                f2.writelines(line)
            else:
                pass
        return f2



    def get_line_number(file_name, re_string):
        '''Gets the line number of a specific regex in a file.'''
        line_number = []
        # if status == 'original':
        #     fn = f"/p_original/{file_name}.txt"
        # elif status == 'update':
        #     fn = f"/p_update/{file_name}.txt"
        # else:
        #     fn = f"{file_name}.txt"
        f = open(file_name, 'r')
        lines = f.readlines()
        num = 0
        for line in lines:
            if re_string.search(line):
                # line_number = line_number.append(num)
                # print(num)
                line_number.append(num)
                # i += 1
            num += 1
        return line_number


    def diff_report(original, update, report):
        '''Creates a report for each hip number. Takes the lists from get_meta_data() and the path to the report directory'''
        i = 0
        # Clear out the report directory
        files = glob.glob(f'{report}/*')
        for f in files:
            os.remove(f)
        # hip_list = ["{:06d}".format(int(x)) for x in hip_list]
        for hip in zip(original, update):
            # Need to add a check to see if the file exists in the directory
            if os.path.isfile(f"source/original/{source_list[i]}") and os.path.isfile(f"source/update/PH{hip_list[i].zfill(6)}.txt"):
                f = open(f"{p_original}/{source_list[i]}", "r")
                f2 = open(f"{p_update}/PH{hip_list[i].zfill(6)}.txt", "r")
                flines = f.readlines()
                flines2 = f2.readlines()
                diff = difflib.unified_diff(flines, flines2, fromfile=f"{source_list[i]}", tofile=f"PH{hip_list[i].zfill(6)}.txt")
                diffh = difflib.HtmlDiff().make_file(flines, flines2, f"{source_list[i]}", f"PH{hip_list[i].zfill(6)}.txt")
                # print(''.join(diff))
                with open(f"{p_report}/{hip_list[i]}.html", "w") as f:
                    print("Creating report for HIP", hip_list[i])
                    f.write(''.join(diffh))
                i += 1
            else:
                print(f"File not found for HIP {hip_list[i]}")
                i += 1


    def get_difference(list):
        '''Gets the difference between each number in a list'''
        n = 0
        global list_difference
        list_difference = []
        list_difference = [list[i+1]-list[i] for i in range(len(list)-1)]
        return list_difference






##########################################################################################
# Main part of the program
##########################################################################################

    # Read the files
    print("reading files...")
    read_file_lines(f"{file_name}") #file_name is from argv
    print("Done reading files")
    
    # Get source file names and hip numbers
    print("Getting meta data...")
    # get_meta_data()
    hip_list = get_meta_data()[0]
    source_list = get_meta_data()[1]
    print("Hip list from step 1:\n", hip_list)
    print("Source list from step 1:\n", source_list)
    print("Done with meta data")
    print("Shortening files...") # Get rid of the 3rd dam to the Race Record if it exists
    for horse in zip(source_list, hip_list):
        line_third_dam = get_line_number(f"{p_original}/{horse[0]}.txt", three_dam_re)
        line_race_record = get_line_number(f"{p_original}/{horse[0]}.txt", race_record_re)
        shorten_file(f"{p_original}/{horse[0]}.txt", f"{p_original}/{horse[0]}_short.txt", line_third_dam, line_race_record)
        # shorten_file(f"{p_update}/PH{horse[1].zfill(6)}.txt", f"{p_update}/PH{horse[1].zfill(6)}_short.txt", line_third_dam, line_race_record)

    seperate_lines(p_original, 'original')
    seperate_lines(p_update, 'update')
    # test = get_line_number('FM1-586', one_dam_re)
    # print(test)
    # Find locations of the 1st and 3rd dam, Race Record, and then sex and sire 
    


    # sex_sire_list = get_line_number(p_original, sex_sire_re)
    # print("Sex Sire line list:\n", sex_sire_list)
    # print("Creating report...")
    # print("Current source list:\n", source_list)
    # print(source_list)
    # print("Current hip list:\n", hip_list)
    # diff_report(source_list, hip_list, p_report)


if __name__ == "__main__":
    main()



    # 256397809