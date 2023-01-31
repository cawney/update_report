import os # for file paths
from sys import argv # for command line arguments, getting hipped file name
import re # for regex
import difflib # for diffing files
import glob # for finding files in a directory

def main():
    script, file_name = argv

    ############################################################
    # Regex
    ############################################################

    hip_number_re = re.compile(r"(HIP NUMBER:)(?P<hip>\d{1,4})")
    source_file_re = re.compile(r"[A-Z]{2}\d{6}\.TXT")
    one_dam_re = re.compile(r'1st dam\n')
    sex_sire_re = re.compile(r'\(\d{4}\s')


    ############################################################
    # Lists I'll need globally
    ############################################################

    hip_list = []
    source_list = []

    ############################################################
    # Paths
    ############################################################

    p_original = glob.glob(r"./source/original/")
    p_update = r"./source/update"
    p_report = r"./report"

    ############################################################
    # Initializing difflib
    ############################################################


    # d = difflib.Differ()

    def read_file_lines(file_name):
        '''Reads the file line by line and returns a list of lines'''
        with open(file_name, 'r') as f:
            global f1
            f1 = f.readlines()
            # print(f.readlines())
            return f1
    f1 = read_file_lines(file_name)


    def get_meta_data():
        '''Gets the hip number and source file name from the list of lines, ignores hips with withdrawn status'''
        # global hip_list
        # global source_list
        hip_list = []
        source_list = []

        for line in f1:
            if hip_number_re.search(line):
                # hip_number_re.search('hip')
                if "WITHDRAWN" in line:
                    pass
                else:
                    # print(hip_number_re.search(line).group('hip'))
                    hip_list.append(hip_number_re.search(line).group('hip'))
            elif source_file_re.search(line):
                # print(source_file_re.search(line).group())
                source_list.append(source_file_re.search(line).group())
            else:
                pass
        return hip_list, source_list

    hip_list = get_meta_data()[0]
    source_list = get_meta_data()[1]


    def get_line_number(folder, re_string):
        '''Cleans the files and puts each horse on its own line'''
        i = 0
        line_number = []
        for f in glob.glob(f'{folder}/*_clean.txt'):
            os.remove(f)
        for horse in zip(hip_list, source_list):
            with open(f"{folder}/{source_list[i]}", "r") as f: #, open(f"{folder}/{source_list[i].split('.')[0]}_clean.txt", "w") as f2:
                flines = f.readlines()
                num = 0
                for line in flines:
                    if re_string.search(line) != None:
                        line_number.append(num)
                        # f2.writelines(line)
                        # print(line_number)
                    num += 1
            i += 1
        # print(f"Line numbers for {re_string}")
        # print(line_number)
        return line_number

    def diff_report(original, update, report):
        '''Creates a report for each hip number. Takes the lists from get_meta_data() and the path to the report directory'''
        i = 0
        files = glob.glob(report)
        for f in files:
            os.remove(f)
        # hip_list = ["{:06d}".format(int(x)) for x in hip_list]
        for hip in zip(original, update):
            # print(f"Original: {source_list[i]}")
            # print(f"Update: {hip_list[i].zfill(6)}")
            # Need to add a check to see if the file exists in the directory
            if os.path.isfile(f"{p_original}/{source_list[i]}") and os.path.isfile(f"{p_update}/PH{hip_list[i].zfill(6)}.TXT"):
                f = open(f"{p_original}/{source_list[i]}", "r")
                f2 = open(f"{p_update}/PH{hip_list[i].zfill(6)}.TXT", "r")
                flines = f.readlines()
                flines2 = f2.readlines()
                diff = difflib.unified_diff(flines, flines2, fromfile=f"{source_list[i]}", tofile=f"PH{hip_list[i].zfill(6)}.TXT")
                diffh = difflib.HtmlDiff().make_file(flines, flines2, f"{source_list[i]}", f"PH{hip_list[i].zfill(6)}.TXT")
                # print(''.join(diff))
                with open(f"{p_report}/{hip_list[i]}.html", "w") as f:
                    print("Creating report for HIP", hip_list[i])
                    f.write(''.join(diffh))

                i += 1
            else:
                print(f"File not found for HIP {hip_list[i]}")
                i += 1


    # def get_line_number(file_name, new_file, string_to_search):
    #     '''Rewrites the files so each horse will be on its own line'''
    #     # global line_number
    #     line_number = []
    #     with open(file_name, 'r') as read_obj, open(new_file, 'w') as write_obj:
    #         flines = read_obj.readlines()
    #         num = 0
    #         for line in flines:
    #             if string_to_search.search(line) != None:
    #                 line_number.append(num)
    #                 write_obj.writelines(line)
    #             num += 1
    #     # print(line_number)
    #     return line_number


    def get_difference(list):
        n = 0
        global list_difference
        list_difference = []
        list_difference = [list[i+1]-list[i] for i in range(len(list)-1)]
        # print(list_difference)
        return list_difference


    def write_strings(line, length, old_file, new_file):
        old_f = open(old_file, 'r')
        new_f = open(new_file, 'w')
        old_l = old_f.readlines()
        lines = old_f.readlines()
        n = 0
        for i, v in enumerate(line_number, start=0):
            # print(i, v)
            # print(i, v)
            if i < len(list_difference):
                group = old_l[v:v+list_difference[i]]
            else:
                group = old_l[v:v+list_difference[i-1]]
            string_group = ''.join(group)
            string_group = string_group.replace("\n", "")
            if "2nd dam" in string_group:
                string_group = string_group[:string_group.find("2nd dam")]
            # print(string_group)
            new_f.writelines(string_group)
            new_f.write("\n")




##########################################################################################
# Main part of the program
##########################################################################################
    
    print("reading file...")
    read_file_lines(f"{file_name}")
    get_meta_data()
    print(hip_list)
    print(source_list)
    print("Done with meta data")
    ## Need to clean file first
    print("Cleaning file...")
    print("getting line numbers...")
    i = 0
    line_original_1d = get_line_number('source/original', one_dam_re)
    print(line_original_1d)
    print("Creating report...")
    # diff_report(source_list, hip_list, './report/*')
    print("Done with report")
    # print(hip_list)


if __name__ == "__main__":
    main()



    # 256397809