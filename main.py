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


    ############################################################
    # Lists I'll need globally
    ############################################################

    hip_list = []
    source_list = []

    ############################################################
    # Paths
    ############################################################

    p_original = r"./source/original"
    p_update = r"./source/update"
    p_report = r"./report"

    ############################################################
    # Initializing difflib
    ############################################################


    d = difflib.Differ()

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

    def diff_report(original, update, report):
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



    print("reading file...")
    read_file_lines(f"{file_name}")
    get_meta_data()
    print(hip_list)
    print(source_list)
    print("Done with meta data")
    ## Need to clean file first
    print("Creating report...")
    diff_report(source_list, hip_list, './report/*')
    print("Done with report")
    # print(hip_list)


if __name__ == "__main__":
    main()



    # 256397809