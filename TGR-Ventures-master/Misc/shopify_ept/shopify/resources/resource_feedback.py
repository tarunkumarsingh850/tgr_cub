from ..base import ShopifyResource


class ResourceFeedback(ShopifyResource):
    _prefix_source = "/products/$product_id/"
    _plural = "resource_feedback"

    @classmethod
    def _prefix(cls, options={}):
        product_id = options.get("product_id")
        if product_id:
            return "{}/products/{}".format(cls.site, product_id)
        else:
            return cls.site
