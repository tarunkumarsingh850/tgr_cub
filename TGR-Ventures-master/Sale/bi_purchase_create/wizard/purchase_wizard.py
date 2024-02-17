from odoo import fields, models


class PurchaseAgreement(models.TransientModel):
    _name = "purchase.wizard"
    _description = "Purchase wizard"

    agreement_line_ids = fields.One2many("purchase.wizard.line", "agreement_id", string="Agreement")
    enquiry_number = fields.Char(string="Enquiry Number")

    def create_pur_agreement(self):
        vendor_list = []
        purchase_list = []
        po_obj = self.env["purchase.order"]
        for rec in self.agreement_line_ids:
            po_order_line = []
            for each in self.agreement_line_ids:
                if rec.vendor_id.id not in vendor_list:
                    if rec.vendor_id.id == each.vendor_id.id:
                        line_value = (
                            0,
                            0,
                            {
                                "product_id": each.product_id.id,
                                "name": each.product_id.name,
                                "product_qty": each.quantity,
                                "product_uom": each.uom_id.id,
                                "price_unit": each.unit_price,
                                "price_subtotal": each.price_subtotal,
                            },
                        )
                        po_order_line.append(line_value)
                        sale_id = each.sale_id
            if rec.vendor_id.id not in vendor_list:
                vendor_list.append(rec.vendor_id.id)
                values = {
                    "partner_id": rec.vendor_id.id,
                    "order_line": po_order_line,
                    "sale_id": sale_id.id,
                }
                purchase_id = po_obj.create(values)
                purchase_list.append(purchase_id.id)
        sale_id.purchase_ids = [(4, x, None) for x in purchase_list]
        return {
            "name": "Purchase Order",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "purchase.order",
            "target": "self",
            "domain": [("id", "in", purchase_list)],
        }


class PurchaseAgreementLIne(models.TransientModel):
    _name = "purchase.wizard.line"

    agreement_id = fields.Many2one(
        "purchase.wizard",
        string="Agreement",
    )
    product_id = fields.Many2one("product.product", string="Product")
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    description_name = fields.Char(string="Name")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price")
    tax_id = fields.Char(string="Taxes")
    uom_id = fields.Many2one("uom.uom", string="Uom")
    price_subtotal = fields.Float(string="Subtotal")
    sale_id = fields.Many2one("sale.order", string="Sale Order")
