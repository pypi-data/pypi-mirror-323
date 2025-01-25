import os
import random
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil  # To check the number of available CPU cores and usage

def augmentor(input_directory, image_list, output_directory, file_type="default", size="default", total_output_for_each=100):
    # Validate inputs
    if len(image_list) > 20:
        raise ValueError("You can provide a maximum of 20 images.")
    
    if not (50 <= total_output_for_each <= 200):
        raise ValueError("total_output_for_each must be between 50 and 200.")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Determine how many CPU threads we should use (70% of available cores)
    available_cores = psutil.cpu_count(logical=True)
    num_workers = max(1, int(available_cores * 0.7))  # Use 70% of the available cores (at least 1 worker)
    
    # Helper function to apply augmentations
    def apply_augmentation(image_path, output_count):
        img = Image.open(image_path)

        # Resize if needed
        if size != "default":
            img = img.resize(size)

        # Define augmentations
        augmentations = [
            lambda img: img.rotate(random.randint(0, 360)),  # Random rotation
            lambda img: ImageOps.mirror(img),  # Horizontal flip
            lambda img: ImageEnhance.Brightness(img).enhance(random.uniform(0.5, 1.5)),  # Brightness adjustment
            lambda img: ImageEnhance.Contrast(img).enhance(random.uniform(0.5, 1.5)),  # Contrast adjustment
            lambda img: ImageEnhance.Sharpness(img).enhance(random.uniform(0.5, 2.0)),  # Sharpness adjustment
            lambda img: ImageEnhance.Color(img).enhance(random.uniform(0.5, 1.5)),  # Color adjustment
            lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),  # Random horizontal flip
            lambda img: img.transpose(Image.FLIP_TOP_BOTTOM),  # Random vertical flip
            lambda img: img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 2.0))),  # Blur effect
            lambda img: crop_image(img),  # Random crop
        ]

        # Function for random cropping
        def crop_image(img):
            width, height = img.size
            left = random.randint(0, int(width * 0.2))
            upper = random.randint(0, int(height * 0.2))
            right = random.randint(int(width * 0.8), width)
            lower = random.randint(int(height * 0.8), height)
            return img.crop((left, upper, right, lower))

        # Generate and save augmented images
        basename, ext = os.path.splitext(os.path.basename(image_path))
        if file_type == "default":
            ext = os.path.splitext(image_path)[1]
        elif file_type:
            ext = f".{file_type.lower()}"
        
        for i in range(output_count):
            augmented_img = img.copy()
            # Apply a random number of augmentations (at least 2 augmentations)
            num_augmentations = random.randint(2, 5)
            applied_augmentations = random.sample(augmentations, num_augmentations)
            
            for augmentation in applied_augmentations:
                augmented_img = augmentation(augmented_img)
            
            output_name = f"{basename}_aug_{i+1}{ext}"
            output_path = os.path.join(output_directory, output_name)
            
            # Convert to RGB if necessary (JPEG does not support RGBA)
            if ext.lower() == ".jpg" or ext.lower() == ".jpeg":
                if augmented_img.mode == "RGBA":
                    augmented_img = augmented_img.convert("RGB")
            
            augmented_img.save(output_path)

    # Process each image using ThreadPoolExecutor (parallel processing)
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for image in image_list:
            image_path = os.path.join(input_directory, image)
            futures.append(executor.submit(apply_augmentation, image_path, total_output_for_each))
        
        # Wait for all futures to complete
        for future in as_completed(futures):
            future.result()  # Ensures exceptions are raised if any occurred during the processing


