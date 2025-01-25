import numpy as np
from .TableLoader import TableLoader


class BaseProcessor:
    def __init__(self, table_name, data_catalog):
        """Base class to provide common DataFrame operations."""
        self.table_name = table_name
        self.data_catalog = data_catalog
        
        # Initialize TableLoader with the table_name and data_catalog
        self.table_loader = TableLoader(table_name, data_catalog)
        
        # Now you can access methods and properties from the TableLoader
        self.data = self.table_loader.get_dataframe()
        
        self.rename_column()
        
    def rename_column(self):
        # Renaming columns that contain 'name' to 'NAME'
        self.data.rename(columns={col: 'NAME' if 'name' in col.lower() else col for col in self.data.columns}, inplace=True)

    def handle_nans_and_zeros(self, colName):
        # Calculate the minimum value excluding 0
        min_value = self.data[self.data[colName] != 0][colName].min()

        # Replace NaN and 0 values with the calculated minimum value
        self.data[colName] = self.data[colName].replace({0: min_value, np.nan: min_value})
    
    def get_raw_data(self):
        return self.table_loader.original_dataframe