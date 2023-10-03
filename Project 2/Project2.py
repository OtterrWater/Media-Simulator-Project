'''
Project 2: Now that we are part of a studio, we need to modify project 1's script to the
additional workflows and users on a per work order basis
• To handle "handoff" we will be using argparse
• Will also accept AutoDesk Flame files
• Parse naming of files to put into Database
• Insert data into Mongo DB
• Run script 5 separate times to populate data
• Answer questions with database calls

MongoDB 2 collection formats:
1) <User that ran script> <Machine> <Name of User on file> <Date of file> <submitted date>
2) <Name of User on file> <Date of file> <location> <frame/ranges>

RUNNING DATA
20230323:
python project2.py -x Xytech_20230323.txt -b Baselight_JJacobs_20230323.txt
python project2.py -x Xytech_20230323.txt -f Flame_DFlowers_20230323.txt
python project2.py -x Xytech_20230323.txt -f Flame_MFelix_20230323.txt
20230324:
python project2.py -x Xytech_20230324.txt -b Baselight_TDanza_20230324.txt
20230325:
python project2.py -x Xytech_20230325.txt -b Baselight_GLopez_20230325.txt
20230326:
python project2.py -x Xytech_20230326.txt -b Baselight_THolland_20230326.txt
python project2.py -x Xytech_20230326.txt -f Flame_DFlowers_20230326.txt
20230327:
python project2.py -x Xytech_20230327.txt -b Baselight_THolland_20230327.txt
python project2.py -x Xytech_20230327.txt -f Flame_DFlowers_20230327.txt
'''
import argparse, os, pymongo, getpass
from datetime import datetime

parser = argparse.ArgumentParser(description='Organize files')
parser.add_argument('-x','--xy_file', required=True)
parser.add_argument('-b','--bl_file')
parser.add_argument('-f','--f_file')
parser.add_argument('-v', '--verbose', action='store_true', help='print verbose')#prints in terminal
parser.add_argument('-o', '--file_output', action='store_true', help='print file')#creates csv file
args = parser.parse_args()

file_contents = {}#library of file contents

name_on_file = ""
date_on_file = ""
machine_on_file = ""

for filename in os.scandir('import_files'):
    if filename.is_file():
        with open(filename.path, 'r') as file:
            if args.xy_file in filename.name:
                file_contents[filename.name] = file.read() #read file contents 
                xy_file = file_contents[args.xy_file] #file contents get assigned to variable xy_file
                xy_filename = filename.name.strip('.txt').split('_')
                for num in xy_filename:
                    date_on_file = f"{num[:4]}/{num[4:6]}/{num[6:]}"#getting and formatting date on file

            elif args.bl_file is not None and args.bl_file in filename.name:
                file_contents[filename.name] = file.read()
                bl_file = file_contents[args.bl_file]
                bl_filename = filename.name.strip(".txt").split("_")
                machine_on_file = bl_filename.pop(0)#getting specific machine name
                name_on_file = bl_filename.pop(0)#getting name on file

            elif args.f_file is not None and args.f_file in filename.name:
                file_contents[filename.name] = file.read()
                f_file = file_contents[args.f_file]
                f_filename = filename.name.strip(".txt").split("_")
                machine_on_file = f_filename.pop(0)#getting specific machine name
                name_on_file = f_filename.pop(0)#getting name on file

# XYTECH FILE
xytech_folder = []
for line in xy_file.splitlines():
    if "/" in line:
        xytech_folder.append(line)

filed_folders = []
#XYTECH -> BASELIGHT
if args.bl_file is not None:
    for line in bl_file.splitlines():
        parts = line.strip().split(" ")
        original_bl_folder = parts.pop(0)
        sub_bl_folder = original_bl_folder.replace("/images1/Avatar","")
        for xy_line in xytech_folder:
            if sub_bl_folder in xy_line:
                processed_folder = xy_line
            
        first = ""
        temp = ""
        last = ""
        for num in parts:
            if "<err>" in num or "<null>" in num:
                continue

            if first == "":
                first = int(num)
                temp = first
                continue

            if int(num) == (temp+1):
                temp = int(num)
                continue
            else:
                last = temp
                if first == last:
                    filed_folders.append("%s %s" % (processed_folder, first))
                else:
                    filed_folders.append("%s %s-%s" % (processed_folder, first, last))
                first = int(num)
                temp = first
                last = ""
        last = temp
        if first != "":
            if first == last:
                filed_folders.append("%s %s" % (processed_folder, first))
            else:
                filed_folders.append("%s %s-%s" % (processed_folder, first, last))

#XYTECH -> FLAME
elif args.f_file is not None:
    for line in f_file.splitlines():
        parts = line.strip().split(" ")
        flame_archive = parts.pop(0)#takes out '/net/flame-archive'
        original_bl_folder = parts.pop(0)
        for xy_line in xytech_folder:
            if original_bl_folder in xy_line:
                processed_folder = xy_line

        first = ""
        temp = ""
        last = ""
        for num in parts:
            if "<err>" in num or "<null>" in num:
                continue

            if first == "":
                first = int(num)
                temp = first
                continue

            if int(num) == (temp+1):
                temp = int(num)
                continue
            else:
                last = temp
                if first == last:
                    filed_folders.append("%s %s" % (processed_folder, first))
                else:
                    filed_folders.append("%s %s-%s" % (processed_folder, first, last))
                first = int(num)
                temp = first
                last = ""
        last = temp
        if first != "":
            if first == last:
                filed_folders.append("%s %s" % (processed_folder, first))
            else:
                filed_folders.append("%s %s-%s" % (processed_folder, first, last))

#-----------------------------------------------------------------------------------
#DATE
current_day = datetime.now().strftime('%Y/%m/%d')

#get user of current system
username = getpass.getuser()

# Connect to the MongoDB Atlas cluster
cluster_url = f"mongodb://localhost:27017"
myclient = pymongo.MongoClient(cluster_url)
mydb = myclient["database"]# Access a database
dblist = myclient.list_database_names()

location_Frames_Ranges = "\n".join(filed_folders)
if args.bl_file and args.verbose or args.f_file and args.verbose:
    #<User that ran script> <Machine> <Name of User on file> <Date of file> <submitted date>
    collect_1 = "Collection 1:\nUser: %s\nMachine: %s\nName of User on File: %s\nDate of File: %s\nSubmitted Date: %s\n" % (username, machine_on_file, name_on_file, date_on_file, current_day)

    #<Name of User on file> <Date of file> <location> <frame/ranges>
    collect_2 = "\nCollection 2:\nName of User on file: %s\nDate of File: %s\nLocation and Frame/Ranges: \n%s" % (name_on_file, date_on_file, location_Frames_Ranges)

    print(collect_1, collect_2)

elif args.bl_file and args.file_output or args.f_file and args.file_output:
    #<User that ran script> <Machine> <Name of User on file> <Date of file> <submitted date>
    collect_1 = "Collection 1:\nUser: %s\nMachine: %s\nName of User on File: %s\nDate of File: %s\nSubmitted Date: %s\n" % (username, machine_on_file, name_on_file, date_on_file, current_day)

    #<Name of User on file> <Date of file> <location> <frame/ranges>
    collect_2 = "\nCollection 2:\nName of User on file: %s\nDate of File: %s\nLocation and Frame/Ranges: \n%s" % (name_on_file, date_on_file, location_Frames_Ranges)

    with open("FrameLocation.txt","w") as f:
        f.write(collect_1 + collect_2)
    
    print("File Created!")
    
elif args.bl_file or args.f_file:
    #<User that ran script> <Machine> <Name of User on file> <Date of file> <submitted date>
    col_1 = mydb["collection 1"]
    col_1_dict = {"User":username, "Machine":machine_on_file, "Name of User on File": name_on_file, "Date of File":date_on_file, "Submitted Date":current_day}
    col_1.insert_one(col_1_dict)#insert into database

    #<Name of User on file> <Date of file> <location> <frame/ranges>
    col_2 = mydb["collection 2"]
    col_2_dict = {"Name of User on File":name_on_file, "Date of File":date_on_file, "Location and Frame/Ranges" : filed_folders}
    col_2.insert_one(col_2_dict)#insert into database

    print("data inputted!")