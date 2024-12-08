import os
import sys
import glob

#------------------------------------------------

queue = sys.argv[1]

# Initial part of your files
pattern = '.folder_*'

# Use glob to find files that match the pattern
matching_files = glob.glob(pattern)

# Check if there are any matching files
if not matching_files:
    print(f"No files matching the pattern '{pattern}' were found in the directory {os.getcwd()}")
    sys.exit(1)  # Exit the script if no matching files are found

for file in matching_files:
    print(f"Processing file: {file}")
    
    with open(file, "r") as hf:

        txt = hf.read()
        folders = txt.split(",")
        folders.pop(-1)  # Remove the last empty element

        for folder in folders:
            folder = folder.strip()

            print(folder)
            
            # Convert to absolute path if not already absolute
            if not os.path.isabs(folder):
                folder = os.path.abspath(folder)
                
            print(f"Submitting job for folder: {folder}")
            os.system(f"bsub -M 10000 -oo {folder}/test_out.log -q {queue} {folder}/run.sh  ")
            print(f"Submitted run for {folder}")