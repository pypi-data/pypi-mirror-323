from setuptools import setup, find_packages

setup(
    name="sudhanshu_image_augmentor",
    version="0.2",
    packages=find_packages(),
    
    description="A tool for augmenting images using various transformations.",
    
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    
    # Author info
    author="Sudhanshu Shekhar Karn",
    author_email="sudhanshuskarn@gmail.com",
    
    url="https://github.com/sudhanshuskarn/sudhanshu_image_augmentor",
    
    install_requires=[
        "Pillow>=8.0.0",
        "pytest>=6.0.0",
        "psutil==6.1.1",
        "pluggy>=1.0.0",
    ],
    
    entry_points={
        'console_scripts': [
            'image-augmentor=image_augmentor.cli:main',
        ],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
    ],
    
    python_requires='>=3.12',
    
    license="MIT",
    license_files=["LICENSE"],
)

