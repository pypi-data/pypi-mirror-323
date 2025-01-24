from setuptools import setup, find_packages
setup(
 name="libreria_G5",
 version="0.1.3",
 description=" This library contains different functions to facilitate data preprocessing.",
 long_description=open("README.md").read(),
 long_description_content_type="text/markdown",
 author="Group 5: Garazi Alba, Janire Fuentes, Marcos Garro, Julen Olabarria, Mikel Ortega, Ekhi Sarasa",
 author_email="garazi.alba@alumni.mondragon.edu",
 packages=find_packages(),
 classifiers=[
 "Programming Language :: Python :: 3",
 "License :: OSI Approved :: MIT License",
 "Operating System :: OS Independent",
 ],
 python_requires=">=3.6",
 install_requires=[
 "pandas>=1.0.0",
 "numpy>=1.18.0",
 "scikit-learn>=0.24.0",
 "matplotlib>=3.3.0",
 "seaborn>=0.11.0",
 ],
)