import setuptools

# Read README for long description
with open('README.md', 'r', encoding='utf-8') as readme_file:
	LONG_DESCRIPTION = readme_file.read()

setuptools.setup(
    name="MLDockKit",
    version="0.0.6",
    include_package_data=True,  # Ensure non-code files are included
    description='Python package that calculates Lipinsky descriptors, predicts pIC50 and performs docking',
    url="https://github.com/clabe-wekesa/MLDockKit",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=[
        'rdkit', 'pandas', 'padelpy', 'joblib', 'gemmi', 
        'scikit-learn==1.6.1', 'scipy', 'numpy'
    ],
    author='Edwin Mwakio, Clabe Wekesa, Patrick Okoth',
    author_email='simiyu86wekesa@gmail.com',  
    package_data={
        'MLDockKit': [
            'padel_model.joblib',
            '5gs4.pdbqt',
            'meeko/*',  # Include everything in the meeko folder
        ],
    },
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent"
    ],
)

