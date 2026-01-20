# Scene Date From Filename

This is a plugin for Stashapp to automatically add dates to scenes based on 
time information in the filename. I created this basically for the same reasons
as outlined in this [issue](https://github.com/stashapp/stash/discussions/3635).
Basically, I want my scenes to be sorted by newest to oldest by having stashapp use
the creation date/modification date. In my case, when I move my files in the future (after my hard drive dies) it will
break the very likely break the creation date, and I don't want to rely on the modification date,
so I created a python program to put the creation/modification date in the file name, then
created a stashapp plugin to add/update the date of the scenes based on the filename.

This is a custom plugin I developed myself, though some basic boiler plate was 
taken from one of the [plugins from the official repository](https://github.com/stashapp/CommunityScripts/tree/main/plugins/image_date_from_metadata).

# Usage

You must use the `add_time_to_filename.py` program to add timestamp information to your files
for the plugin to read. Usage is `python3 /path/to/program/add_time_to_filename.py /path/to/folder/to/rename.
The program will only search the given directory. It does not search recursively. Currently it uses the mtime.

Copy and paste `update_creation_date.py` and `update_creation_date.yml` into your plugins directory (next to your config.yml file,
which itself is probably in a directory nammed config). The files must be together, but they can be in whatever directory
you want them in, like `/plugins/random/path/update_creation_date.yml`. Reload your plugins in stash (settings -> plugins).

Once the files are dated you can use the plugin to automatically modify the dates. Note, if a file does not
have time information in the form of [[t-xxxxxxx]] it will be ignored. There are two tasks, one to
add dates to undated files, and one to update the dates on all items (overwriting existing ones). There is
also a hook task. Also, when a new scene is added to stashapp for the first time, the program will run on just that
one scene, check if it has time information, and add it automatically.


# TODO

- add an index.yml so you can just add the url in stash rather than having to manually add the plugin