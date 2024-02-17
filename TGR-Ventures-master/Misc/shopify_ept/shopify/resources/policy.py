from ..base import ShopifyResource
from .. import mixins


class Policy(ShopifyResource, mixins.Metafields, mixins.Events):
    pass
