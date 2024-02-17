from ..base import ShopifyResource
from .inventory_level import InventoryLevel


class Location(ShopifyResource):
    def inventory_levels(self, **kwargs):
        return InventoryLevel.find(
            from_="{}/locations/{}/inventory_levels.json".format(ShopifyResource.site, self.id), **kwargs
        )
