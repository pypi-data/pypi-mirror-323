import argparse
from pathlib import Path
from ascii_monet.ascii_monet import ascii_monet


sample_image_names = [
    'assets/pearl.png',
    'assets/darkside.jpg',
    'assets/flowers.jpg',
    'assets/earth.jpg',
    'assets/mushrooms.webp',
    'assets/mushrooms_red.jpg',
]
sample_images = { Path(img).stem: str(Path(__file__).parent / img) for img in sample_image_names }


def main():
    parser = argparse.ArgumentParser(
        description="Generate ASCII art from an image."
    )
    parser.add_argument("image_path", nargs="?", help="Path to the image file")
    parser.add_argument('--verbose', '-v', action='store_true', help='Prints verbose logs', default=False)
    parser.add_argument('--stats', action='store_true', help='Prints stats', default=False)

    parser.add_argument('--sample', help='Select an image from one of the sample images included with the utility')

    parser.add_argument('--chars-to-use', '-chars', help='Give a list of chars to use in the image as a string')
    parser.add_argument('--grayscale', '-g', action='store_true', help='Prints image in grayscale')
    parser.add_argument('--light-background', action='store_true', help='Assumes white background when selecting chars')
    parser.add_argument('--top-perc', help='Select top percentile to use for luminance range', type=int, default=98)
    parser.add_argument('--bottom-perc', help='Select bottom percentile to use for luminance range', type=int, default=5)

    parser.add_argument('--terminal-width', action='store_true', help='Set image to terminal width')
    parser.add_argument('--terminal-height', action='store_true', help='Set image to terminal height')
    parser.add_argument('--width', '-wid', help='', type=int)
    parser.add_argument('--height', '-hei', help='', type=int)
    parser.add_argument('--max-width', help='', type=int)
    parser.add_argument('--max-height', help='', type=int)
    
    parser.add_argument('--all-ascii-chars', action='store_true', help='Use all visible ascii chars')
    parser.add_argument('--only-alpha', action='store_true', help='Only use alphabetic characters')
    parser.add_argument('--only-alpha-numeric', action='store_true', help='Only use alpha-numeric characters')

    # parser.add_argument('--background-color', '-bc', help='')
    # parser.add_argument('--char-aspect-ratio', help='Aspect ratio of chars given as a string as "H:W"')

    args = parser.parse_args()

    if not args.image_path and not args.sample:
        image_path = str(Path(__file__).parent / 'assets/pearl.png')
        print("\nWelcome to ascii-monet! Here is a sample image:\n")
        ascii_monet.generate(image_path, width=80, top_percentile=97)
        print('\npath: "{}"'.format(image_path))
        print("\nUSAGE: ascii-monet <image-path> <OPTIONS>\nuse --help to see options\n")
        exit(1)
    
    if [ x for x in [args.width, args.height, args.max_width, args.max_height, args.terminal_width, args.terminal_height] if x ] == []:
        # args.max_height = 40
        args.width = 100

    chars_to_use = None if not args.chars_to_use else list(args.chars_to_use)

    image_path = args.image_path
    if args.sample:
        image_path = sample_images.get(args.sample)
        if not image_path:
            print('Error: No such sample "{}"'.format(args.sample))
            print('Sample images: {}'.format(list(sample_images.keys())))
            exit(1)
    
    ret = ascii_monet.generate(
        image_path,
        verbose=args.verbose,
        stats=args.stats,
        custom_chars=chars_to_use,
        all_ascii=args.all_ascii_chars,
        only_alpha=args.only_alpha,
        only_alpha_num=args.only_alpha_numeric,
        terminal_width=args.terminal_width,
        terminal_height=args.terminal_height,
        width=args.width,
        height=args.height,
        max_height=args.max_height,
        max_width=args.max_width,
        light_background=args.light_background,
        grayscale_mode=args.grayscale,
        top_percentile=args.top_perc,
        bottom_percentile=args.bottom_perc,
    )
    if args.sample:
        print('\npath: "{}"\n'.format(image_path))
    exit(ret)


if __name__ == "__main__":
    main()
