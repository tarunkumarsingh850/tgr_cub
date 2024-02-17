# See LICENSE file for full copyright and licensing details.
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def create_sale_order_line_ept(self, vals):
        """
        Required data in dictionary :- order_id, name, product_id.
        Migration done by Haresh Mori on September 2021
        """
        sale_order_line = self.env["sale.order.line"]
        order_line = {
            "order_id": vals.get("order_id", False),
            "product_id": vals.get("product_id", False),
            "company_id": vals.get("company_id", False),
            "name": vals.get("description", ""),
            "product_uom": vals.get("product_uom"),
        }

        new_order_line = sale_order_line.new(order_line)
        new_order_line.product_id_change()
        order_line = sale_order_line._convert_to_write({name: new_order_line[name] for name in new_order_line._cache})

        order_line.update(
            {
                "order_id": vals.get("order_id", False),
                "product_uom_qty": vals.get("order_qty", 0.0),
                "price_unit": vals.get("price_unit", 0.0),
                "discount": vals.get("discount", 0.0),
                "tax_id": vals.get("tax_id", []),
                "state": "draft",
            }
        )
        return order_line

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        product_id = self.env["product.product"].search([("id", "=", res["product_id"])])
        if self.order_id.magento_website_id.income_account_id and product_id.detailed_type == "product":
            res["account_id"] = self.order_id.magento_website_id.income_account_id.id
        elif product_id.default_code == "MAGENTO DISCOUNT" and self.order_id.magento_website_id.income_account_id:
            res["account_id"] = self.order_id.magento_website_id.income_account_id.id
        elif product_id.default_code == "MAGENTO_SHIP" and self.order_id.magento_website_id.shipment_account_id:
            res["account_id"] = self.order_id.magento_website_id.shipment_account_id.id
        elif (
            self.order_id.magento_website_id.delivery_isurance_account_id
            and product_id.default_code == "DeliveryIsurance"
        ):
            res["account_id"] = self.order_id.magento_website_id.delivery_isurance_account_id.id
        elif self.order_id.shopify_instance_id.income_account_id and product_id.detailed_type == "product":
            res["account_id"] = self.order_id.shopify_instance_id.income_account_id.id
        elif product_id.default_code == "Store Credit":
            res["account_id"] = self.order_id.magento_website_id.income_account_id.id
        return res
