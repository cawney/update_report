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
    re_yob = re.compile(r"(?!\()(\d{4})\s") # Gets the YOB
   #  re_sex = re.compile(r"(?!by\s)([fcgr])")
    re_sex = re.compile(r"\d{4}\s([fcgr])")
    re_money = re.compile(r"(Total:\s|\d,\s)\$(?P<money>\d+(?:\,\d+(?:\,\d+)?)?)")
    re_sire = re.compile(r"(by (.)+?)(\)|\.)")
    re_date = re.compile(r', (?P<date>\d{4}),')
    re_name = re.compile(r'^[\s+]+.*?(([A-Z]|=\*).+?)((\s\()|(,))')
    produce_re = re.compile(r'^\d{4}')

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

    def get_produce(file_name, new_file, horse):
        f = open(file_name, 'r+')

        lines = f.readlines()
        f.close()
        f = open(horse, 'w')
        f2 = open(new_file, 'w')
        i = 0
        for line in lines:
            if 'PRODUCE RECORD' in line:
                f2.writelines(lines[i:])
                break
            else:
                f.writelines(line)
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
        diffh = difflib.HtmlDiff(wrapcolumn=150).make_file(flines, flines2, f"{original}", f"{update}")
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
            elif re_money.search(line) and int(re_money.search(line).group('money').replace(',', '')) >= 10000:
                f2.writelines(line)
            elif not re_unnamed.search(line) and not re_unraced.search(line) and not re_unplaced.search(line):
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
        f.close()
        f2.close()
        f3.close()
        f4.close()
        return f4


    ###########################################
    # Functions for the Fasig-Tipton Report
    ###########################################


    def get_update_strings(list):
        line_number = []
        global string_update
        line_starts_with_plus = re.compile(r'^\+')
        line_starts_with_minus = re.compile(r'^\-')
        line_starts_with_question = re.compile(r'^\?')
        string_update = []
        for i, line in enumerate(list):
            if i < 20:
                pass
            if line_starts_with_plus.search(line): # If the line starts with a +, then it's a potential update
                # print(line)
                # print("Line starts with + ", i)
                update_money = re_money.search(line) # Get the money from the line
                if update_money:
                    # print("Found money")
                    update_money = int(update_money.group('money').replace(',', ''))
                else:
                    update_money = 0
                            #    int(re_money.search(line).group('money').replace(',', ''))
                if i < len(list) - 1 and line_starts_with_question.search(list[i+1]): # If the next line starts with a ?, then it's a potential update
                    # print("Next line starts with ? ", i+1)
                    for j in reversed(list[:i]):
                        if line_starts_with_minus.search(j):
                            og_money = re_money.search(j) # Get the money from the line
                            if og_money:
                                og_money = int(og_money.group('money').replace(',', ''))
                            else:
                                og_money = 0
                            if update_money > og_money+1000: # If the update money is more than 5k greater than the original money, then it's a potential update
                                # line_number.append(i)
                                # f1.writelines(line)
                                # print('Update', line)
                                string_update.append(line)
                                line_number.append(i)
                                break
                            else:
                                break
                elif re.search(re_date, line) and update_money > 50000: # If the line has a date and the money is greater than 50k, then it's a potential update
                    # print("Found date ", i)
                    string_update.append(line)
                    line_number.append(i)
                else:
                    pass
            else:
                pass


        return string_update, line_number


    def get_updates(file_name, horse):
        """reads through a file and finds the lines that starts with a + and then prints them"""
        f = open(f"{file_name}", 'r')
        
        lines = f.readlines()
        f.close()
        gen1 = get_generation(file_name)[0]
        gen2 = get_generation(file_name)[1]
        gen3 = get_generation(file_name)[2]
        gen4 = get_generation(file_name)[3]
        i = 0
        n = 0
        the_strings = get_update_strings(lines)[0]
        the_numbers = get_update_strings(lines)[1]
        
        # for line, string in zip(lines, the_strings):
            # if i <= 20:
            #     pass
            # elif line.startswith('-'):
            #     pass
            # elif line.startswith('+'):
        print("Horse number ", horse)
        print("The strings ", the_strings)
        print("The numbers ", the_numbers)
        if len(the_strings) == 0:
            pass
        else:
            f2 = open(f"{p_report}/fasig/{horse}.xml", 'w')
            f2.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<FasigTiptonSalesServices>\n<Service>saleUpdates</Service>\n<FasigTiptonUpdates>\n\t<Update>\n")
            for line, string in zip(the_numbers, the_strings):
                # print(string)
                if string in lines:
                    # print("Found string", string, "in line", lines[line])
                    f2.writelines(string)
                    name_string = ''
                    horse_yob = ''
                    horse_sex = ''
                    dam_name = ''
                    dam_dam_name = ''
                    sire_name = ''
                    position = ''
                    if 'RACE RECORD' in string:
                        print("Butt")
                    if line in gen1:
                        name_string = get_names(string, 1)
                        horse_sex = 'f'
                        # sire_name = 
                    elif line in gen2:
                        dam_name = get_names(lines[get_closest(line, gen1)], 1)
                        # f2.write(f"\t\t<DamDamName>{get_names(lines[get_closest(line, gen1)], 1)}</DamDamName>\n")
                    elif line in gen3:
                        dam_name = get_names(lines[get_closest(line, gen2)], 3)
                        dam_dam_name = get_names(lines[get_closest(line, gen1)], 1)
                    elif line in gen4:
                        dam_name = get_names(lines[get_closest(line, gen3)], 4)
                    else:
                        pass
                    name_string = re_name.search(string).group(1)
                    horse_yob = re_yob.search(string)
                    if horse_yob:
                        horse_yob = horse_yob.group(1)
                    if re_sex.search(string):
                        horse_sex = re_sex.search(string).group(1)
                    sire_name = re_sire.search(string)
                    if sire_name:
                        sire_name = sire_name.group(1)
                        sire_name = re.sub(r'by ', '', sire_name)
                    f2.write(f"\t\t<hip>{horse}</hip>\n\t\t<SaleEntryCode>PH23</SaleEntryCode>\n\t\t<SaleCode>FTFEB</SaleCode>\n\t\t<SaleName>FT FEB MIXED 21</SaleName>\n")
                    f2.write(f'\t\t<HorseName>{name_string}</HorseName>\n')
                    f2.write(f"\t\t<HorseYOB>{horse_yob}</HorseYOB>\n")
                    f2.write(f"\t\t<HorseSex>{horse_sex}</HorseSex>\n")
                    f2.write(f"\t\t<DamName>{dam_name}</DamName>\n")
                    f2.write(f"\t\t<DamDamName>{dam_dam_name}</DamDamName>\n")
                    f2.write(f"\t\t<SireName>{sire_name}</SireName>\n")
                    f2.write(f"\t\t<OfficialPosition>{position}</OfficialPosition>\n")
                    f2.write(f"\t\t<RaceNumber></RaceNumber>\n")
                    f2.write(f"\t\t<RaceType></RaceType>\n")
                    f2.write(f"\t\t<Grade></Grade>\n")
                    f2.write(f"\t\t<RaceDate></RaceDate>\n")
                    f2.write(f"\t\t<TrackName></TrackName>\n")
                    f2.write(f"\t\t<UpdPosition></UpdPosition>\n")
                    f2.write(f"\t\t<Generation></Generation>\n")
                    f2.write(f"\t\t<Earnings></Earnings>\n")
                    f2.write(f"\t\t<BlackType></BlackType>\n") ## Y or N
                    f2.write(f"\t\t<WhiteType></WhiteType>\n") ## Y or N
                    f2.write(f"\t\t<UpdateLink></UpdateLink>\n")
                else:
                    pass
                i += 1
        
        #### Write the page:
                
        
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
            if name:
                return name.group(1)
            else:
                return None

    def get_substring(string, regex):
        """Gets the substring from a string"""
        return regex.search(string).group(1)
        


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

    print("Seperating files for original...") # This seperated the original files into 3 main groups to append later
    for horse in zip(source_list, hip_list):
        # line_third_dam = get_line_number(f"{p_original}/{horse[0]}.txt", three_dam_re) # Gets the line number of the 3rd dam in the original file
        line_1st_dam = get_line_number(f"{p_original}/{horse[0]}.txt", one_dam_re)
        shorten_file(f"{p_original}/{horse[0]}.txt", f"{p_original}/{horse[0]}_3.txt", 0, line_1st_dam) # Gets the 3x of the original file
        get_rr(f"{p_original}/{horse[0]}.txt", f"{p_original}/{horse[0]}_2.txt", f"{p_original}/{horse[0]}_norr.txt")
        get_produce(f"{p_original}/{horse[0]}_2.txt", f"{p_original}/{horse[0]}_produce.txt", f"{p_original}/{horse[0]}_rr.txt")
        
        get_middle(f"{p_original}/{horse[0]}_norr.txt", f"{p_original}/{horse[0]}_1.txt", '1st dam', '3rd dam') # Gets the 1st and 2nd dam into a separate file , f"{p_original}/{horse[0]}_1.txt"


    print("Shortening files for update...") # This seperated the update files into 3 main groups to append later
    for horse in zip(source_list, hip_list):
        get_rr(f"{p_update}/PH{horse[1].zfill(6)}.txt", f"{p_update}/PH{horse[1].zfill(6)}_2.txt", f"{p_update}/{horse[1]}_norr.txt") # Gets the Record and Produce of the update file
        get_produce(f"{p_update}/PH{horse[1].zfill(6)}_2.txt", f"{p_update}/PH{horse[1].zfill(6)}_produce.txt", f"{p_update}/PH{horse[1].zfill(6)}_rr.txt")
        line_1st_dam = get_line_number(f"{p_update}/PH{horse[1].zfill(6)}.txt", one_dam_re)
        shorten_file(f"{p_update}/PH{horse[1].zfill(6)}.txt", f"{p_update}/PH{horse[1].zfill(6)}_3.txt", 0, line_1st_dam) # Gets the 3x of the update file
        get_middle(f"{p_update}/{horse[1]}_norr.txt", f"{p_update}/PH{horse[1].zfill(6)}_1.txt", '1st dam', '3rd dam')


    print("Seperating the lines...")
    for horse in zip(source_list, hip_list):
        line_sex_sire = get_line_number(f"{p_original}/{horse[0]}_1.txt", sex_sire_re)
        line_produce = get_line_number(f"{p_original}/{horse[0]}_produce.txt", produce_re)
        seperate_lines(f"{p_original}/{horse[0]}_produce.txt", f"{p_original}/{horse[0]}_4.txt", line_produce, False)
        
        with open(f"{p_original}/{horse[0]}_rr.txt", "r") as f, open(f"{p_original}/{horse[0]}_2.txt", "w") as f2:
            lines = f.readlines()
            rr = []
            record = ''
            for line in lines:
                if re.search(r'no report', line):
                    pass
                else:
                    rr.append(line)
                record = ''.join(rr)
                record = record.replace('\n', '')
                record = record.replace('    ', ' ')
                # record = re.sub(r"\n\s{5}", ' ', record)
            f2.writelines(record+'\n')

        with open(f"{p_update}/PH{horse[1].zfill(6)}_rr.txt", "r") as f, open(f"{p_update}/PH{horse[1].zfill(6)}_2.txt", "w") as f2:
            lines = f.readlines()
            rr = []
            record = ''
            for line in lines:
                if re.search(r'no report', line):
                    pass
                else:
                    rr.append(line)
                record = ''.join(rr)
                record = record.replace('\n', '')
                record = record.replace('    ', ' ')
            f2.writelines(record+'\n')

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

    print("getting updates...")
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
        os.remove(f"{p_original}/{horse[0]}_produce.txt")
        os.remove(f"{p_original}/{horse[0]}_rr.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_1.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_2.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_3.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_4.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_5.txt")
        os.remove(f"{p_update}/{horse[1]}_norr.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_final.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_test.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_produce.txt")
        os.remove(f"{p_update}/PH{horse[1].zfill(6)}_rr.txt")
    # print("Done cleaning up")

    print("Done")
    stop_time = timeit.default_timer()
    print("Total time: ", stop_time - start_time)


if __name__ == "__main__":
    main()