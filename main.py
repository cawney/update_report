import os # for file paths
from sys import argv # for command line arguments, getting hipped file name
import re # for regex
import difflib # for diffing files
import glob # for finding files in a directory
import timeit # for timing the script
from bs4 import BeautifulSoup # for parsing html

start_time = timeit.default_timer() # I was curious how long the script takes to run

### What this script does:
# 1. Gets the hip number and source file name from the list of lines, ignores hips with withdrawn status
# 2. Puts the source files in the order they appear in hip order
# 3. Seperates the files into 3 groups, the 3x, middle and RR/PR
# 4. Cleans up the middle group (removes 3rd-4th dam if present and puts each horse on a line by itself)
# 5. Puts them back together in the correct order
# 6. Compares the files, makes an HTML files with the differences (for PP)
# 7. Make an XML file for Fasig
   # a. read the update lines from compare files generated in step 6


def main():
    script, file_name = argv

    ############################################################
    # Regex
    ############################################################

    hip_number_re = re.compile(r"(HIP NUMBER:)(?P<hip>\d{1,4})") # Gets the hip number
    source_file_re = re.compile(r"[A-Z]{2}\d{6}\.\w{3}") # Gets the source file name
    one_dam_re = re.compile(r'1st dam\n') # Gets the first dam
    three_dam_re = re.compile(r'3rd dam\n') # Gets the third dam
    sex_sire_re = re.compile(r'\(\d{4}\s') # Gets the sex and sire (technically gets the YOB, but it's the same thing)
    race_record_re = re.compile(r'RACE RECORD') # Gets the race record
    re_yob = re.compile(r"(?!\()\d{4}\s") # Gets the YOB
    re_sex = re.compile(r"(?!by\s)([fcgr])")
    re_money = re.compile(r"(Total:\s|\d,\s)\$(?P<money>\d+(?:\,\d+(?:\,\d+)?)?)")

    ############################################################
    # Paths
    ############################################################

    p_source = os.getcwd() + r"/source"
    p_original = p_source + r"/original"
    p_update = p_source + r"/update"
    p_report =  os.getcwd() + r"/report"

    ############################################################
    # Functions
    ############################################################


    def read_file_lines(file_name):
        '''Reads the file line by line and returns a list of lines'''
        with open(file_name, 'r') as f:
            global f1
            f1 = f.readlines()
            return f1
    f1 = read_file_lines(file_name) # This is the file that is passed from the command line in argv


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


    def seperate_lines(file_name, new_file, list_name, need_first_dam):
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
        if need_first_dam == True:
            list_name.insert(0, 0)
        f = open(file_name, 'r')
        lines = f.readlines()
        list_diff = get_difference(list_name)
        f2 = open(new_file, 'w')
        # print("list_name:\n", list_name)
        for n, m in enumerate(list_name, start=0):
            if n < len(list_diff):
                # horse = lines[m:m+list_diff[n-1]]
                horse = lines[m:m+list_diff[n]]
            if n == len(list_diff):
                horse = lines[m:]
            else:
                pass
            horse_string = ''.join(horse)
            horse_string = horse_string.replace('\n', '')
            if '1st dam' in horse_string:
                horse_string = horse_string.replace('1st dam', '1st dam\n')
            elif '2nd dam' in horse_string:
                horse_string = horse_string.replace('2nd dam', '\n2nd dam\n')
            # horse_string[-1].replace('\n', '')
            f2.write(horse_string + '\n')


    def shorten_file(og_file, new_file, num1, num2):
        '''Shortens the file based off the line numbers provided.
        the 4 outcomes:
        1. num1 and num2 are 0. --> Everything is written to the file.
        2. num1 is 0 and num2 is not 0. --> Everything up to num2 is written to the file. (This is a trick to get the 3x)
        3. num1 is not 0 and num2 is 0. --> Everything after num1 is written to the file. 
        4. num1 and num2 are not 0. --> Everything between num1 and num2 is written to the file.
        '''
        f = open(og_file, 'r')
        f2 = open(new_file, 'w')
        lines = f.readlines()
        n1 = 0
        n2 = 0
        if type(num1) == list:
            if len(num1) != 0:
                n1 = int(num1[0])
        if type(num1) == int:
            n1 = num1
        if type(num2) == list:
            if len(num2) != 0:
                n2 = int(num2[0])
        if type(num2) == int:
            n2 = num2
        if n1 == 0 and n2 == 0:
            # print("First String is 0. Everything was written.")
            f2.writelines(lines)
        elif n1 != 0 and n2 != 0:
            print("N1 was 0, but n2 was something")
            f2.writelines(lines[:n1])
            f2.writelines(lines[n2:])
        elif n1 != 0 and n2 == 0:
            f2.writelines(lines[n1:])
        elif n1 == 0 and n2 != 0:
            f2.writelines(lines[:n2])
        else:
            pass
        return f2


    def get_rr(file_name, new_file, horse):
        f = open(file_name, 'r+')

        lines = f.readlines()
        f.close()
        # f = open(file_name, 'w')
        f = open(horse, 'w')
        f2 = open(new_file, 'w')
        i = 0
        for line in lines:
            if 'RACE RECORD' in line:
                f2.writelines(lines[i:])
                break
            else:
                f.writelines(line)
            # else:
            #    f.writelines(line)
            i += 1


    def get_middle(file_name, new_file, string1, string2):
        f = open(file_name, 'r')
        lines = f.readlines()
        f2 = open(new_file, 'w')
        i = 0
        for line in lines:
            if string1 in line:
                for line in lines[i:]:
                    if string2 in line:
                        break
                    else:
                        f2.write(line)
            i += 1


    def get_line_number(file_name, re_string):
        '''Gets the line number of a specific regex in a file.'''
        line_number = []
        f = open(file_name, 'r')
        lines = f.readlines()
        num = 0
        for line in lines:
            if re_string.search(line):
                # line_number = line_number.append(num)
                # print(num)
                line_number.append(num)
                # i += 1
            else:
               pass
            num += 1
        return line_number


    def diff_report(original, update, report, hip):
        '''Creates a report for each hip number. Takes the lists from get_meta_data() and the path to the report directory'''
        i = 0
        if os.path.isdir(report):
            os.remove(report)
        f = open(original, "r")
        f2 = open(update, "r")
        f3 = open(report, 'w')
        f4 = open(f"{p_report}/pp/{hip}.html", 'w')
        flines = f.readlines()
        flines2 = f2.readlines()
        diff = difflib.ndiff(flines, flines2) #, fromfile=f"{original}", tofile=f"{update}"
        diffh = difflib.HtmlDiff().make_file(flines, flines2, f"{original}", f"{update}")
        f3.write(''.join(diff))
        f4.write(''.join(diffh))


    def get_difference(list):
        '''Gets the difference between each number in a list'''
        n = 0
        global list_difference
        list_difference = []
        list_difference = [list[i+1]-list[i] for i in range(len(list)-1)]
        return list_difference


    def clean_file(file_name, new_file):
        '''Cleans up the files by removing the extra lines and adding a blank line at the end of the file.'''
        f = open(f"{file_name}", 'r')
        f2 = open(f"{new_file}", 'w')
        lines = f.readlines()
        # Regex for junk spaces:
        re_junk = re.compile(r'(?!^)(\s{3}\.?([\s\.])*)')
        for line in lines:
            if re_junk.search(line):
                # print("Found junk")
                line = re.sub(re_junk, ' ', line)
                f2.writelines(line)
            else:
                f2.writelines(line)
        return f2

    def jettison_shit(file_name, new_file):
        '''Removes the junk lines, like unnamed, ect.'''
        f = open(f"{file_name}", 'r')
        f2 = open(f"{new_file}", 'w')
        lines = f.readlines()
        # Regex for junk spaces:
        re_unnamed = re.compile(r'Unnamed')
        re_unnamed_exception = re.compile(r'Racing in ')
        re_unraced = re.compile(r'Unraced.+\n')
        producer_exception = re.compile(r'(Producer)|(Dam of)')
        re_unplaced = re.compile(r'Unplaced.+\n')
        re_placed = re.compile(r'\b[pP]laced.')
        re_dam = re.compile(r'\d[stnd]+\sdam')
        for line in lines:
            if producer_exception.search(line) or re_dam.search(line):
                f2.writelines(line)
            elif 'See above' in line:
                f2.writelines(line)
            elif re_unnamed.search(line):
                pass
            elif re_unraced.search(line):
                pass
            elif re_unplaced.search(line):
                pass
            elif re_money.search(line) == None:
                pass
            elif re_money.search(line):
                money = re_money.search(line)
                if int(money.group('money').replace(',', '')) >= 10000:
                    f2.writelines(line)

            # if re_unnamed.search(line) and not re_unnamed_exception.search(line):
            #     # Gets rid of the unnamed lines
            #     pass
            # if re_dam.search(line):
            #     f2.writelines(line)
            # elif re_unraced.search(line) and not producer_exception.search(line): # Gets rid of unraced w/o producer
            #     pass
            # elif re_unplaced.search(line) and not producer_exception.search(line) and not re_placed.search(line):
            #     pass
            # elif 'See above' in line:
            #     f2.writelines(line)
            # elif re_money.search(line) == None:
            #     pass
            # elif re_money.search(line):
            #     money = re_money.search(line)
            #     # print(money.group('money'))
            #     if int(money.group('money').replace(',', '')) < 10000 and not producer_exception.search(line):
            #         # f2.write(line+'poooop')
            #         print("Less than 5k")
            #         pass
            #     else:
            #         f2.writelines(line)
            else:
                f2.writelines(line)


    def append_files(file_1, file_2, file_3, new_file):
        '''Appends the files together'''
        f = open(f"{file_1}", 'r')
        f2 = open(f"{file_2}", 'r')
        f3 = open(f"{file_3}", 'r')
        f4 = open(f"{new_file}", 'w')
        lines = f.readlines()
        lines2 = f2.readlines()
        lines3 = f3.readlines()
        f4.writelines(lines)
        f4.writelines(lines2)
        f4.writelines(lines3)
        return f4


    ###########################################
    # Functions for the Fasig-Tipton Report
    ###########################################


    def get_update_strings(list):
        line_number = []
        global string_update
        for i, line in enumerate(list):
            if line.startswith("+"):
                # print("Line: ", i)
                # print("Lines: ", line)
                if i < len(list) - 1 and list[i+1].startswith("?"):
                    # print("Line: ", i+1)
                    # print("Lines: ", lines[i+1])
                    re_string = re.finditer(r'[+^]', list[i+1])
                    index = [m.start() for m in re_string]
                    line_number.append(i)
                    # print(index)
                    string_update = {}
                    string_update[i] = line[min(index):max(index)]
                else:
                    # print("Just a + line")
                    pass
            else:
                # print("Not a + line", i)
                pass
        return string_update


    def get_updates(file_name, horse):
        """reads through a file and finds the lines that starts with a + and then prints them"""
        f = open(f"{file_name}", 'r')
        f2 = open(f"{p_report}/fasig/{horse}.xml", 'w')
        lines = f.readlines()
        f.close()
        gen1 = get_generation(file_name)[0]
        gen2 = get_generation(file_name)[1]
        gen3 = get_generation(file_name)[2]
        gen4 = get_generation(file_name)[3]
        i = 0
        n = 0
        print("Starting on horse\n", horse)
        get_update_strings(lines)
        # print(get_update_strings(file_name))
        # line_index = get_update_strings(file_name)[0]
        # line_number = get_update_strings(file_name)[1]
        f2.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<FasigTiptonSalesServices>\n<Service>saleUpdates</Service>\n<FasigTiptonUpdates>\n\t<Update>\n")
        for line in lines:
            if i <= 1:
                pass
            elif line.startswith('-'):
                pass
            elif line.startswith('+'):
                if i in gen1:
                    f2.write(f"<hip>{horse}</hip>\n")
                    f2.write("<SaleEntryCode>PH23</SaleEntryCode>\n<SaleCode>FTFEB</SaleCode>\n<SaleName>FT FEB MIXED 21</SaleName>\n")
                    f2.writelines(f"update on line {i}: {line}")
                elif i in gen2:
                    print("Gen 1: ", gen1)
                    print("Gen 2: ", gen2)
                    f2.write(f"\t\t<hip>{horse}</hip>\n")
                    f2.write("\t\t<SaleEntryCode>PH23</SaleEntryCode>\n\t\t<SaleCode>FTFEB</SaleCode>\n\t\t<SaleName>FT FEB MIXED 21</SaleName>\n")
                    f2.write(f"\t\t<HorseName>{get_names(line, 2)}</HorseName>\n")
                    f2.write(f"\t\t<HorseYOB>{get_substring(line, re_yob)}</HorseYOB>\n")
                    f2.write(f"\t\t<HorseSex>{get_substring(line, re_sex)}</HorseSex>\n")
                  #   f2.write(f"{lines[get_closest(i, gen1)]}")
                    f2.write(f"{get_closest(i, gen1)}\n")
                    # f2.write(f"\t\t<DamName>{get_names(lines[get_closest(i, gen1)], 1)}</DamName>\n")
                    f2.write(f"\t\t<DamDamName>{get_names(lines[get_closest(i, gen1)], 1)}</DamDamName>\n")
                    f2.write(f"\t\t<SireName>Sire Name</SireName>\n")
                    f2.write(f"\t\t<OfficalPosition>3</OfficalPosition>\n")
                    f2.write(f"\t\t<RaceNumber>2</RaceNumber>\n")
                    f2.write(f"\t\t<RaceType>MCL</RaceType>\n")
                    f2.write(f"\t\t<Grade></Grade>\n")
                    f2.write(f"\t\t<RaceDate>20200606</RaceDate>\n")
                    f2.write(f"\t\t<TrackName>CHURCHILL DOWNS</TrackName>\n")
                    f2.write(f"\t\t<UpdPosition>2</UpdPosition>\n")
                    f2.write(f"<Generation>2</Generation>\n")
                    f2.write(f"<Earnings>$2,200</Earnings>\n")
                    f2.write(f"<BlackType>N</BlackType>\n")
                    f2.write(f"<WhiteType>Y</WhiteType>\n")
                    f2.write(f"<UpdateLink>http://www.test.equineline.com/to/be/determined/00003.htm</UpdateLink>\n")
                    f2.writelines(f"update on line {i}: {line}")
                    f2.writelines(f"Dam is in line {get_closest(i, gen1)}: {lines[get_closest(i, gen1)]}")
                elif i in gen3:
                    f2.write(f"\t\t<hip>{horse}</hip>\n")
                    f2.write("\t\t<SaleEntryCode>PH23</SaleEntryCode>\n\t\t<SaleCode>FTFEB</SaleCode>\n\t\t<SaleName>FT FEB MIXED 21</SaleName>\n")
                    f2.write(f"\t\t<HorseName>{get_names(line, 2)}</HorseName>\n")
                    f2.write(f"\t\t<HorseYOB>{get_substring(line, re_yob)}</HorseYOB>\n")
                    f2.write(f"\t\t<HorseSex>{get_substring(line, re_sex)}</HorseSex>\n")
                elif i in gen4:
                    f2.write(f"\t\t<hip>{horse}</hip>\n")
                    f2.write("\t\t<SaleEntryCode>PH23</SaleEntryCode>\n\t\t<SaleCode>FTFEB</SaleCode>\n\t\t<SaleName>FT FEB MIXED 21</SaleName>\n")
                    f2.write(f"\t\t<HorseName>{get_names(line, 3)}</HorseName>\n")
                    f2.write(f"\t\t<HorseYOB>{get_substring(line, re_yob)}</HorseYOB>\n")
                    f2.write(f"\t\t<HorseSex>{get_substring(line, re_sex)}</HorseSex>\n")
            else:
                pass
            i += 1
        f2.write("\t</update>\n</FasigTiptonUpdates>\n</FasigTiptonSalesServices>")
        f2.close()
        n += 1


    def get_generation(file_name):
        """Gets the generation of the horse"""
        g1 = re.compile(r'^[\s+-]{2}([\w\*=]).+?(, by)')
        g2 = re.compile(r"^[\s+-]{5}([\w\*=])")
        g3 = re.compile(r"^[\s+-]{5}\.\s{2}[\w\*=]")
        g4 = re.compile(r"^[\s+-]{5}\.\s{2}\.\s{2}[\w\*=]")
        f = open(f"{file_name}", 'r')
        lines = f.readlines()
        lines_g1 = []
        lines_g2 = []
        lines_g3 = []
        lines_g4 = []
        for l, line in enumerate(lines):
            if g1.search(line):
                lines_g1.append(l)
            elif g2.search(line):
                lines_g2.append(l)
            elif g3.search(line):
                lines_g3.append(l)
            elif g4.search(line):
                lines_g4.append(l)
            else:
                pass
        return lines_g1, lines_g2, lines_g3, lines_g4


    def get_closest(k, nums):
        """Gets the closest number to k in nums"""
        max_num = 0
        for num in nums:
            if num < k and num > max_num:
                max_num = num
        return max_num

    def get_names(string, generation):
        """Gets the names of the horses"""
        re_gen1 = re.compile(r'(^[\s+]{2}(?P<name>[\w=\*].+?))(, by)')
        re_name = re.compile(r'^[\s+]+.*?((\w|=|\*).+?)\s\(')
        if generation == 1:
            name = re_gen1.search(string)
            return name.group('name')
        else:
            name = re_name.search(string)
            return name.group(1)

    def get_substring(string, regex):
        """Gets the substring from a string"""
        return regex.search(string).group(0)
        


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
    print("Done with meta data")

    print("Shortening files for original...") # This seperated the original files into 3 main groups to append later
    for horse in zip(source_list, hip_list):
        # line_third_dam = get_line_number(f"{p_original}/{horse[0]}.txt", three_dam_re) # Gets the line number of the 3rd dam in the original file
        line_1st_dam = get_line_number(f"{p_original}/{horse[0]}.txt", one_dam_re)
        shorten_file(f"{p_original}/{horse[0]}.txt", f"{p_original}/{horse[0]}_3.txt", 0, line_1st_dam) # Gets the 3x of the original file
        get_rr(f"{p_original}/{horse[0]}.txt", f"{p_original}/{horse[0]}_2.txt", f"{p_original}/{horse[0]}_norr.txt")
        get_middle(f"{p_original}/{horse[0]}_norr.txt", f"{p_original}/{horse[0]}_1.txt", '1st dam', '3rd dam') # Gets the 1st and 2nd dam into a separate file , f"{p_original}/{horse[0]}_1.txt"


    print("Shortening files for update...") # This seperated the update files into 3 main groups to append later
    for horse in zip(source_list, hip_list):
        get_rr(f"{p_update}/PH{horse[1].zfill(6)}.txt", f"{p_update}/PH{horse[1].zfill(6)}_2.txt", f"{p_update}/{horse[1]}_norr.txt") # Gets the Record and Produce of the update file
        # get_middle(f"{p_update}/PH{horse[1].zfill(6)}.txt", f"{p_update}/PH{horse[1].zfill(6)}_1.txt", '1st dam', '3rd dam') # Gets the 1st and 2nd dam into a separate file
        line_1st_dam = get_line_number(f"{p_update}/PH{horse[1].zfill(6)}.txt", one_dam_re)
        shorten_file(f"{p_update}/PH{horse[1].zfill(6)}.txt", f"{p_update}/PH{horse[1].zfill(6)}_3.txt", 0, line_1st_dam) # Gets the 3x of the update file
        get_middle(f"{p_update}/{horse[1]}_norr.txt", f"{p_update}/PH{horse[1].zfill(6)}_1.txt", '1st dam', '3rd dam')


    print("Seperating the lines...")
    for horse in zip(source_list, hip_list):
        # print("Seperating lines for", horse[0])
        line_sex_sire = get_line_number(f"{p_original}/{horse[0]}_1.txt", sex_sire_re)
        # print("For", horse[0])
        # print(line_sex_sire)
        seperate_lines(f"{p_original}/{horse[0]}_1.txt", f"{p_original}/{horse[0]}_4.txt", line_sex_sire, True)
        line_sex_sire = get_line_number(f"{p_update}/PH{horse[1].zfill(6)}_1.txt", sex_sire_re)
        seperate_lines(f"{p_update}/PH{horse[1].zfill(6)}_1.txt", f"{p_update}/PH{horse[1].zfill(6)}_4.txt", line_sex_sire, True)


    print("Cleaning files...")
    for horse in zip(source_list, hip_list):
        clean_file(f"{p_original}/{horse[0]}_4.txt", f"{p_original}/{horse[0]}_5.txt")
        clean_file(f"{p_update}/PH{horse[1].zfill(6)}_4.txt", f"{p_update}/PH{horse[1].zfill(6)}_5.txt")
    print("Done cleaning files")

    print("Jettisoning files...")
    for horse in zip(source_list, hip_list):
        jettison_shit(f"{p_original}/{horse[0]}_5.txt", f"{p_original}/{horse[0]}_test.txt")
        jettison_shit(f"{p_update}/PH{horse[1].zfill(6)}_5.txt", f"{p_update}/PH{horse[1].zfill(6)}_test.txt")

    print("Appending files...")
    for horse in zip(source_list, hip_list): # I'm changing out _5 with _test
        append_files(f"{p_original}/{horse[0]}_3.txt", f"{p_original}/{horse[0]}_test.txt", f"{p_original}/{horse[0]}_2.txt", f"{p_original}/{horse[0]}_final.txt")
        append_files(f"{p_update}/PH{horse[1].zfill(6)}_3.txt", f"{p_update}/PH{horse[1].zfill(6)}_test.txt", f"{p_update}/PH{horse[1].zfill(6)}_2.txt", f"{p_update}/PH{horse[1].zfill(6)}_final.txt")
    print("Done appending files")
    
    print("Comparing files...")
    for horse in zip(source_list, hip_list):
        diff_report(f"{p_original}/{horse[0]}_final.txt", f"{p_update}/PH{horse[1].zfill(6)}_final.txt", f"{p_report}/{horse[1]}.txt", horse[1])
    print("Done comparing files")

    print("Cleaning up HTML...")
    for horse in zip(source_list, hip_list):
        with open(f"{p_report}/pp/{horse[1]}.html", 'r') as f:
            flines = f.readlines()
        with open(f"{p_report}/pp/{horse[1]}.html", 'w') as f:
            for line in flines:
                # [1mCATNIP[22m
                line = line.replace('[1m', '<strong>')
                line = line.replace('[22m', '</strong>')
                f.writelines(line)
    print("Done cleaning the diff")

    print("Making text file markdown...")
    # This is so I can manipulate the text file to make it look better
    for horse in zip(source_list, hip_list):
        with open(f"{p_report}/{horse[1]}.txt", 'r') as f:
            flines = f.readlines()
        with open(f"{p_report}/{horse[1]}.txt", 'w') as f:
            i = 0
            for line in flines:
                # [1mCATNIP[22m
                line = line.replace('[1m', '**')
                line = line.replace('[22m', '**')
                if i <= 1:
                    pass
                else:
                    f.writelines(line)
                i += 1

    print("Making an getting updates...")
    for horse in zip(source_list, hip_list):
        get_updates(f"{p_report}/{horse[1]}.txt", horse[1])

    print("Cleaning up...")
    for horse in zip(source_list, hip_list):
        os.remove(f"{p_original}/{horse[0]}_1.txt")
        os.remove(f"{p_original}/{horse[0]}_2.txt")
        os.remove(f"{p_original}/{horse[0]}_3.txt")
        os.remove(f"{p_original}/{horse[0]}_4.txt")
        os.remove(f"{p_original}/{horse[0]}_5.txt")
        os.remove(f"{p_original}/{horse[0]}_norr.txt")
        os.remove(f"{p_original}/{horse[0]}_test.txt")
        os.remove(f"{p_original}/{horse[0]}_final.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_1.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_2.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_3.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_4.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_5.txt")
        os.remove(f"{p_update}/{horse[1]}_norr.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_final.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_test.txt")
    # print("Done cleaning up")

    print("Done")
    stop_time = timeit.default_timer()
    print("Total time: ", stop_time - start_time)


if __name__ == "__main__":
    main()