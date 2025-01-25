from DataCatalog import DataCatalog, TableInfo


class ExtendedDataCatalog(DataCatalog):
    def __init__(self, aprx=None):
        """Extend the DataCatalog to focus on feature layers and their attribute tables."""
        super().__init__(aprx)  # Call the parent constructor to initialize the base class
        self.feature_layers = self._get_feature_layers_with_attribute_tables()

    def _get_feature_layers_with_attribute_tables(self):
        """Override the method to fetch only feature layers and their attribute tables."""
        
        # List all layers in the map
        for layer in self.map_obj.listLayers():
            if layer.isFeatureLayer:  # Check if it's a feature layer
                # Here, we get the dataSource, which is the feature class or table linked to the layer
                attribute_table = layer.dataSource  # This represents the feature class or table source
                feature_layer_info = TableInfo(
                    name=layer.name,
                    dataSource=layer.dataSource,
                    table_obj=layer.dataSource
                )
                self.tables.append(feature_layer_info)