import os
import shutil
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from colorama import just_fix_windows_console, init
just_fix_windows_console() # gets ANSI working in Windows CMD
# init(strip=False) 

class ascii_monet:
    
    fonts = [
        "assets/Anonymous.ttf",
        "assets/fonts/iAWriterDuospace-Regular.otf",
        "assets/fonts/CascadiaMono-Regular.otf",
    ]
    font_path = os.path.join(os.path.dirname(__file__), fonts[-1])
    
    verbose = False
    stats = False
    
    @classmethod
    def generate(cls, image_path, custom_chars=None, all_ascii=False, only_alpha=False, only_alpha_num=False, terminal_width=False, terminal_height=False, height=None, width=80, max_height=100, max_width=None, light_background=False, grayscale_mode=False, top_percentile=90, bottom_percentile=5, verbose=False, stats=False):
        """ Given a path to an image, generates colored ASCII art of the image in the terminal """

        cls.verbose = verbose
        cls.stats = stats

        # image_path = os.path.join(os.curdir, path)
        if not os.path.exists(image_path):
            print('ERROR: Path does not exist: "{}"'.format(image_path))
            return 1
        
        cls.log('Generating ASCII art of image: "{}"'.format(image_path))
        
        chars = cls.getCharsToUse(custom_chars=custom_chars, all_ascii=all_ascii, only_alpha=only_alpha, only_alpha_num=only_alpha_num, light_background=light_background)
        cls.log('Using set of {} chars'.format(len(chars)))
        cls.log('chars: [  {}  ...  {}  ]'.format( ''.join(chars[0:10]), ''.join(chars[-10:]) ))

        image = np.array(Image.open(image_path))
        block_size = cls.getBlockSize(image.shape, terminal_width, terminal_height, height, width, max_height, max_width)
        blocks = cls.toBlocks(image, block_size)

        # get average block pixel values
        colors = []
        for row in blocks:
            color_row = []
            for char in row:
                pixel_mean = np.astype(np.mean(char, axis=(0, 1)), np.uint8)
                if grayscale_mode:
                    pixel_mean = np.ones_like(pixel_mean) * np.mean(pixel_mean)
                color_row.append(pixel_mean)
            colors.append(color_row)
        
        luminance_values = [ np.mean(x) for color_row in colors for x in color_row ]
        luminance_top_perc = int(np.percentile(luminance_values, top_percentile))
        luminance_bot_perc = int(np.percentile(luminance_values, bottom_percentile))
        cls.log("90th and 10th percentile luminance values: ({}, {})".format(luminance_top_perc, luminance_bot_perc))
        
        # display ascii image
        for color_row in colors:
            for RGB in color_row:
                char = cls.getChar(RGB, chars, min_luminance=luminance_bot_perc, max_luminance=luminance_top_perc)
                cls.print_colored_text(char, RGB, end='')
            print()
        
        return 0

    
    @classmethod
    def print_colored_text(cls, text, RGB, bold=True, end=None):
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
        
        if len(img.shape) > 2:
            depth = math.floor( img.shape[2] )
            blocks_shape = (hei, wid, block_rows, block_cols, depth)
        else:
            blocks_shape = (hei, wid, block_rows, block_cols) # grayscale, no 'depth'
        blocks = np.empty(blocks_shape, dtype=np.uint8)
        for J in range(hei):
            for I in range(wid):
                block = img[
                    J*block_rows:(J+1)*block_rows,
                    I*block_cols:(I+1)*block_cols,
                ]
                blocks[J][I] = block
        return blocks
    
    
    @classmethod
    def getChar(cls, RGB, chars, min_luminance=0, max_luminance=255):
        max_fluct = 3
        luminance = np.mean(RGB)
        idx = math.floor(cls.map_value(luminance, min_luminance, max_luminance, 0, len(chars)-max_fluct-1))
        RGB_mapped = [ int(cls.map_value(int(x), 0, 255, 0, 3)) for x in RGB ]
        random.seed(str(RGB_mapped) + '111111')
        if max_fluct:
            idx_fluct = random.randint(-max_fluct, max_fluct-1)
            idx += idx_fluct
        idx = cls.contain_value_between(idx, 0, len(chars)-1)
        # return str(idx_fluct+max_fluct)
        # return str(idx%10)
        return chars[idx]
    

    @classmethod
    def getCharsToUse(cls, custom_chars=None, all_ascii=False, only_alpha_num=False, only_alpha=False, light_background=False):
        chars_upper = [ chr(x) for x in range(65, 91) ]
        chars_lower = [ chr(x) for x in range(97, 123) ]
        chars_digits = [ str(x) for x in range(10) ]
        chars_all = [ chr(x) for x in range(33, 127) ]

        chars = chars_all
        if custom_chars:
            chars = custom_chars
        elif all_ascii:
            chars = chars_all
        elif only_alpha:
            chars = chars_upper + chars_lower
        elif only_alpha_num:
            chars = chars_upper + chars_lower + chars_digits
        chars.sort(key=lambda ch: cls.get_on_off_pixel_ratio(ch, cls.font_path), reverse=(light_background==True))
        return chars
    
    
    @classmethod
    def getBlockSize(cls, img_shape, use_terminal_width, use_terminal_height, height, width, max_height, max_width):

        block_ar = 20/9
        img_ar = img_shape[0] / img_shape[1]

        def calculate_display_width(height):
            return height * img_ar

        def calculate_display_height(width):
            return width / img_ar
        
        terminal_width, terminal_height = shutil.get_terminal_size()

        display_width = 80

        if width:
            display_width = width
        
        elif height:
            display_width = calculate_display_width(height)
        
        elif use_terminal_width:
            display_width = terminal_width
        
        elif use_terminal_height:
            display_width = calculate_display_width(terminal_height)
        
        if max_height and calculate_display_height(display_width) > max_height:
            cls.log('Limiting to max height of:', max_height)
            display_width = calculate_display_width(max_height)
        
        if max_width and display_width > max_width:
            cls.log('Limiting to max width of:', max_width)
            display_width = max_width
        
        block_w = img_shape[1] / display_width
        block_h = block_w * block_ar
        block_w, block_h = int(np.ceil(block_w)), int(np.ceil(block_h))
        
        cls.log('image shape:', img_shape)
        cls.log('terminal_size: w={}  h={}'.format(terminal_width, terminal_height))
        cls.log('display_width:', display_width)
        cls.log('display_height:', calculate_display_height(display_width))
        cls.log('block_w:', block_w)
        
        return block_h, block_w
    
    
    @classmethod
    def log(cls, *args):
        if cls.verbose:
            print(*args)
    
    
    #region static methods
    
    @staticmethod
    def map_value(x, a_min, a_max, b_min, b_max):
        return b_min + (x - a_min) * (b_max - b_min) / (a_max - a_min)
    
    @staticmethod
    def contain_value_between(x, lower, upper):
        return max(min(x, upper), lower)
    
    @staticmethod
    def get_on_off_pixel_ratio(char, font_path):
        font_size = 24
        
        ar = 7/12
        img = Image.new('1', (int(font_size*ar), font_size), 0) # '1' mode is 1-bit pixels
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(font_path, font_size)
        draw.text((0, 0), char, font=font, fill=1)

        pixels = list(img.getdata())
        on_pixels = pixels.count(1)
        off_pixels = pixels.count(0)

        total_pixels = on_pixels + off_pixels
        if total_pixels == 0:
            return 0
        return on_pixels / total_pixels
    
    #endregion

