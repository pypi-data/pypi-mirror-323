# G4_PreprocessingLib

G4_PreprocessingLib is a Python library that provides a comprehensive toolkit for cleaning, preprocessing, and managing a pandas DataFrame.

## Features

1. **CleanData Method**:

This method cleans the dataset by handling NaN values based on column type (object or numerical). It will delete columns with NaN values exceeding a user-defined threshold (lim_nan) that by default is set at 65%. It also detects and handles outliers in numerical columns using the Z-score method. Finally, it supports multiple strategies for imputing missing values (mean, median, mode, bfill, ffill, max, and min). Bare in mind some of these methods can only be used for numerical values. Finally, threshold to discard outlier values can also be determined by the user but by default will have a value of 3 as it is the most common criteria to discard outlier values.

2. **EncodeColumn Method**:

Encodes categorical data in a specified column to numeric values using LabelEncoder. It has an option to choose if the user ones to mantain the original column and add an additional encoded column at the end or if the user wants to simply replace the existing column with the encoded one.

3. **DropColumn Method**:

Removes a specified column by its index, with error handling for out-of-range indices.

4. **HomogenizeData Method**:

Standardizes object type columns by converting its values to lowercase and stripping whitespaces.

## Installation

To use this library the user must ensure that the following libraries are installed and then use the package manager [pip](https://pip.pypa.io/en/stable/) to install the library.

```bash
pip install pandas numpy scipy scikit-learn

pip install G4_PreprocessingLib
```

## Usage

1. **Initialize the Class**

After importing the library and pandas into a python file, the user must load their dataset by using one of the many pandas commands made for that purpose. After that an instance of the class must be created. In this instance the user can specify the parameters previously mentioned or leave the default ones. The only parameter that is mandatory to provide is the dataset here defined as df.

```python
import G4_PreprocessingLib
import pandas as pd

# Load your dataset
df = pd.read_csv("your_dataset.csv")

# Create an instance of the class
data = DataStructure(df,65,'mode','mean',3)
```

2. **Clean the Dataset**

The next step is to apply the CleanData method to do a preprocessing procedure on the provided dataset with the parameters set by the user or, in the absence of them, the default parameters.
```python
data.CleanData()  # Cleans the DataFrame based on the provided parameters
```

3. **Encode and Decode Columns**

After cleaning the dataset additional procedures like encoding acertain object type columns.
```python
data.EncodeColumn(1,'Y')  # Encodes the column at index 1 and generates the encoded column at the end
```
4. **Drop a Column**

Additional columns can be eliminated with the DropColumn method.

```python
data.DropColumn(2)  # Removes the column at index 2
```
5. **Homogenize the categorical Data**
```python
data.HomogenizeData()  # Standardizes all object type columns
```
## Parameters
- **df**: The pandas DataFrame to process.
- **lim_nan**: Threshold (in percentage) for dropping columns based on NaN values. Default is 65%.
- **m_obj**: Strategy for imputing missing values in object-type columns. Choices are:
  - **'mode'** (default)
  - **'bfill'** (fills the column with the last value)
  - **'ffill'** (fills the column with the first value)
- **m_num**: Strategy for imputing missing values in numerical columns. Choices are:
  - **'mean'** (default)
  - **'median'**
  - **'mode'**
  - **'bfill'** (fills the column with the last value)
  - **'ffill'** (fills the column with the first value)
  - **'max'**
  - **'min'**
- **threshold**: Limit to determine if a value is an outlier.

Bare in mind that when using either 'bfill' or 'ffill' options, it will take the first non-NaN value that they find in the column an fill it with it starting from that value's position. Meaning that, if one of these methods is chosen and the last or first value, respectively, of the column is a NaN value, the program will not impute it.

## Error Handling

This library has taken into account possible mistakes that the user may make, so different error handling methods have been applied. 

- **InvalidMethodError**: raised for invalid imputation methods in m_obj or m_num.
- **InvalidParameterError**: raised if lim_nan is not a numeric value.
- **IndexError**: raised for out-of-range column indices in methods like DropColumn.
- **ValueError**:  raised when a function receives an argument of the correct type but with an inappropriate or invalid value.
- **KeyError**: raised when a key (or column name in this context) is not found or conflicts with existing keys in a dataFrame.

## Example

```python
import G4_PreprocessingLib as Plib
import pandas as pd

# Create a sample dataset
data_dict = {
    'Name': ['Alice', 'Bob', None, 'David'],
    'Age': [25, None, 23, 35],
    'Salary': [50000, 60000, None, 45000]
}

df = pd.DataFrame(data_dict)

# Initialize the DataStructure class
data = Plib.DataStructure(df,50,'mode','median',4)

# Clean the dataset
data.CleanData()

# Encode a column
data.EncodeColumn(0)

# Homogenize string data
data.HomogenizeData()

# View the cleaned DataFrame
print(data.df)
```

## License
This project is licensed under the MIT License. Feel free to use and modify it as needed.

[MIT](https://choosealicense.com/licenses/mit/)