import hashlib
import os
import platform
import shutil
import sys
import time

SAFE_MODE = True

UNICODE_ENCODE_ERR = "Unicode character not supported by your console."

def archive_it(archive_time_limit, target):
    if time.time() - os.path.getmtime(target) < archive_time_limit:
        return False
    else:
        return True

def days_to_seconds(days):
    return 24.0 * 60.0 * 60.0 * days

def clean_empty_dirs(root):
    walk = os.walk(root, topdown=False)
    for step in walk:
        dirpath = step[0]

        if 'DfsrPrivate' in dirpath:
            continue

        try:
            print(dirpath)

        except UnicodeEncodeError:
            print(UNICODE_ENCODE_ERR)

        try:
            os.rmdir(dirpath)

            try:
                print("Removed: %s" % dirpath)
            except UnicodeEncodeError:
                print(UNICODE_ENCODE_ERR)

        except OSError:
            try:
                print("Unable to remove: %s" % dirpath)
            except UnicodeEncodeError:
                print(UNICODE_ENCODE_ERR)

def gen_hash(src_path):
    _hash = hashlib.md5()
    with open(src_path, 'rb') as src_file:
        buf = src_file.read()
        _hash.update(buf)
    return _hash

def equal_hashes(file_1, file_2):
    file_1_hash, file_2_hash = gen_hash(file_1), gen_hash(file_2)
    if file_1_hash.hexdigest() == file_2_hash.hexdigest():
        return True
    else:
        return False

def remove_trailing_slash(path):
    if len(path) > 1 and not os.path.split(path)[1]:
        return path[:len(path)-1]
    else:
        return path

def main():
    archive_time = days_to_seconds(float(sys.argv[3]))
    archive_store = remove_trailing_slash(sys.argv[2])
    cur_dir = remove_trailing_slash(sys.argv[1])
    old_path, root = os.path.split(cur_dir)
    archive_root = os.path.join(archive_store, root)

    EXCLUDE_FILES = set('thumbs.db')

    problems = []

    try:

        os.mkdir(archive_root)

    except FileExistsError:
        pass

    print("\nThe (old) path prior to the directory to be archived %s" % old_path)
    print("Current directory: %s" % cur_dir)
    print("Archives are stored in: %s" % archive_store)
    print("Archive root for the present archival process: %s\n" % archive_root)

    walk = os.walk(cur_dir)

    for step in walk:
        dirpath, dirnames, filenames = step[0], step[1], step[2]
        cur_arch_dir = archive_store + dirpath[len(old_path):]

        dirnames[:] = [d for d in dirnames if 'DfsrPrivate' not in d]
        filenames[:] = [f for f in filenames if 'thumbs.db' not in f]

        try:
            print(dirpath)
        except UnicodeEncodeError:
            print(UNICODE_ENCODE_ERR)

        # Make the directories seen in this level of the walk.
        for dir in dirnames:
            try:
                os.mkdir(os.path.join(cur_arch_dir, dir))

            except FileExistsError:
                # If the directory already exists in the archive, nothing further must be done.
                pass

            except FileNotFoundError:
                problems.append(dirpath)


        # Check for old files, and archive them if necessary.
        for _file in filenames:
            if _file in EXCLUDE_FILES:
                continue

            else:
                src = os.path.join(dirpath, _file)
                if os.path.isfile(src) and archive_it(archive_time, src):
                    dst = os.path.join(cur_arch_dir, _file)

                    pywin32 = False
                    if platform.system() == 'Windows':
                        try:
                            import win32file
                            import win32security
                            pywin32 = True

                        except ImportError:
                            # Notify user that permissions will be lost if they proceed.
                            pass

                    try:
                        if pywin32:
                            acl = win32security.GetFileSecurity(src, win32security.DACL_SECURITY_INFORMATION)
                            win32file.CopyFile(src, dst, 0)
                            win32security.SetFileSecurity(dst, win32security.DACL_SECURITY_INFORMATION, acl)

                        else:
                            shutil.copy2(src, dst)

                        src_hash = gen_hash(src)
                        dst_hash = gen_hash(dst)

                        if src_hash.hexdigest() == dst_hash.hexdigest() and not SAFE_MODE:
                            os.remove(src)

                    except PermissionError:
                        # Log which file can't be copied.
                        pass

                    except FileNotFoundError:
                        problems.append(src)


    if not SAFE_MODE:
        # Clean up empty directories in the archive.
        print("Cleaning directories under: %s" % archive_root)
        clean_empty_dirs(archive_root)

        # Clean up empty directories in the source directory.
        print("Cleaning directories under: %s" % cur_dir)
        clean_empty_dirs(cur_dir)

    # Error reporting
    with open('problems.txt', mode='w', encoding='utf-8') as a_file:
        for problem in problems:
            a_file.write("%s\n" % problems)

if __name__ == '__main__':
    main()
