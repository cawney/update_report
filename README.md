# update_report

Update reports for Fasig

## Goals

- make a list of files based off hip number (00300.html)
- Take out all the unnamed horses
- See if I can get the difference in money
  - Don't put update horse if difference in update is little
- Get rid of the 3rd and 4th dam

## What's needed to run

- A folder, 'source\original', with the original files
- A folder, 'source\update', with the updated files
- A folder for reports, 'reports'
- Both folders (update and orginal) should have all the files in them, if not it will break.

## Steps

1. Read the files, and get 2 lists
   1. the source file list
   2. the hip list (this is less important because the horse files are already in hip order)
2. Get rid of horses that are withdrawn

## To do

- [ ] Get rid of the 3rd and 4th dam in the original to compare
- [ ] get the rest of the line numbers for different spots in the pedigree (1st dam, 2nd, where the horses are)
- [ ] run the report off of the stringed out version of the pedigree and update
- [X] String it out so each horse is on a line of itself
