'''
Project 1: import/export script
    - Import file created from baselight(Baselight_export.txt)
    - Import xytech work order (Xytech.txt)
    - Script will parse data
    - Computation done to match shareholder request, to replace file system from local baselightto facility
    storage (remember color correcter's prefer local storage for bandwidth issues)
        - Export CSV file ('/' indicates columns):
        - Line 1: Producer / Operator / job /notes
        - Line 4: show location / frames to fix
        - Frames in consecutive order shown as ranges

Information:
Baselight: for color grading; enhancing visual quality of files and/or tv shows
Xytech: for managing & scheduling resources

ArgParse:
python project1.py Xytech.txt Baselight_export.txt 
'''
import argparse

parser = argparse.ArgumentParser(information='Automates the process file transfers within Baselight and Xytech')
parser.add_argument('xy_file', type=argparse.FileType('r'))
parser.add_argument('bl_file', type=argparse.FileType('r'))
args = parser.parse_args()

misc = []
xytech_folder = []
with args.xy_file as file:
    for line in file:
        if line.startswith("Location") or line.startswith("Notes") or line.startswith("\n"):
            pass
        elif line.startswith("/"):
            line = line.strip()
            xytech_folder.append(line)
        else:
            line = line.strip()
            misc.append(line)

filed_folders = []
with args.bl_file as file:
    for line in file:
        parts = line.strip().split(" ")
        original_bl_folder = parts.pop(0)
        sub_bl_folder = original_bl_folder.replace("/images1/","")
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


misc_format = " / ".join(misc)
print(misc_format, '\n\n')
for content in filed_folders:
    print(content)

file_format = "\n".join(filed_folders)
with open("file.txt","w") as file:#create file and write
    file.write("%s\n\n%s" % (misc_format, file_format))