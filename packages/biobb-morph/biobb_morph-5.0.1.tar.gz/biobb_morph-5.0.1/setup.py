import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_morph",
    version="5.0.1",
    author="Biobb developers",
    author_email="mferri@bsc.es",
    description="biobb_morph is the Biobb module collection to create patien-specific 3D meshes from IVD template examples.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility",
    url="https://github.com/bioexcel/biobb_morph",
    project_urls={
        "Documentation": "http://biobb-morph.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/",
    },
    packages=setuptools.find_packages(exclude=["docs", "test"]),
    package_data={"biobb_morph": ["py.typed"]},
    include_package_data=True,
    install_requires=[
        "biobb_common==5.0.0",
        "torch",
        "numpy-stl",
        "numpy",
        "trimesh",
        "matplotlib",
        "scikit-learn",
        "scipy",
        "meshio",
        "Rtree",
    ],
    python_requires=">=3.9",
    entry_points={"console_scripts": ["morph = biobb_morph.morph.morph:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
    ],
)
