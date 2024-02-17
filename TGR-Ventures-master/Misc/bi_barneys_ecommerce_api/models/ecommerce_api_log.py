from odoo import fields, models


class EcommerceApiLog(models.Model):
    _inherit = "ecommerce.api.log"

    is_barneys = fields.Boolean("Is Barneys")

    def create_log(self, data, response, sale_order_ids, so_creation_type, file_name, is_barneys=False):
        """
        Create log with the response
        """
        state = "success" if ("success" in response) else "failed"
        self.create(
            {
                "state": state,
                "status_message": response,
                "body": data,
                "sale_order_ids": [(4, x.id) for x in sale_order_ids] if sale_order_ids else False,
                "type": so_creation_type,
                "file_name": file_name,
                "is_barneys": is_barneys,
            }
        )
