# See LICENSE file for full copyright and licensing details.
from odoo import models


class DataQueueMixinEpt(models.AbstractModel):
    """Mixin class for delete unused data queue from database."""

    _inherit = "data.queue.mixin.ept"

    def delete_data_queue_ept(self, queue_data=False, is_delete_queue=False):
        """
        This method will delete data queues from database.
        """
        if not queue_data:
            queue_data = []
        queue_data += [
            "sync_import_magento_product_queue",
            "magento_order_data_queue_ept",
            "magento_customer_data_queue_ept",
        ]
        return super(DataQueueMixinEpt, self).delete_data_queue_ept(queue_data, is_delete_queue)
