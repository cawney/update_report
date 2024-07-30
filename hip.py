import re
from os import getcwd as cwd
# import argv

# Read the file

local_path = cwd()
file_name = 'NYSELDAM.TXT'
file_path = local_path + '/' + file_name

hip_number = 1
print("Current working directory: {0}".format(local_path))
print(local_path)

with open(file_path, 'r') as file:
   contents = file.readlines()

# open the file to write to
f = open(file_path, 'w')


# If line starts with regex '^sa0', then add hip number:n to the line above it
for i, line in enumerate(contents):
   if re.match(r'^sa0', line):
      # contents[i-1] = contents[i-1].strip() + '\nHip Number:{0}\nBarn Number:\n'.format(hip_number)
      # line = "Hip Number:{0}\nBarn Number:\n{line}".format(hip_number, line)
      line = "Hip Number:" + str(hip_number) + "\nBarn Number:\n" + line
      hip_number += 1
      # f.write(contents[i-1])
      f.write(line)
   else:
      f.write(line)
      continue

f.close()



# Write the updated contents back to the file
# with open(file_path, 'w') as file:
#    file.write(contents)

# print(contents)