import os
import shutil
import sys
from shutil import copyfile

IMAGE_EXT = {'png', 'jpg', 'tif', 'tiff', 'gif', 'jpeg', 'psd', 'pdf', 'eps', 'ai', 'indd', 'raw'}
TOCOPY_EXT = {'tex', 'sty', 'bst', 'bib', 'log', 'bbl'}
COMMENT_START = '%'


def get_img_names_file_from_log(root_path, logfile):
    with open(logfile) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]

    pattern = '<use'
    img_names = []
    for i, line in enumerate(lines, 1):
        if line.startswith(pattern):
            img_name = line.split(' ')[1][:-1]
            img_name = os.path.join(root_path, img_name)
            img_names.append(img_name)

    return img_names


def find_files_by_extension(root, extensions):
    img_paths = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            ext = name.split('.')[-1]
            if ext not in extensions: continue
            img_path = os.path.join(path, name)
            img_paths.append(img_path)
    return img_paths


def copy_files(src_paths, root_path, tgt_dir):
    tgt_paths = []
    for src_path in src_paths:
        tgt_path = src_path.replace(root_path, tgt_dir)
        tgt_paths.append(tgt_path)
        copy_file(src_path, tgt_path)
    return tgt_paths


def copy_file(src_path, tgt_path):
    d = os.path.split(tgt_path)[0]
    if not os.path.exists(d):
        os.makedirs(d)
    copyfile(src_path, tgt_path)


def delete_comments(tex_files):
    for tex_file in tex_files:
        delete_comments_file(tex_file)


def get_char_positions(s, tgt):
    pos = []
    for i, c in enumerate(s[:-1]):  # don't check the last character, we do not mind if it is % as it can be useful
        if c == tgt:
            pos.append(i)
    return pos


def delete_comments_file(tex_file):
    with open(tex_file) as f:
        lines = f.readlines()

    lines = [x.strip() for x in lines]
    clear_lines = []
    for line in lines:
        # comment-out the complete line
        if line.strip().startswith(COMMENT_START):
            continue
        # check if a part of a line should be commented out
        indices = get_char_positions(line, COMMENT_START)
        end = -1
        for idx in indices:
            if line[idx - 1] != '\\':
                end = idx
                break
        if end > 0:
            clear_lines.append(line[:end] + '\n')
        else:
            clear_lines.append(line + '\n')

    with open(tex_file, 'w') as f:
        f.writelines(clear_lines)


def main(root_path, tgt_dir, logfile):
    # create new target directory
    os.makedirs(tgt_dir)

    # find all tex files
    source_files = find_files_by_extension(root_path, TOCOPY_EXT)
    source_files_new = copy_files(source_files, root_path, tgt_dir)

    # find all images and used images
    used_images = get_img_names_file_from_log(root_path, logfile)
    copy_files(used_images, root_path, tgt_dir)

    # delete comments
    delete_comments(source_files_new)

    # make a zip archive
    shutil.make_archive(tgt_dir, 'zip', tgt_dir)


if __name__ == '__main__':
    # path to the project
    root_path = sys.argv[1]
    # where the new project should be saved
    tgt_dir = sys.argv[2]
    # where is the .log file of the corresponding project
    # If you downloaded project from overleaf, you might need to download this .log file manually.
    # You can find it if you click the 'Logs and output files' next to 'Recompile' button. Then you need to scroll to
    # the bottom, click 'Other logs and files', and choose 'log file'.
    logfile = sys.argv[3]
    # Also note that, in case that you use bibtex, you need to download (and put to the project directory) the '.bbl'
    # file. You can find it in the Overleaf in the same place as the .log file.
    # See https://arxiv.org/help/submit_tex#bibtex.
    main(root_path, tgt_dir, logfile)
