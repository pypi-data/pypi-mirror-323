import argparse
import os
from image_augmentor.augmentor import augmentor

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Image Augmentation Tool")
    
    # Define arguments for input, output, image list, etc.
    parser.add_argument("input_directory", help="Directory with input images")
    parser.add_argument("output_directory", help="Directory to save augmented images")
    parser.add_argument("image_list", nargs='+', help="List of image filenames")
    parser.add_argument("--file_type", default="default", help="Output file type (jpg, png, or default)")
    parser.add_argument("--size", default="default", help="Resize images (width,height or 'default')")
    parser.add_argument("--total_output_for_each", type=int, default=50, help="Number of augmented images per input image")

    args = parser.parse_args()

    # Parse the size argument if it's not 'default'
    if args.size != "default":
        args.size = tuple(map(int, args.size.split(',')))

    # Expand the input and output directories in case they include environment variables like $HOME
    input_dir = os.path.expandvars(args.input_directory)
    output_dir = os.path.expandvars(args.output_directory)

    # Ensure that the directories are resolved properly before calling augmentor
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    # Call the augmentor function
    augmentor(
        input_directory=input_dir,
        image_list=args.image_list,
        output_directory=output_dir,
        file_type=args.file_type,
        size=args.size,
        total_output_for_each=args.total_output_for_each
    )

if __name__ == "__main__":
    main()

