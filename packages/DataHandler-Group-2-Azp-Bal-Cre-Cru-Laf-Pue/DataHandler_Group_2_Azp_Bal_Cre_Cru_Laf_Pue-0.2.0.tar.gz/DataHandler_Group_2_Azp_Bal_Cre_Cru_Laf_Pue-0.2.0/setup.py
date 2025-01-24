from setuptools import setup, find_packages
setup(
    name="DataHandler_Group_2_Azp_Bal_Cre_Cru_Laf_Pue",
    version="0.2.0",
    description="Dataset handler of group 2",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author="Irati Azpilgain, Mikel Ballesteros, Ander Crespo, Estibaliz Cruz, Lucas Lafuente y Mikel Puerta",
    author_email="mikel.puerta@alumni.mondragon.edu",
    url="https://github.com/Group_2_DataHandler/Group_2_DataHandler",
    packages=find_packages(),
    install_requires=["pandas","numpy","seaborn","matplotlib","scikit-learn","openpyxl","xlrd"],
    classifiers=["Programming Language :: Python :: 3",    "License :: OSI Approved :: MIT License","Operating System :: OS Independent",],
    python_requires=">=3.6",
)
