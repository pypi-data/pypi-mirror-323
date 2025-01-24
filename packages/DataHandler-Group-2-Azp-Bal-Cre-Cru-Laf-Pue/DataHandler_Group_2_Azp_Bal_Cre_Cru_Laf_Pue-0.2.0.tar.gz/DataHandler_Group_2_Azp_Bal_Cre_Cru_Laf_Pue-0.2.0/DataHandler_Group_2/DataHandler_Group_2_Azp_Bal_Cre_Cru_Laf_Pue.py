import pandas as pd 
import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class DatasetHandler_Group_2:

    def __init__(self, data):
        self.data = data
        self.data_read = None

    def initiate(self):
        try:
            if data == '':
                raise ValueError("Data has not been loaded.")
            cond = 1
            self.read_table()
            if self.data_read is None:
                cond = 0
                raise ValueError("File not saved, exiting library")
            print("What do you want to do with your dataset?")
            while cond == 1:
                print("Function menu:")
                print("1. Show saved data.")
                print("2. Show data information.")
                print("3. Drop a column of the dataset.")
                print("4. Drop empty lines that surpass a threshold.")
                print("5. Drop lines that fulfill a condition.")
                print("6. Impute empty values.")
                print("7. Tidy columns.")
                print("8. Show unique values or quantiles.")
                print("9. Plot data.")
                print("10. Eliminate outliers from numerical columns.")
                print("11. Save data.")
                print("0. Exit")
                option = int(input("Which function of the library do you want to choose?\n"))
                if option == 0:
                    cond = 0
                    print("Exiting library. Thanks for using it!")
                elif option == 1:
                    self.show_data()
                elif option == 2:
                    self.show_info()
                elif option == 3:
                    self.drop_specific_column()
                elif option == 4:
                    self.drop_columns()
                elif option == 5:
                    self.drop_lines()
                elif option == 6:
                    self.impute_empty()
                elif option == 7:
                    self.tidy_categorical_columns()
                elif option == 8:
                    self.show_unique()
                elif option == 9:
                    self.plot_data()
                elif option == 10:
                    self.eliminate_outliers()
                elif option == 11:
                    self.save_dataset()
                elif option < 0 and option > 11:
                    raise ValueError("Choose an available option.")
        except ValueError as ve:
            print("Error: %s."%(ve))
        except TypeError:
            print("Error: Please enter a number.")

    def read_table(self): # Function to read the datasets imported.
        try:
            if self.data.split(".")[1] == "csv":
                print("Your file is a csv.")
                delimiter = input("Please, enter your delimiter: ")
                self.data_read = pd.read_csv(self.data, delimiter=delimiter).copy()
                if len(list(self.data_read.columns)) == 1:
                    cond = input("Is your file of only one column?\n(Y/N): ")
                    if cond.upper() == "N":
                        raise ValueError()
                print("Your data file %s has been copied." % (self.data))
            elif self.data.split(".")[1] == "xlsx":
                print("Your file is a xlsx Excel.")
                self.data_read = pd.read_excel(self.data, engine="openpyxl").copy()
                print("Your data file %s has been copied." % (self.data))
            elif self.data.split(".")[1] == "xls":
                print("Your file is a xls Excel.")
                self.data_read = pd.read_excel(self.data, engine="xlrd").copy()
                print("Your data file %s has been copied." % (self.data))
            else:
                print("File not supported, please ensure that your file is csv, xlsx or xls file.")
        except ImportError:
            print("Import error occurred.")
            print("If you want to read a xlsx file, please install openpyxl in your device.\nUse pip install openpyxl in your anaconda prompt.")
            print("If you want to read a xls file, please install xlrd in your device.\nUse pip install xlrd in your anaconda prompt.")
        except ValueError:
            print("Delimiter wrong, please make sure you choose the correct delimiter.")
        except FileNotFoundError:
            print("File not found in the folder.")

    def show_data(self): # Function to show the first lines of the dataset, in case the value is empty, all the data will be shown.
        try:
            if self.data_read is None:
                    raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            lines = int(input("How many lines do you want to choose? (Maximum lines of the dataset: %s)"%(len(self.data_read.columns))))
            if 0 <= lines <= self.data_read.index.size:
                print(self.data_read.head(lines))
            elif lines < 0 or self.data_read.index.size < lines:
                raise ValueError("There are not %s lines in your dataset."%(lines))
            else:
                raise ValueError("Please, insert a number.")
        except ValueError as ve:
            print("Error: %s" % (ve))

    def show_info(self): # Function to show the information of the dataset columns.
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            print(self.data_read.info())
        except ValueError as ve:
            print("Error: %s"%(ve))

    def drop_specific_column(self): # Function to drop a specific columns.
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            
            print("Your data table %s has the following columns:\n%s" % (self.data, list(self.data_read.columns)))
            for i in range(len(list(self.data_read.columns))):
                print("%s. %s" % (i + 1, self.data_read.columns[i]))
            
            val = input("Enter column numbers separated by commas (e.g., 1,3,5) to drop the columns: ")
            indexes = [int(x.strip()) for x in val.split(',')]  # Parse input into a list of integers
            
            # Validate indexes
            if not all(1 <= idx <= len(list(self.data_read.columns)) for idx in indexes):
                raise ValueError("All values must be between 1 and %s." % len(list(self.data_read.columns)))
            
            # Drop specified columns
            columns_to_drop = [list(self.data_read.columns)[idx - 1] for idx in indexes]
            self.data_read.drop(columns=columns_to_drop, axis=1, inplace=True)
            
            print("Columns %s dropped." % columns_to_drop)
        
        except ValueError as ve:
            print("Error: %s" % ve)
        except Exception as e:
            print("An unexpected error occurred: %s" % e)

    def drop_lines(self): # Function to drop lines that fulfill a condition.
        try:
            # Verificar si los datos han sido cargados
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            # Separar columnas numéricas y categóricas
            numeric_columns = self.data_read.select_dtypes(include=['number']).columns.tolist()
            categorical_columns = self.data_read.select_dtypes(include=['object']).columns.tolist()
            # Solicitar elección del tipo de columna
            election = input("Choose if you want to drop numeric or categorical variable column.\n1. Numerical columns.\n2. Categorical columns.\nChoose: ")
            if election == '1':  # Si elige columnas numéricas
                print("Which column do you want to edit?")
                for i, col in enumerate(numeric_columns, start=1):
                    print("%s. %s"%(i,col))
                # Solicitar selección de columna
                col_choice = int(input("Choose a number from 1 to %s: "%(len(numeric_columns))))
                if 1 <= col_choice <= len(numeric_columns):
                    column = numeric_columns[col_choice - 1]
                else:
                    raise ValueError("Invalid column selection.")
                # Elegir cómo eliminar valores
                elimination_choice = input("Choose the elimination way.\n1. Higher values.\n2. Smaller values.\n3. Equal values.\nChoose: ")
                if elimination_choice in ['1', '2', '3']:
                    print("The column values are between (%s, %s)"%(self.data_read[column].min(),self.data_read[column].max()))
                    num_val = float(input("Enter the value: "))  # Convertir a float para evitar errores
                    if self.data_read[column].min() <= num_val <= self.data_read[column].max():
                        if elimination_choice == '1':
                            print("Eliminating values higher than %s."%(num_val))
                            self.data_read = self.data_read[self.data_read[column] <= num_val]
                        elif elimination_choice == '2':
                            print("Eliminating values smaller than %s."%(num_val))
                            self.data_read = self.data_read[self.data_read[column] >= num_val]
                        elif elimination_choice == '3':
                            print("Eliminating values equal to %s."%(num_val))
                            self.data_read = self.data_read[self.data_read[column] != num_val]
                    else:
                        raise ValueError("Invalid value.")
                else:
                    raise ValueError("Invalid elimination choice.")
            elif election == '2':  # Si elige columnas categóricas
                print("Which column do you want to edit?")
                for i, col in enumerate(categorical_columns, start=1):
                    print("%s. %s"%(i,col))
                # Solicitar selección de columna
                col_choice = int(input("Choose a number from 1 to %s: "%(len(categorical_columns))))
                if 1 <= col_choice <= len(categorical_columns):
                    column = categorical_columns[col_choice - 1]
                else:
                    raise ValueError("Invalid column selection.")
                # Mostrar valores únicos y solicitar cuál eliminar
                unique_values = self.data_read[column].unique()
                print("Unique values in the column:")
                for i, val in enumerate(unique_values, start=1):
                    print("%s. %s"%(i,val))
                line_choice = int(input("Choose a number from 1 to %s: "%(len(unique_values))))
                if 1 <= line_choice <= len(unique_values):
                    value_to_remove = unique_values[line_choice - 1]
                    print("Eliminating rows where %s equals %s."%(column,value_to_remove))
                    self.data_read = self.data_read[self.data_read[column] != value_to_remove]
                else:
                    raise ValueError("Invalid value choice.")
            else:
                raise ValueError("Invalid column type selection.")
        except ValueError as ve:
            print("Error: %s."%(ve))
    
    def drop_columns(self):  # Function to drop lines that have a higher amount of empty values that threshold. For correct use, enter a number between 0 and 100
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            percent = self.data_read.isnull().mean() * 100
            print(percent)
            threshold = int(input("Enter the threshold to drop the columns: "))
            if 0 <= threshold <= 100:
                drop_cols = percent[percent > threshold].index
                if len(drop_cols) == 0:
                    print("No columns dropped.")
                else:
                    self.data_read.drop(columns=drop_cols, inplace=True)
                    print("%s columns eliminated, they exceed the %s%% threshold." % (list(drop_cols), threshold))
            elif threshold <= 0 or 100 <= threshold:
                raise ValueError("Threshold should be between 0 and 100.")
            else:
                raise TypeError("Please ensure threshold is a number.")
        except ValueError as ve:
            print("Error: %s" % (ve))
        except TypeError as e:
            print("Error: %s."%(e))

    def impute_empty(self): # Function to impute empty values.
        if self.data_read is None:
            raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
        print("Showing the  empty values of the data table %s."%(self.data))
        print(self.data_read.isna().sum())
        print("How do you want to impute the values?")
        cond1 = input("1. Impute every column at once.\n2. Choose method column by column.\nChoose 1 or 2: ")
        # Separate numerical and categorical imputations
        self.impute_numerical_columns(cond1)
        self.impute_categorical_columns(cond1)
        print("Now the data table %s has the following empty values:"%(self.data))
        print(self.data_read.isna().sum())

    def impute_numerical_columns(self, cond1): # Function to impute numerical columns.
        numerical_columns = self.data_read.select_dtypes(include=[np.number]).columns
        if cond1 == '1':
            cond3 = input("Choose the imputation method for numerical columns.\n1. Mean.\n2. Median.\n3. Interpolation.\n4. Regression.\n5. Leave empty values.\nChoice: ")
            if cond3 == '1':
                print("Imputing numerical values with the mean.")
                self.data_read[numerical_columns] = self.data_read[numerical_columns].fillna(self.data_read[numerical_columns].mean())
            elif cond3 == '2':
                print("Imputing numerical values with the median.")
                self.data_read[numerical_columns] = self.data_read[numerical_columns].fillna(self.data_read[numerical_columns].median())
            elif cond3 == '3':
                print("Imputing numeric values interpolating.")
                self.data_read[numerical_columns] = self.data_read[numerical_columns].interpolate(method='linear')
            elif cond3 == '4':
                print("Imputing numerical values using regression.")
                for column in numerical_columns:
                    self.impute_using_regression(column)
            elif cond3 == '5':
                print("Leaving empty values as is.")
            else:
                raise ValueError("Invalid choice for numerical imputation method.")

        elif cond1 == '2':
            for column in numerical_columns:
                cond3 = input("Choose the imputation method for column %s.\n1. Mean.\n2. Median.\n3. Interpolation.\n4. Regression.\n5. Leave empty values.\nChoice: "%(column))
                if cond3 == '1':
                    self.data_read[column].fillna(self.data_read[column].mean(), inplace=True)
                elif cond3 == '2':
                    self.data_read[column].fillna(self.data_read[column].median(), inplace=True)
                elif cond3 == '3':
                    self.data_read[column].interpolate(method='linear', inplace=True)
                elif cond3 == '4':
                    self.impute_using_regression(column)
                elif cond3 == '5':
                    print("Leaving empty values as is.")
                else:
                    raise ValueError("Invalid imputation method for column %s."%(column))

    def impute_categorical_columns(self, cond1): # Function to impute categorical columns.
        categorical_columns = self.data_read.select_dtypes(include=['object']).columns
        if cond1 == '1':
            cond3 = input("Choose the imputation method for categorical columns.\n1. Mode.\n2. Copy value of above.\n3. Copy value of below.\n4. Predictive Model.\n5. Leave empty values.\nChoice: ")
            if cond3 == '1':
                print("Imputing categorical values with the mode.")
                for column in categorical_columns:
                    mode_value = self.data_read[column].mode()
                    if not mode_value.empty:
                        self.data_read[column].fillna(mode_value[0], inplace=True)
            elif cond3 == '2':
                print("Copying value from above to impute missing values.")
                self.data_read[categorical_columns] = self.data_read[categorical_columns].fillna(method='ffill')
            elif cond3 == '3':
                print("Copying value from below to impute missing values.")
                self.data_read[categorical_columns] = self.data_read[categorical_columns].fillna(method='bfill')
            elif cond3 == '4':
                print("Imputing categorical values using predictive model.")
                for column in categorical_columns:
                    self.impute_using_predictive_model(column)
            elif cond3 == '5':
                print("Leaving empty values as is.")
            else:
                raise ValueError("Invalid choice for categorical imputation method.")

        elif cond1 == '2':
            for column in categorical_columns:
                cond3 = input("Choose the imputation method for column %s.\n1. Mode.\n2. Copy value of above.\n3. Copy value of below.\n4. Predictive Model.\nChoice: "%(column))
                if cond3 == '1':
                    mode_value = self.data_read[column].mode()
                    if not mode_value.empty:
                        self.data_read[column].fillna(mode_value[0], inplace=True)
                elif cond3 == '2':
                    self.data_read[column].fillna(method='ffill', inplace=True)
                elif cond3 == '3':
                    self.data_read[column].fillna(method='bfill', inplace=True)
                elif cond3 == '4':
                    self.impute_using_predictive_model(column)
                else:
                    raise ValueError("Invalid imputation method for column %s."%(column))

    def impute_using_regression(self, column): # Function to make a regression.
        # Check if there are missing values to impute
        if self.data_read[column].isnull().sum() > 0:
            # Separate rows where the column is not null
            complete_data = self.data_read.dropna(subset=[column])
            X = complete_data.drop(columns=[column])
            y = complete_data[column]
            
            # Ensure all features in X are numeric
            X = X.apply(pd.to_numeric, errors='coerce').fillna(0)
            y = pd.to_numeric(y, errors='coerce')  # Ensure y is numeric

            # Train Linear Regression model
            model = LinearRegression()
            model.fit(X, y)

            # Predict for missing data
            missing_data = self.data_read[self.data_read[column].isnull()].drop(columns=[column])
            missing_data = missing_data.apply(pd.to_numeric, errors='coerce').fillna(0)

            # Assign predictions
            self.data_read.loc[self.data_read[column].isnull(), column] = model.predict(missing_data)

    def impute_using_predictive_model(self, column): # Function that predicts a categorical value using Random Forest.
        # Predictive imputation for categorical data using Random Forest
        if self.data_read[column].isnull().sum() > 0:
            print("Imputing missing values for column %s using Random Forest model."%(column))

            # Codificar los valores de la columna categórica a valores numéricos
            le = LabelEncoder()

            # Crear una copia temporal de la columna codificada
            encoded_column = le.fit_transform(self.data_read[column].astype(str))

            # Dividir datos en faltantes y no faltantes
            datos_completos = self.data_read.loc[self.data_read[column].notna()]
            datos_faltantes = self.data_read.loc[self.data_read[column].isna()]

            # Separar las características y la variable objetivo
            X_train = datos_completos.drop(columns=[column])
            y_train = encoded_column[self.data_read[column].notna()]

            # Asegurarse de que todas las características sean numéricas
            X_train = X_train.apply(pd.to_numeric, errors='coerce').fillna(0)  # Convertir a numérico y manejar valores faltantes

            # Entrenar el modelo RandomForest
            modelo = RandomForestClassifier()
            modelo.fit(X_train, y_train)

            # Predecir los valores faltantes
            X_test = datos_faltantes.drop(columns=[column])
            X_test = X_test.apply(pd.to_numeric, errors='coerce').fillna(0)  # Asegurarse de que también sea numérico

            # Realizar predicciones
            predicciones = modelo.predict(X_test)

            # Convertir las predicciones de nuevo a las categorías originales
            self.data_read.loc[datos_faltantes.index, column] = le.inverse_transform(predicciones)

    def plot_data(self):  # Function to plot data.
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            # Set global font style to Cambria
            plt.rcParams['font.family'] = 'Cambria'
            sns.set(font="Cambria")
            # Separate numeric and categorical columns
            numeric_columns = self.data_read.select_dtypes(include=['number']).columns.tolist()
            categorical_columns = self.data_read.select_dtypes(include=['object']).columns.tolist()
            # Ask the user to select the plot type
            print("Select the type of plot:")
            print("1. Line plot")
            print("2. Histogram")
            print("3. Scatter plot")
            print("4. Box plot")
            print("5. Heatmap of missing values")
            print("6. Bar plot")
            plot_choice = int(input("Enter your choice (1-6): "))
            def adjust_yaxis(ax):
                """Adjusts the Y-axis to have ticks at intervals of 20."""
                ax.yaxis.set_major_locator(MultipleLocator(20))
                plt.setp(ax.get_yticklabels(), rotation=45, horizontalalignment='right')
            # Plotting based on user choice
            if plot_choice in [1, 2, 4]:  # These require numeric columns
                print("Select a numeric column for the plot:")
                for i, col in enumerate(numeric_columns, start=1):
                    print("%s. %s" % (i, col))
                col_choice = int(input("Choose a number from 1 to %s: " % (len(numeric_columns))))
                if 1 <= col_choice <= len(numeric_columns):
                    column_name = numeric_columns[col_choice - 1]
                else:
                    raise ValueError("Invalid column selection.")
                print("Column '%s' selected." % (column_name))
                # Create a figure and axis explicitly for Seaborn
                fig, ax = plt.subplots(figsize=(10, 6))
                if plot_choice == 1:  # Line plot
                    self.data_read[column_name].plot(kind='line', title="Line Plot of %s" % (column_name), ax=ax)
                elif plot_choice == 2:  # Histogram
                    self.data_read[column_name].plot(kind='hist', title="Histogram of %s" % (column_name), ax=ax)
                elif plot_choice == 4:  # Box plot
                    sns.boxplot(data=self.data_read, y=column_name, ax=ax)
                    ax.set_title("Box Plot of %s" % (column_name))
                adjust_yaxis(ax)
            elif plot_choice == 3:  # Scatter plot requires two numeric columns
                print("Select a numeric column for the X-axis:")
                for i, col in enumerate(numeric_columns, start=1):
                    print("%s. %s" % (i, col))
                col_choice_x = int(input("Choose a number from 1 to %s: " % (len(numeric_columns))))
                if 1 <= col_choice_x <= len(numeric_columns):
                    column_x = numeric_columns[col_choice_x - 1]
                else:
                    raise ValueError("Invalid column selection.")
                print("Column '%s' selected for X-axis." % (column_x))
                print("Select a numeric column for the Y-axis:")
                for i, col in enumerate(numeric_columns, start=1):
                    print("%s. %s" % (i, col))
                col_choice_y = int(input("Choose a number from 1 to %s: " % (len(numeric_columns))))
                if 1 <= col_choice_y <= len(numeric_columns):
                    column_y = numeric_columns[col_choice_y - 1]
                else:
                    raise ValueError("Invalid column selection.")
                print("Column '%s' selected for Y-axis." % (column_y))
                # Create a figure and axis explicitly for Seaborn
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.scatterplot(data=self.data_read, x=column_x, y=column_y, ax=ax)
                ax.set_title("Scatter Plot of %s vs %s" % (column_x, column_y))
                adjust_yaxis(ax)
            elif plot_choice == 6:  # Bar plot
                print("Select a categorical column for the X-axis:")
                for i, col in enumerate(categorical_columns, start=1):
                    print("%s. %s" % (i, col))
                col_choice_x = int(input("Choose a number from 1 to %s: " % (len(categorical_columns))))
                if 1 <= col_choice_x <= len(categorical_columns):
                    column_x = categorical_columns[col_choice_x - 1]
                else:
                    raise ValueError("Invalid column selection.")
                print("Column '%s' selected for X-axis." % (column_x))
                print("Select a numeric column for the Y-axis:")
                for i, col in enumerate(numeric_columns, start=1):
                    print("%s. %s" % (i, col))
                col_choice_y = int(input("Choose a number from 1 to %s: " % (len(numeric_columns))))
                if 1 <= col_choice_y <= len(numeric_columns):
                    column_y = numeric_columns[col_choice_y - 1]
                else:
                    raise ValueError("Invalid column selection.")
                print("Column '%s' selected for Y-axis." % (column_y))
                # Create a figure and axis explicitly for Seaborn
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.barplot(x=column_x, y=column_y, data=self.data_read, hue=column_x, palette='Set2', ax=ax)
                ax.set_title("Bar Plot Differentiated by Categorical Column")
                adjust_yaxis(ax)
            elif plot_choice == 5:  # Heatmap of missing values
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.heatmap(self.data_read.isnull(), cbar=False, cmap="viridis", ax=ax)
                ax.set_title("Heatmap of Missing Values")
                plt.show()
            else:
                raise ValueError("Invalid plot choice.")
            plt.tight_layout()
            plt.show()
            # Save the plot
            save_choice = input("Do you want to save this plot? (Y/N): ").strip().upper()
            if save_choice == 'Y':
                filename = input("Enter the filename (without extension): ")
                file_path = os.path.join(os.getcwd(), "%s.png" % filename)
                # Save the explicit figure (fig) instead of plt
                fig.savefig(file_path)  # Save the current figure
                print("Plot saved at: %s" % file_path)
            else:
                print("Plot not saved.")
        except ValueError as ve:
            print("Error: %s" % (ve))
        except Exception as e:
            print("An unexpected error occurred: %s" % (e))
    
    def tidy_categorical_columns(self): # Function to tidy categorical values.
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            categorical_columns = self.data_read.select_dtypes(include=['object']).columns.tolist()
            for i in categorical_columns:
                self.data_read[i] = self.data_read[i].str.lower().str.strip()
            print("Categorical columns tidied.")
        except ValueError as ve:
            print("Error: %s"%(ve))
    
    def show_unique(self): # Function to show unique values.
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")
            print("Showing unique values of categorical columns and percentiles of numerical columns.")
            for i in range(len(list(self.data_read.columns))):
                print("%s. %s" % (i + 1, self.data_read.columns[i]))
            
            val = int(input("Enter column number: "))
            if val <= len(list(self.data_read.columns)):
                if self.data_read.dtypes[self.data_read.columns[val]]=="object":
                    print(self.data_read[self.data_read.columns[val]].unique())
                elif self.data_read.dtypes[self.data_read.columns[val]] in ["float64", "int64"]:
                    print("First quantile: %s"%(self.data_read[self.data_read.columns[val]].quantile(0)))
                    print("Second quantile: %s"%(self.data_read[self.data_read.columns[val]].quantile(0.25)))
                    print("Third quantile (Median): %s"%(self.data_read[self.data_read.columns[val]].quantile(0.5)))
                    print("Fourth quantile: %s"%(self.data_read[self.data_read.columns[val]].quantile(0.75)))
                    print("Fifth quantile: %s"%(self.data_read[self.data_read.columns[val]].quantile(1)))
        except ValueError as ve:
            print("Error: %s"%(ve))
    
    def eliminate_outliers(self):
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please call 'read_table()' method first.")            
            print("Program to eliminate outliers from numerical variable columns.")
            print("Your dataset has the following numeric columns.")
            numeric_columns = self.data_read.select_dtypes(include=['number']).columns.tolist()
            for i, col in enumerate(numeric_columns):
                print("%s. %s"%(i+1,col))
            col_idx = int(input("Which column do you want to eliminate outliers from?\n"))            
            if 1 <= col_idx <= len(numeric_columns):
                col = numeric_columns[col_idx - 1]  # Adjusted index
                print("The column '%s' has the following quantiles:"%(col))
                # Handle NaN values
                column_data = self.data_read[col].dropna()                
                # Calculate Q1, Q3, and IQR
                Q1 = np.percentile(column_data, 25)
                Q3 = np.percentile(column_data, 75)
                IQR = Q3 - Q1                
                # Calculate bounds
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                print("Lower bound: %s"%(lower_bound))
                print("First quantile: %s"%(Q1))
                print("Second quantile (Median): %s"%(np.percentile(column_data, 50)))
                print("Third quantile: %s"%(Q3))
                print("Upper bound: %s"%(upper_bound))                
                # Identify outliers
                below_bound = self.data_read[self.data_read[col] < lower_bound]
                above_bound = self.data_read[self.data_read[col] > upper_bound]                
                print("Summary of outliers for column '%s':"%(col))
                if not below_bound.empty:
                    print("Number of values below lower bound (%s): {%s}"%(lower_bound,len(below_bound)))
                    print("Below bound values and their deviations:")
                    print(below_bound[col] - lower_bound)
                else:
                    print("No outliers below the lower bound.")                
                if not above_bound.empty:
                    print("Number of values above upper bound (%s): %s"%(upper_bound,len(above_bound)))
                    print("Above bound values and their deviations:")
                    print(above_bound[col] - upper_bound)
                else:
                    print("No outliers above the upper bound.")                
                # Ask user whether to remove outliers
                decision = input("Do you want to remove these outliers? (y/n): ").strip().lower()
                if decision == 'y':
                    self.data_read = self.data_read[(self.data_read[col] >= lower_bound) & (self.data_read[col] <= upper_bound)]
                    print("Outliers removed.")
                else:
                    print("Outliers retained.")
            else:
                raise ValueError("Invalid column selection.")        
        except ValueError as ve:
            print("Error: %s"%(ve))

    def save_dataset(self):
        try:
            if self.data_read is None:
                raise ValueError("Data hasn't been loaded yet. Please load a dataset first.")
            # Determine the file format and save accordingly
            if self.data.endswith('.csv'):
                self.data_read.to_csv(self.data, index=False)
                print("Dataset saved to %s as CSV."%(self.data))
            elif self.data.endswith('.xlsx') or self.data.endswith('.xls'):
                self.data_read.to_excel(self.data, index=False, engine='openpyxl')
                print("Dataset saved to %s as Excel."%(self.data))
            elif self.data.endswith(".xls"):
                self.data_read.to_excel(self.data, index=False, engine='xlrd')
                print("Dataset saved to %s as Excel."%(self.data))
            else:
                raise ValueError("Unsupported file format. Only CSV and Excel files are supported.")
        except ValueError as ve:
            print("Error: %s"%(ve))
        except Exception as e:
            print("An unexpected error occurred while saving the dataset: %s"%(e))