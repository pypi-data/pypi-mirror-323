from setuptools import setup, find_packages

setup(
    name="simple_photo_organizer",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",  # Add other dependencies here
        "PyExifTool",
    ],
    entry_points={
        "console_scripts": [
            "simplephoto=simple_photo_organizer.cli:main", "photoorganizer=simple_photo_organizer.cli:main"
        ],
    },
    author="Quaesius",
    description="A CLI tool for sorting photos into folders according to their modification date and numbering them. Needs exiftool to work and asks for permission to install it, if it is not found.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Quaesius/Simple-Photo-Organizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)