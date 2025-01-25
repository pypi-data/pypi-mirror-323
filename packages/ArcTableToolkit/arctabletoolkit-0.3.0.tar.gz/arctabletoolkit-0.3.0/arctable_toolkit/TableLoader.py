import arcpy
import pandas as pd


class TableLoader:
    def __init__(self, table_name, data_catalog):
        """Initializes TableLoader with table_name and DataCatalog instance."""
        self.data_catalog = data_catalog  # Store the DataCatalog instance
        self.table_info = self.data_catalog.get_table_by_name(table_name)

        if self.table_info is None or self.table_info.table_obj is None:
            raise ValueError(f"Table '{table_name}' not found or is invalid.")
        
        # Load the table into a pandas DataFrame
        self.original_dataframe = self._table_to_dataframe()

    def _table_to_dataframe(self):
        """
        Convert the ArcGIS table to a pandas DataFrame using arcpy.da.SearchCursor.

        Returns:
        - A pandas DataFrame containing the table's data.
        """
        # Fetch field names from the ArcGIS table
        field_names = [field.name for field in arcpy.ListFields(self.table_info.table_obj)]

        # Using arcpy.da.SearchCursor to fetch rows
        rows = []
        with arcpy.da.SearchCursor(self.table_info.table_obj, field_names) as cursor:
            for row in cursor:
                rows.append(row)

        # Convert the rows to a pandas DataFrame
        df = pd.DataFrame(rows, columns=field_names)
        
        return df

    def get_dataframe(self):
        """Returns a copy of the original DataFrame."""
        return self.original_dataframe.copy()