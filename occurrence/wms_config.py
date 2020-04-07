# ### wms_config.py

# # Load django-wms classes
# from wms import maps, layers, views

# # Load model with spatial field (Point, Polygon, MultiPolygon)
# from occurrence.models import TaxonAreaEncounter, CommunityAreaEncounter

# # Subclass the WmsLayer class and point it to a spatial model
# # use WmsVectorLayer for vector data and WmsRasterLayer for rasters
# class TAEWmsLayer(layers.WmsVectorLayer):
#     model = TaxonAreaEncounter

# class CAEWmsLayer(layers.WmsVectorLayer):
#     model = CommunityAreaEncounter

# # Subclass the WmsMap class and add the layer to it
# class OccWmsMap(maps.WmsMap):
#     layer_classes = [ TAEWmsLayer, CAEWmsLayer ]

# # Subclass the WmsView to create a view for the map
# class OccWmsView(views.WmsView):
#     map_class = OccWmsMap
