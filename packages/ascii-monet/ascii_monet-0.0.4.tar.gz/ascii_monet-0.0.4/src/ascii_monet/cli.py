import argparse
import shutil
from pathlib import Path
from ascii_monet.ascii_monet import ascii_monet

def main():
    parser = argparse.ArgumentParser(
        description="Generate ASCII art from an image."
    )
    parser.add_argument("image_path", nargs="?", help="Path to the image file")
    parser.add_argument('--grayscale', '-g', action='store_true', help='Prints image in grayscale')
    parser.add_argument('--background-color', '-bc', help='Prints image in grayscale')

    args = parser.parse_args()

    if not args.image_path:
        print("Usage: ascii-monet <image-path> <OPTIONS>")
        exit(1)

    # get script dir
    scriptdir = Path(__file__).resolve().parent
    # print(scriptdir)
    
    terminal_width = shutil.get_terminal_size().columns
    print(terminal_width)

    print()
    ret = ascii_monet.generate(args.image_path)
    print()
    exit(ret)


if __name__ == "__main__":
    main()
