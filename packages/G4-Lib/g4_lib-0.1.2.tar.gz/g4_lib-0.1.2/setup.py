from setuptools import setup, find_packages

setup( 
 name="G4_Lib",
 version="0.1.2",
 description="Automatic preprocessing library for dataset cleaning",
 long_description=open("README.md").read(),
 long_description_content_type="text/markdown",
 author="Group 4: Aiora De La Lama, Katalin Garcia, Sofia Garlito, Maren Lakalle, Julen Pagola, Naia Sanz",
 author_email="sofiamaria.garlito@mondragon.alumni.edu",
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
     "scikit-learn>0.24.0",
     "scipy>=1.0.0"
 ]
)
