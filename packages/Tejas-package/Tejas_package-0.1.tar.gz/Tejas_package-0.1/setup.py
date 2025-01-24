from setuptools import setup, find_packages

setup(
    name="Tejas_package",  # Replace with your package name
    version="0.1",  # Version of your package
    packages=find_packages(),  # Automatically finds all sub-packages
    install_requires=[],  # List any dependencies your package needs
    long_description=open('README.md').read(),  # Optional: Read the README
    long_description_content_type='text/markdown',  # Optional: If you're using Markdown for README
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # If you're using MIT License
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Define Python version requirements
    entry_points={
        "console_scripts": [
            "run-my-script = my_package.script:run_script",  # Optional: For CLI command
        ]
    },
)

