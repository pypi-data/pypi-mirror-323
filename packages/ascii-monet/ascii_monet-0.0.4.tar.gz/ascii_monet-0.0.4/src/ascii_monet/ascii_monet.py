import os
import math
import numpy as np
from PIL import Image
from colorama import just_fix_windows_console
just_fix_windows_console()

class ascii_monet:
    
    @classmethod
    def generate(cls, path):
        """ Given a path to an image, generates colored ASCII art of the image in the terminal """

        image_path = os.path.join(os.curdir, path)
        # image_path = os.path.abspath(os.path.join(os.curdir, path))
        if not os.path.exists(image_path):
            print('ERROR: Path does not exist: "{}"'.format(image_path))
            return 1
        
        print('Generating ASCII art of image: "{}"'.format(image_path))
        
        image = np.array(Image.open(image_path))
        block_size = np.astype(np.array((20,9)) * 0.8, int)
        blocks = cls.toBlocks(image, block_size)
        for row in blocks:
            for char in row:
                pixel_mean = np.astype(np.mean(char, axis=(0, 1)), np.uint8)
                char = cls.getChar(pixel_mean)
                cls.print_colored_text(char, pixel_mean, end='')
            print()

    
    @classmethod
    def print_colored_text(cls, text, RGB, bold=True, end=None):
        fmt = "\033[{};38;2;{};{};{}m{}\033[0m"
        cls.print_ansi(text, RGB, bold=True, end=end)
    
    @staticmethod
    def print_ansi(text, RGB, bold=True, end=None):
        bold_bit = '1' if bold else '0'
        fmt = "\033[{};38;2;{};{};{}m{}\033[0m"
        string = fmt.format(bold_bit, *RGB, text)
        print(string, end=end)
    
    
    @staticmethod
    def toBlocks(img, block_size=(8, 8)):
        block_rows, block_cols = block_size
        hei = math.floor( img.shape[0]/block_rows )
        wid = math.floor( img.shape[1]/block_cols )
        blocks = np.empty((hei, wid, block_rows, block_cols, 3), dtype=np.uint8)
        for J in range(hei):
            for I in range(wid):
                block = img[
                    J*block_rows:(J+1)*block_rows,
                    I*block_cols:(I+1)*block_cols,
                ]
                blocks[J][I] = block
        return blocks
    
    @staticmethod
    def getChar(px_mean):
        return '0'