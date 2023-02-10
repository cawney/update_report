# update_report

Update reports for Fasig

## What's needed to run

- Latest version of Python 3 (any will work, but I'm running 3.10.5)
- A folder, 'source\original', with the original files
- A folder, 'source\update', with the updated files
- A folder for reports, 'reports'
- Both folders (update and orginal) should have all the files in them, if not it will break.

## Starting it up

- Open a terminal
- Navigate to where the folder is
- Make sure you have the right folders in place, if not, create them
  - souce>original, source>update, reports
  - files should be in original and update for the sale
- Run the command `python3 main.py *big file*`
  - My big file is FM1-586.txt

## Steps

1. Read the files, and get 2 lists
   1. the source file list
   2. the hip list (this is less important because the horse files are already in hip order)
2. Get rid of horses that are withdrawn
3. Seperate the source file into a few parts
   1. 3x
   2. Female
   3. Race Record
   4. Produce Record
4. For the female, RR and Produce record:
   1. Get a list of every horse in the pedigree using REGEX
   2. Seperate them into a long line, get rid of spacing less the beginning
5. Combine the files again now that the horses are on their own line
6. Compare the two files and get the difference
   1. Outputs HTML and txt files
7. Use the HTML file for Pedigree Productions
8. From txt file look for differences to include in the XML file
   1. If the difference in money is less than 1000, don't include it
   2. If the horse is new to the page and money is greater than 50000 include it
9. Write out XML to get the important stuff, if the parameters are not met, don't generate xml file

## To do

- [X] Get rid of the 3rd and 4th dam in the original to compare
- [X] run the report off of the stringed out version of the pedigree and update
- [X] String it out so each horse is on a line of itself
- [ ] Clean up the HTML file so it's not so ugly (Secondary)
