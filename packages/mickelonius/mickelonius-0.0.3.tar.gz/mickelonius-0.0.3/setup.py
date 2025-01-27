import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mickelonius",
    version="0.0.3",
    author="Mike Lee",
    author_email="mike@mickelonius.com",
    description="Package containing various data analysis tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=[
        'data',
        'test',
        'python',
        'venv',
        'venv39',
        'vignettes',
        'dist',
        'build',
        'dask-worker-space',
        'ml.egg-info',
        'scripts',

    ]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)