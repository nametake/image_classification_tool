#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import Tkinter as tk
from PIL import ImageTk, Image
"""
python classification.py [face_img_dir] [char_list_file] [output_dir]
"""

INIT_KEY_CODE = 97
UNKNOWN_DIR_CODE = 121  # y
NO_CHARACTER_CODE = 122 # z

UNKNOWN_DIR = "00unknown"
NO_CHARACTER_DIR = "01no_character"

class ImageController(object):

    def __init__(self, images_dir_path, character_list, output_dir):
        self._images_dir_path = images_dir_path
        self._image_file_list = self._get_image_list(images_dir_path)
        self._character_list = character_list
        self._output_dir = output_dir
        self._moved_images = []

        self._create_dir()

    def _get_image_list(self, images_dir_path):
        """
        画像のファイル名のリストをバリデーションして返す。
        """
        tmp_images = os.listdir(images_dir_path)
        images = []
        for tmp in tmp_images:
            if tmp.find("png") == -1:
                continue
            images.append(tmp)
        r = re.compile("([0-9]+)")
        images.sort(cmp=lambda x,y: cmp(int(r.search(x).group(1)),
                                        int(r.search(y).group(1))))
        return images

    def _create_dir(self):
        if not os.path.isdir(self._output_dir):
            os.mkdir(self._output_dir)
        for char_name in self._character_list:
            char_dir = os.path.join(self._output_dir, char_name)
            if not os.path.isdir(char_dir):
                os.mkdir(char_dir)
        unknown_dir = os.path.join(self._output_dir, UNKNOWN_DIR)
        no_character = os.path.join(self._output_dir, NO_CHARACTER_DIR)
        if not os.path.isdir(unknown_dir):
            os.mkdir(unknown_dir)
        if not os.path.isdir(no_character):
            os.mkdir(no_character)


    def is_image_empty(self):
        if not self._image_file_list:
            return True
        return False

    def get_now_image_path(self):
        return os.path.join(self._images_dir_path, self._image_file_list[0])

    def rollback(self):
        if not self._moved_images:
            print "No moved images."
            return False
        image_name, moved_path = self._moved_images.pop()
        origin_path = os.path.join(self._images_dir_path, image_name)
        os.rename(moved_path, origin_path)
        self._image_file_list.insert(0, image_name)
        return True

    def move_image(self, keycode):
        # 画像の名前を取得
        image_name = self._image_file_list[0]

        # 移動前の画像パス
        from_path = os.path.join(self._images_dir_path, image_name)

        # 移動先の画像パス
        to_path = self._get_to_path(keycode, image_name)

        if to_path == None:
            print "Character index out of bounds."
            return False

        # 画像を移動
        os.rename(from_path, to_path)

        # 移動済のリストに格納
        self._image_file_list.pop(0)
        self._moved_images.append([image_name, to_path])

        return True

    def _get_to_path(self, keycode, image_name):

        if keycode == UNKNOWN_DIR_CODE:
            print "Unknown Character"
            return os.path.join(self._output_dir, UNKNOWN_DIR, image_name)
        if keycode == NO_CHARACTER_CODE:
            print "NO Character"
            return os.path.join(self._output_dir, NO_CHARACTER_DIR, image_name)

        char_index = keycode - INIT_KEY_CODE
        if char_index < 0 or len(self._character_list) <= char_index:
            return None
        character_name = self._character_list[char_index]
        print "Character name: {}".format(character_name)
        return os.path.join(self._output_dir, character_name, image_name)


class MatchIndexGetter(object):

    def __init__(self, list):
        self._list = list
        self._input_string = ''

    def add_char(self, char):
        self._input_string += char
        return self.get_match_count()

    def clear(self):
        self._input_string = ''

    def _search(self):
        indexes = []
        values = []
        for i, v in enumerate(self._list):
            find_index = str(v).find(self._input_string)
            if find_index == 0:
                indexes.append(i)
                values.append(v)
        return indexes, values

    def get_match_count(self):
        indexes, values = self._search()
        return len(indexes)

    def get_match_list(self):
        indexes, values = self._search()
        return values

    def get_match_index(self):
        indexes, values = self._search()
        return indexes


class ImageFrame(tk.Frame):
    def __init__(self, img_path, master=None):
        tk.Frame.__init__(self, master)
        image = Image.open(img_path)
        self.now_img = img_path
        self.img = ImageTk.PhotoImage(image)

        self.il = tk.Label(self, image=self.img)
        self.il.pack()

    def update(self, img_path):
        self.il.destroy()

        self.now_img = img_path
        image = Image.open(img_path)
        self.img = ImageTk.PhotoImage(image)

        self.il = tk.Label(self, image=self.img)
        self.il.pack()


def main():
    if len(sys.argv) <= 3:
        print "Not character file."
        sys.exit(0)

    #####################################################
    # Init
    #####################################################
    # Read image file
    images_dir = sys.argv[1]
    # Read character list file
    char_list_file = sys.argv[2]
    li = open(char_list_file).readlines()
    char_list = []
    for i, char in enumerate(li):
        c = char.rstrip("\n")
        char_list.append(c)
        print "{}: {}".format(chr(i + INIT_KEY_CODE), c)

    print "{}: {}".format(chr(UNKNOWN_DIR_CODE), "Unknown")
    print "{}: {}".format(chr(NO_CHARACTER_CODE), "No character")
    # Read output dir
    output_dir = sys.argv[3]

    img_con = ImageController(images_dir, char_list, output_dir)


    #####################################################
    # GUI
    #####################################################
    # Create window
    root = tk.Tk()
    frame = ImageFrame(img_con.get_now_image_path(), root)

    def key(event):
        # Shift
        if event.keysym_num == 0:
            return
        # End
        if event.keysym == "Escape":
            root.quit()
            return
        # Rollback
        if event.keysym == "space":
            img_con.rollback()
            frame.update(img_con.get_now_image_path())
            return

        img_con.move_image(event.keysym_num)
        if img_con.is_image_empty():
            root.quit()
            print "End!!!"
            return
        frame.update(img_con.get_now_image_path())

    frame.bind("<KeyPress>", key)
    frame.pack()
    frame.focus_set()

    root.mainloop()

if __name__ == '__main__':
    main()

