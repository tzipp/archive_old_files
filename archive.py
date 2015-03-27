import os
import shutil
import time


def archive_it(archive_time_limit, target):
    if time.time() - os.path.getmtime(target) < archive_time_limit:
        return False
    else:
        return True

def main():
    ARCHIVE_TIME = 31556952 # seconds = 365.2425 days
    ARCHIVE_STORE = '/home/farrell/archive'

    cur_dir = os.getcwd()
    old_path, root = os.path.split(cur_dir)
    archive_root = os.path.join(ARCHIVE_STORE, root)
    os.mkdir(archive_root)

    print("The (old) path prior to the directory to be archived %s" % old_path)
    print("Current directory: %s" % cur_dir)
    print("Archives are stored in: %s" % ARCHIVE_STORE)
    print("Archive root for the present archival process: %s" % archive_root)

    walk = os.walk(cur_dir)

    for step in walk:
        dirpath, dirnames, filenames = step[0], step[1], step[2]
        cur_arch_dir = ARCHIVE_STORE + dirpath[len(old_path):]

        # Make the directories seen in this level of the walk.
        for dir in dirnames:
            os.mkdir(os.path.join(cur_arch_dir, dir))

        # Check for old files, and archive them if necessary.
        for _file in filenames:
            if archive_it(ARCHIVE_TIME, os.path.join(dirpath,_file)):
                shutil.copy(os.path.join(dirpath, _file), os.path.join(cur_arch_dir, _file))

if __name__ == '__main__':
    main()







