import os
import pytest
from PIL import Image
from image_augmentor.augmentor import augmentor

# Test helper function to set up temporary directories
@pytest.fixture
def setup_directories():
    input_dir = "test_input"
    output_dir = "test_output"
    
    # Create directories for testing
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a sample image for testing
    img = Image.new('RGB', (100, 100), color='red')
    img.save(os.path.join(input_dir, "test_image.jpg"))
    
    yield input_dir, output_dir  # Provide directories to the test function
    
    # Clean up after the test
    for f in os.listdir(input_dir):
        os.remove(os.path.join(input_dir, f))
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))
    os.rmdir(input_dir)
    os.rmdir(output_dir)

# Test the augmentor function
def test_augmentor(setup_directories):
    input_dir, output_dir = setup_directories
    
    # Call the augmentor function (adjust this based on your actual function's signature)
    augmentor(
        input_directory=input_dir,
        image_list=["test_image.jpg"],
        output_directory=output_dir,
        file_type="jpg",
        size=(50, 50),  # Resize the image to 50x50 for the test
        total_output_for_each=50  # Generate one augmented image
    )
    
    # Check that the output directory contains the expected augmented image(s)
    output_files = os.listdir(output_dir)
    assert len(output_files) > 0, "No augmented images were generated"
    
    # Check that the output image is in the correct format (jpg)
    output_image_path = os.path.join(output_dir, output_files[0])
    assert output_image_path.endswith(".jpg"), "Output image is not in the expected JPG format"
    
    # Check if the output image has the expected size (50x50)
    output_image = Image.open(output_image_path)
    assert output_image.size == (50, 50), f"Expected image size (50, 50), but got {output_image.size}"


