import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spread_scoring_utilities",                      # Your package name (should be unique on PyPI)
    version="0.1.0",                                   # Package version
    author="sporter better",
    author_email="sporterbetter@gmail.com",
    description="Sports scoring utility module",
    long_description=long_description,                 # Renders on your package page on PyPI
    long_description_content_type="text/markdown",     # Tells PyPI to parse README as Markdown
    packages=setuptools.find_packages(),               # Automatically finds your package directories
    install_requires=[
        "numpy>=1.19.0",                               # Dependencies
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",       # Or whichever you choose
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
