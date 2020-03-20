import subprocess

# open cmd
proc = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE)

# activate conda prompt out of cmd
proc.stdin.write(
    b"/K C:/Users/Oliver/Anaconda3/Scripts/activate.bat C:/Users/Oliver/Anaconda3\n")

# start the pyhton file running the test
# TODO conda activate virtualenv to the final virtualenv name (maybe: testbench)
# proc.stdin.write(
#     b"cd C:/Users/Oliver/Desktop/Masterarbeit/03_Software/testbench-control && python testbench_control.py\n")

# temporary file link for testing
proc.stdin.write(
    b"cd C:/Users/Oliver/Desktop/Masterarbeit/03_Software/z_Tutorials_Beispielprogramme/test-exe && python main.py\n")

# -----------------------------------------------------------------------------------
# possible programm outline:

# check database for entries
# while entries > 0:
#   get entry with lowest id from database and store filename in variable
#   print data form entry (name of file, id) and seperator(\n ----- \n)
#   run script 'testbench-control.py' with that filename as parameter
#   delete entry that was fetched from database
#   update entries (check database for entries)
#   print number of entries left in database
#
# when loop ends: program is finished and cmd will close automatically
