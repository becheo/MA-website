import subprocess
import time

import mysql.connector as mysql
# import app_helpers
import main

# TODO datei in Ordner mit 'testbench-control' speichern.
#  -> muss ja nur auf Datenbank zugreifen können

db = mysql.connect(
    host='localhost',
    user='root',
    passwd='aligator3',
    database='website'
)

# open cmd
# proc = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE)

# activate conda prompt out of cmd
# proc.stdin.write(
#     b"/K C:/Users/Oliver/Anaconda3/Scripts/activate.bat C:/Users/Oliver/Anaconda3\n")

# start the pyhton file running the test
# TODO conda activate virtualenv to the final virtualenv name (maybe: testbench)
# proc.stdin.write(
#     b"cd C:/Users/Oliver/Desktop/Masterarbeit/03_Software/testbench-control && python testbench_control.py\n")

# temporary file link for testing
# proc.stdin.write(
#     b"cd C:/Users/Oliver/Desktop/Masterarbeit/03_Software/z_Tutorials_Beispielprogramme/test-exe && python main.py\n")

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

cursor = db.cursor()

# TODO überlegen, welche methode hier besser ist: nur erster Eintrag oder alle fetchen
# result = cursor.execute("SELECT * FROM queue limit 1")
result = cursor.execute("SELECT * FROM queue")
files = cursor.fetchall()

print("Anzahl der Dateien in der Warteschlange: {}" .format(len(files)))
# for i in range(len(files)):
#     print(files[i])

print("Folgende Datei wird getestet: {}" .format(files[0]))
# database columns: | queueID | id | filename | add_date |
filename_now = files[0][2]
id_now = files[0][1]
# TODO hier später durch das testbench-control Programm ersetzen
# main.count(filename_now)
main.create_file(filename_now, id_now)

# delete file
# cursor = db.cursor()
# # TODO überlegen, welche id hier genommen werden soll bzw. auch, ob es die Möglichkeit
# # geben soll einen Test nochmal zu starten, obwohl er schon durchgeführt wurde
# cursor.execute("DELETE FROM queue WHERE id = %s", [id_now])
# db.commit()
# cursor.close()
