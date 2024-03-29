from ..base import ShopifyResource


class Metafield(ShopifyResource):
    _prefix_source = "/$resource/$resource_id/"

    @classmethod
    def _prefix(cls, options={}):
        resource = options.get("resource")
        if resource:
            return "{}/{}/{}".format(cls.site, resource, options["resource_id"])
        else:
            return cls.site
