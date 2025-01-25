from setuptools import setup, find_packages

setup(
    name="viyu-cli",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "viyu=viyu.cli:main",  # Register the `viyu` command
        ],
    },
    install_requires=[
        # Add your dependencies here (example: 'requests', 'flask', etc.)
    ],
    description="A custom Python CLI framework for managing server projects and apps",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/viyu-cli",  # Replace with your repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    long_description=open('README.md').read(),  # Read long description from README file
    long_description_content_type="text/markdown",
    license="MIT",
)
