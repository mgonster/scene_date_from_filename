# Author: Mgonster
#
# This code, given a folder, will add an artificial timestamp to the filename.
# The timestamp is put at the end formatted as [[t-\d]] and is in nanoseconds.
# The files creation dates are read, they are put in order, then given timestamps
# starting from today and subtracting a day each iteration (newer items will have
# newer timestamps)

import os
import sys
from pathlib import Path
import re

if len(sys.argv) != 2:
    print("usage: add_time_to_filename.py /path/to/renaming/folder")
    exit()

os.chdir(sys.argv[1])
# os.chdir("./test/")

files = [{"path": p, "ctime_ns": p.lstat().st_mtime_ns} for p in Path(".").iterdir() if p.is_file()]
#sort by oldest files first (we will loop through them first and give them the newest dates)
files.sort(key=lambda x: x["ctime_ns"], reverse=True)
time_check = re.compile(r'\[\[t-\d+\]\]')
for i, file in enumerate(files) :
    file_object = file["path"]
    file_name = file_object.stem
    if time_check.search(file_name):
        continue
    suffix = file_object.suffix
    # 1 day is 24 hours is 60 minutes is 60 seconds is 1000 milliseconds is 1000 microseconds is 1000 nanoseconds
    one_day_in_ns = 1 * 24 * 60 * 60 * 1000 * 1000 * 1000
    # we double the offset to two days per item because there is a rare situation as seen with these two numbers:
    # 1762149076428115367 (Nov 2, 11:51:16 AM)
    # 1762062652059077262 (Nov 2, 12:50:52 AM)
    # even though they are a *day apart, they show as the same day in the America/Chicago timezone (CST)
    # so since these are artificial dates anyway, we just make the separation 2 days
    day_offset_ns = i * 2 * one_day_in_ns
    # we artificially set the time back by i days to allow for date ordering (since the
    # minimum distinguishable time is in days)
    birth_time = file["ctime_ns"] - day_offset_ns
    file_object.rename(f"./{file_name}[[t-{birth_time}]]{suffix}")