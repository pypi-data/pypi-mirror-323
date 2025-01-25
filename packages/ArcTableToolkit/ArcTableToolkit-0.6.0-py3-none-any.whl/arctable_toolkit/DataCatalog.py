import arcpy

from collections import namedtuple


# Define a namedtuple for table information
TableInfo = namedtuple('TableInfo', ['name', 'dataSource', 'table_obj'])

class DataCatalog:
    def __init__(self, aprx=None):
        """Initialize the DataCatalog with all tables from the current ArcGIS project."""
        if aprx is None:
            aprx = arcpy.mp.ArcGISProject("CURRENT")  # Use current ArcGIS project if none is provided
        
        # Get the first map in the project (you can change this if you want to specify a different map)
        self.map_obj = aprx.listMaps()[0]
        
        # Initialize the list of tables
        self.tables = self._get_all_tables()
    
    def _get_all_tables(self):
        """Retrieve all tables from the specified map object."""
        tables = []
        
        # List all tables in the specific map
        map_tables = self.map_obj.listTables()
        for table in map_tables:
            table_info = TableInfo(
                name=table.name,
                dataSource=table.dataSource,
                table_obj=table
            )
            tables.append(table_info)
        
        return tables

    def get_table_by_name(self, table_name):
        """Return the TableInfo object for a specific table by name."""
        # Find the table by name
        table_info = next((t for t in self.tables if t.name == table_name), None)
        if table_info:
            return table_info
        else:
            raise ValueError(f"Table '{table_name}' not found in the catalog.")
    
    def get_table_names(self):
        """Return a list of all table names in the catalog."""
        return [table.name for table in self.tables]
    
    def display_tables(self):
        """Display a summary of all tables in the catalog."""
        for table in self.tables:
            print(f"Table: {table.name}, DataSource: {table.dataSource}")