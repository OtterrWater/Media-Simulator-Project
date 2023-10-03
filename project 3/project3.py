'''
Project 3:
- Run script with argparse command
- Call the populated database from proj2, find all ranges only that fall in
the length of video
- Using ffmpeg to extract timecode from video and
- write your own timecode method to convert marks to timecode
- Create Thumbnail (96x74) from each entry, but first frame

ffmpeg Documentation: https://ffmpeg.org/documentation.html
beginner commands: https://ostechnix.com/20-ffmpeg-commands-beginners/
'''
import argparse, pymongo, subprocess, xlsxwriter as excel, os

#ArgParse---------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('video', type = str, help='Name of video file')
parser.add_argument('-o', '--file_output', action='store_true', help='Create excel file')
args = parser.parse_args()

#MONGODB----------------------------------------------------------------------
client = pymongo.MongoClient("mongodb://localhost:27017")

db = client['database']
collection_2 = db["collection 2"]

datas = collection_2.find({"Location and Frame/Ranges": {"$exists": True}})
for data in datas:
    values = data["Location and Frame/Ranges"]
    for value in values:
        parts = value.split()#split the array into parts

#ffmpeg-------------------------------------------------------------------------
#GETTING FPS COUNT
video = 'twitch_nft_demo.mp4' #video name inserted w. parser
cmd = "ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1 -show_entries stream=r_frame_rate %s" % (video)
fps_process = subprocess.run(cmd, capture_output=True, text=True)
fps_str = fps_process.stdout.strip()
orgin_fps = int(fps_str.split('/')[0]) #60 fps

#EXTRACTING TIMECODE -> 1min 39seconds
command = 'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s' % (video)
orgin = float(subprocess.check_output(command, shell=True).decode().strip()) #99.626333 sec
orgin_video_frames = int(orgin*orgin_fps) #5977 frames


#frames -> timecode----------------------------------------------------------
def frame_to_timecode(frame):
    fps = orgin_fps
    secs = int(frame/fps)
    mins = int(secs/60)
    hrs = int(mins/60)
    frames = frame % fps
    secs %= 60
    mins %= 60
    tc = "{:02d}:{:02d}:{:02d}.{:02d}".format(hrs, mins, secs, frames)#timecode math
    return tc

#mongoDB----------------------------------------------------------------------
client = pymongo.MongoClient("mongodb://localhost:27017")

db = client['database']
collection_2 = db["collection 2"]

datas = collection_2.find({"Location and Frame/Ranges": {"$exists": True}})
#does not get single frames, only frame ranges (ex: 12-17)

all_file_format = []
for data in datas:
    values = data["Location and Frame/Ranges"]
    for value in values:
        parts = value.split()#split the array into parts
        files = parts.pop(0)
        file_frames = parts.pop(0)
        if '-' not in file_frames:
            pass
        else:
            frames = file_frames.split('-')
            first_frame = frames[0]
            second_frame = frames[1]
            if int(first_frame) < orgin_video_frames:
                first_timecode = frame_to_timecode(int(first_frame))
                second_timecode = frame_to_timecode(int(second_frame))
                all_file_format.append("%s %s-%s %s-%s" % (files, first_frame, second_frame, first_timecode, second_timecode))

#sorting by first frame---------------------------------------------------------
def extract_first_frames(x):
    parts = x.split()
    middle = parts[1]
    num = middle.split('-')
    first_frame = int(num[0])
    return first_frame

sorted_files = sorted(all_file_format, key=extract_first_frames)

for x in sorted_files:
    print(x)

#argsparse ------------------------------------------------------------------------
if args.video and args.file_output:#python project3.py twitch_nft_demo.mp4 -o
    #extracting first frames to get ss of photos from video -----------------------
    all_first_frames = []
    for x in sorted_files:
        first_frame = extract_first_frames(x)
        all_first_frames.append(first_frame)
        
    #frame to pic on specific frames---------------------------------------------------
    for i, frame in enumerate(all_first_frames):
        cmd = "ffmpeg -i %s -vf \"select=eq(n\\,%s),scale=96:74\" -q:v 2 %s" % (video, frame, f"output_{i}.jpg")
        image_file = subprocess.run(cmd, capture_output=True, text=True)

    #Excel creation-------------------------------------------------------------------
    workbook = excel.Workbook("demo_insert.xlsx")
    worksheet = workbook.add_worksheet("demo sheet")

    #inserting data into excel -------------------------------------------------------
    titles = ['Files', 'Frames', 'Timecode']
    for row, x in enumerate(sorted_files):
        parts = x.split()
        for col, part in enumerate(parts):
            worksheet.write(0, col, titles[col]) #inserting titles
            worksheet.write(row+1, col, part) #insert data

    # inserting the photos into excel ------------------------------------------------
    row = 1
    for i, frame in enumerate(all_first_frames):
        worksheet.insert_image(row + i, col+1, f"output_{i}.jpg", {'x_scale': 0.5, 'y_scale': 0.5})
        worksheet.set_row(row + i, 28)#height 28

    #adjusting personal width---------------------------------------------------------
    worksheet.set_column(0, 0, 55) #(first col, last col, width)
    worksheet.set_column(1, 1, 11)
    worksheet.set_column(2, 2, 23)

    workbook.close()

    for i, frame in enumerate(sorted_files):
            os.remove(f"output_{i}.jpg")

    print("Excel file created!")
elif args.video:#python project3.py twitch_nft_demo.mp4
    video_timecode = frame_to_timecode(int(orgin_video_frames))
    print("Processed Video: %s\nVideo Timecode: %s\nVideo fps: %s\n" % (video, video_timecode, orgin_fps))
    for x in sorted_files:
        print(x)
