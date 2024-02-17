from odoo import api, models, _
from odoo.exceptions import UserError

try:
    import barcode

    _lib_imported = True
except ImportError:
    _lib_imported = False
import random


def get_random_number():
    random_num = str(random.randint(1000000000, 99999999999))
    random_first_digit = "256"
    random_str = str(random_first_digit) + "".join(map(str, random_num[:11]))
    return random_str


def generate_ean(barcode_type):
    if not _lib_imported:
        raise UserError(_("python-barcode is not installed. Please install it."))
    EAN = barcode.get_barcode_class(barcode_type)
    ean = EAN(get_random_number())
    return ean.get_fullcode()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def action_generate_barcode(self):
        products = self.env["product.template"].search([("id", "=", self.env.context.get("active_ids"))])
        for product in products:
            if product.barcode:
                continue
            ean = generate_ean("ean13")
            product.barcode = ean


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def action_generate_barcode(self):
        products = self.env["product.product"].search([("id", "=", self.env.context.get("active_ids"))])
        for product in products:
            if product.barcode:
                continue
            ean = generate_ean("ean13")
            product.barcode = ean
