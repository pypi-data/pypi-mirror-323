# DatasetHandler_Group2 Library

DatasetHandler_Group2 is a Python library designed to simplify data cleaning, preprocessing and visualization created by the PBL group 2 of the third year of the bachelor's degree in Engineering Physics Applied to Industry at the AsFabrik campus of Mondragon Unibertsitatea.

The library created by the group formed by Irati Azpilgain, Mikel Ballesteros, Ander Crespo, Estibaliz Cruz, Lucas Lafuente and Mikel Puerta offers an easy-to-use interface for common data science tasks such as handling missing values, removing outliers and creating graphs.

## Usage

Here's a basic example of how to use DatasetHandler_Group2:

```python
from DataHandler_Group_2 import DatasetHandler_Group_2

# Initialize with your dataset and start the menu
handler = DatasetHandler_Group_2("sample.csv")
handler.initiate()
```
After writing this lines, your "sample.csv" will be read and a menu will show up, showing the functions that the library has. 

## Features

- Load datasets from CSV or Excel files.
- Clean data by dropping or imputing missing values.
- Treat existing data of your file.
- Detect and remove outliers.
- Generate descriptive plots such as histograms, scatter plots, boxplots and heatmaps.
- Save the cleaned dataset back to a file if desired.

## Dependencies

The following Python libraries are required:

- pandas
- numpy
- seaborn
- matplotlib
- scikit-learn

You can install them via pip:

```bash
pip install pandas numpy seaborn matplotlib scikit-learn
```
## License

This project is licensed under the MIT License.

## Contact

For questions or issues, please contact mikel.puerta@alumni.mondragon.edu
