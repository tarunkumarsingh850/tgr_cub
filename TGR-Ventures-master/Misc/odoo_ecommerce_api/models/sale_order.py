import os
import csv
import logging
import json
import xml.etree.ElementTree as ET

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    so_creation_type = fields.Selection(
        [("manual", "Manual"), ("api", "API"), ("xml", "XML"), ("csv", "CSV")],
        string="Sale Order Creation Type",
        default="manual",
        readonly=True,
    )
    is_drop_shipping = fields.Boolean(string="Is Drop Shipping", copy=False, default=False)

    def _check_sale_order_data(self, sale_order_data):
        """
        @private: Check for missing or invalid data
        :param dict data: sale order data
        """

        def _check_data(key, parent_key, parent_of_parent_key=None, line_index=None):
            """
            @private: common function for check data existence or validity
            """
            # FIXME: Condition 2 not correctly working if (value assign to the key = '')
            if parent_of_parent_key and (line_index is not None):
                condition = data[parent_of_parent_key][line_index][parent_key].get(key, False)
                condition_2 = not bool(data[parent_of_parent_key][line_index][parent_key][key]) if condition else False
            elif line_index is not None:
                condition = data[parent_key][line_index].get(key, False)
                condition_2 = not bool(data[parent_key][line_index][key]) if condition else False
            else:
                condition = data[parent_key].get(key, False)
                condition_2 = not bool(data[parent_key][key]) if condition else False
            if condition:
                if condition_2:
                    return f"Invalid {parent_key} {key}"
                else:
                    return False
            else:
                return f"Missing {parent_key} {key}"

        # Check company details
        error = []
        # if data.get('company_details', False):
        #     error.append(_check_data('code', 'company_details'))
        # else:
        #     return {'error': 'Missing company details'}
        # Check customer details
        for data in sale_order_data:
            if data.get("customer_details", False):
                error.append(_check_data("code", "customer_details"))  # code
                error.append(_check_data("address_line_1", "customer_details"))  # address_line_1
                # error.append(_check_data('city', 'customer_details'))  # city
                # error.append(_check_data('zip', 'customer_details'))  # zip
                # error.append(_check_data('country', 'customer_details'))  # country
                error.append(_check_data("email", "customer_details"))  # email
                error.append(_check_data("phone", "customer_details"))  # phone
            else:
                error.append("Missing customer details")
            # Check order details
            if data.get("order_details", False):
                i = 0
                for line in data["order_details"]:
                    error.append(_check_data("product_details", "order_details", line_index=i))  # product details
                    error.append(
                        _check_data("code", "product_details", parent_of_parent_key="order_details", line_index=i)
                    )  # product details > code
                    # error.append(_check_data('name', 'product_details', parent_of_parent_key='order_details', line_index=i))  # product details > name
                    # error.append(_check_data('product_type', 'product_details', parent_of_parent_key='order_details', line_index=i))  # product details > product_type
                    # error.append(_check_data('sale_price', 'product_details', parent_of_parent_key='order_details', line_index=i))  # product details > sale_price
                    # error.append(_check_data('product_category', 'product_details', parent_of_parent_key='order_details', line_index=i))  # product details > product_category
                    # error.append(_check_data('currency', 'order_details', line_index=i))  # currency
                    error.append(_check_data("quantity", "order_details", line_index=i))  # quantity
                    error.append(_check_data("unit_price", "order_details", line_index=i))  # unit_price
                    i += 1
            else:
                error.append("Missing order details")
        error = ", ".join([x for x in error if bool(x)])
        return {"error": error if bool(error) else False, "status": 400}

    def _get_ecommerce_customer(self, customer_data, partner_id):
        """
        @private - get e-commerce customer from the
        odoo system, otherwise create new customer with the partner code
        """
        # customer_id = self.env['res.partner'].search([('customer_code', '=', customer_data['code']), ('type', '=', 'invoice'), ('parent_id', '=', partner_id.id)])
        # if len(customer_id) > 1:
        #     return {'error': 'Multiple customers found with same partner code in odoo system', 'status': 400}
        # elif len(customer_id) == 1:
        #     return customer_id
        # elif not customer_id:
        try:
            ecom_partner = self.env["res.partner"].search(
                [("parent_id", "=", partner_id.id), ("email", "=", customer_data["email"])], limit=1
            )
            if ecom_partner:
                return ecom_partner
            else:
                return self.env["res.partner"].create(
                    {
                        "name": customer_data.get("name", False),
                        "parent_id": partner_id.id,
                        "type": "delivery",
                        "street": customer_data["address_line_1"],
                        "street2": customer_data.get("address_line_2", False),
                        "city": customer_data.get("city", False),
                        "state_id": self.env["res.country.state"]
                        .search([("code", "=", customer_data.get("state", False))], limit=1)
                        .id,
                        "country_id": self.env["res.country"]
                        .search([("code", "=", customer_data.get("country", False))], limit=1)
                        .id,
                        "zip": customer_data.get("zip", False),
                        "email": customer_data["email"],
                        "phone": customer_data["phone"],
                        "mobile": customer_data.get("mobile", False),
                    }
                )
        except Exception as e:
            return {"error": e, "status": 400}
        # else:
        # return {'error': 'Unknown error occurred when finding partner in odoo system', 'status': 400}

    def _check_partner(self, partner_data, company_data):
        """
        @private - Find a partner assigned with the odoo system, otherwise raise an error
        """
        partner_id = self.env["res.partner"].search([("customer_code", "=", str(company_data["code"]))])
        if not partner_id:
            return {"error": "Partner code invalid, Relevant partner not found in the odoo system", "status": 400}
        elif len(partner_id) > 1:
            return {"error": "Multiple partners found with the same partner code in the odoo system", "status": 400}
        elif len(partner_id) == 1:
            return partner_id
        else:
            return {"error": "Unknown error occurred when finding a partner inside the odoo system", "status": 400}

    def _get_product(self, product_details):
        """
        @private - Get or create the relevant product
        """
        product_id = self.env["product.product"].search([("default_code", "=", product_details["code"])])
        if len(product_id) > 1:
            return {
                "error": f"Multiple products found with the Internal reference - {product_details['code']}",
                "status": 400,
            }
        elif not product_id:
            try:
                return self.env["product.product"].create(
                    {
                        "name": product_details.get("name", product_details["code"]) or product_details["code"],
                        "type": "product",
                        "default_code": product_details["code"],
                        "list_price": product_details.get("sale_price", 0.00),
                    }
                )
            except Exception as e:
                return {"error": e, "status": 400}
        elif len(product_id) == 1:
            return product_id
        else:
            return {"error": f"Unknown error occurred when finding product for code - {product_details['code']}"}

    def _prepare_order_lines(self, order_details):
        """
        @private - prepare data for sale order lines from order_details
        """
        data = []
        for line in order_details:
            product_id = self._get_product(line["product_details"])
            if "error" in product_id:
                data = product_id
                break
            data.append(
                (
                    0,
                    0,
                    {
                        "name": product_id.display_name,
                        "product_id": product_id.id,
                        "product_uom_qty": line["quantity"],
                        "product_uom": product_id.uom_id.id,
                        "price_unit": line["unit_price"],
                    },
                )
            )
        return data

    def get_order_company_id(self, customer_details, partner):
        """
        @private: check there is a default generic
        sale order creation company available
        """
        dropshipping_code = customer_details.get("warehouse_code", "")
        warehouse = self.env["stock.warehouse"].search([("dropshipping_code", "=", dropshipping_code)])
        if not warehouse:
            return {"error": f"Warehouse with dropshipping code {dropshipping_code} not found.", "status": 400}
        if warehouse not in partner.warehouse_ids:
            return {"error": f"Company {warehouse.company_id.name} not available for {partner.name}", "status": 400}
        company_id = warehouse.company_id
        return company_id

    def _prepare_sale_order_data(self, so_data, so_creation_type):
        """
        @private: Prepare sale order data from the file inside the folder or data coming from the api
        """
        data_status = self._check_sale_order_data(so_data)
        if bool(data_status["error"]):
            return data_status
        else:
            try:
                sale_order_data = []
                for data in so_data:
                    partner_id = self._check_partner(data["customer_details"], data["company_details"])
                    if "error" in partner_id:
                        return partner_id
                    customer_id = self._get_ecommerce_customer(data["customer_details"], partner_id)
                    if "error" in customer_id:
                        return customer_id
                    order_line = self._prepare_order_lines(data["order_details"])
                    if "error" in order_line:
                        return order_line
                    company_id = self.get_order_company_id(data["customer_details"], partner_id)
                    if "error" in company_id:
                        return company_id
                    warehouse = self.env["stock.warehouse"].search(
                        [("dropshipping_code", "=", data["customer_details"].get("warehouse_code", ""))]
                    )
                    sale_order_data.append(
                        {
                            "partner_id": partner_id.id,
                            "partner_invoice_id": customer_id.id,
                            "partner_shipping_id": customer_id.id,
                            "order_line": self._prepare_order_lines(data["order_details"]),
                            "company_id": company_id.id,
                            "so_creation_type": so_creation_type,
                            "is_drop_shipping": True,
                            "auto_workflow_process_id": self.env["sale.workflow.process.ept"]
                            .search(
                                [("is_drop_shipping_workflow_new", "=", True), ("company_id", "=", company_id.id)],
                                limit=1,
                            )
                            .id,
                            "origin": data.get("order_reference", False),
                            "warehouse_id": warehouse.id,
                        }
                    )
            except Exception as e:
                return {"error": e, "status": 400}
        return sale_order_data

    def create_ecommerce_sale_order(self, data, so_creation_type="api", file_name=False):
        """
        Create the sale order from the data
        """
        if type(data) is not list:
            data = [data]
        sale_order_data = self._prepare_sale_order_data(data, so_creation_type)
        sale_order_ids = False
        if "error" in sale_order_data:
            response = sale_order_data
        else:
            try:
                sale_order_ids = self.create(sale_order_data)
                for sale_order_id in sale_order_ids:
                    if sale_order_id.partner_id.ref:
                        new_name = f"{sale_order_id.partner_id.ref}{sale_order_id.name}"
                        sale_order_id.write({"name": new_name})
                    if sale_order_id.auto_workflow_process_id:
                        sale_order_id.process_orders_and_invoices_ept()  # Calling auto workflow action
                    else:
                        sale_order_id.action_confirm()  # Otherwise run normal confirmation
                    if sale_order_id.picking_ids:
                        for picking_id in sale_order_id.picking_ids:
                            picking_id.is_drop_shipping = (
                                sale_order_id.is_drop_shipping and sale_order_id.is_drop_shipping or False
                            )
                created_sale_orders = ", ".join(sale_order_ids.mapped("name"))
                self.create_invoice_record(sale_order_id)
                response = {
                    "success": True,
                    "order_reference": created_sale_orders,
                    "message": f"Sale order {created_sale_orders} created successfully",
                    "status": 200,
                }
            except Exception as e:
                response = {"error": e, "status": 400}
        _logger.info(response)
        self.env["ecommerce.api.log"].create_log(data, response, sale_order_ids, so_creation_type, file_name)
        return response

    def get_shipment_tracking_data(self, data):
        order = self.env["sale.order"].search([("name", "=", data.get("order_number"))])
        if not order:
            return {"error": f"Order {data.get('order_number')} not doesn't exist.", "status": 400}
        data = {
            "order_number": order.picking_ids[0].name,
            "shipment_carrier": order.picking_ids[0].carrier_id.name,
            "shipment_number": order.picking_ids[0].carrier_tracking_ref,
        }
        return json.dumps(data)

    # ================================Schedule Action Related Functions===================================
    def _create_json_from_xml(self, filepath):
        """
        @private: Check the folder path and create the json file from the xml file
        """
        tree = ET.parse(filepath)
        root = tree.getroot()
        data = {}
        try:
            # for company in root.findall('companyDetails'):
            #     data.update({
            #         "company_details": {
            #             "code": company.find('code').text,
            #             "name": company.find('name').text
            #         }
            #     })
            for reference in root.findall("orderReference"):
                data.update({"order_reference": reference.text})
            for customer in root.findall("customerDetails"):
                data.update(
                    {
                        "customer_details": {
                            "code": customer.find("code").text,
                            "name": customer.find("name").text,
                            "address_line_1": customer.find("addressLine1").text,
                            "address_line_2": customer.find("addressLine2").text,
                            "city": customer.find("city").text,
                            "state": customer.find("state").text,
                            "zip": customer.find("zip").text,
                            "country": customer.find("country").text,
                            "email": customer.find("email").text,
                            "phone": customer.find("phone").text,
                            "mobile": customer.find("mobile").text,
                            "warehouse_code": customer.find("warehouse_code").text,
                        }
                    }
                )
            for detail in root.findall("orderDetails"):
                data.update({"order_details": []})
                for line in detail.findall("orderLine"):
                    line_data = {}
                    for product in line.findall("productDetails"):
                        line_data.update(
                            {
                                "product_details": {
                                    "code": product.find("code").text,
                                    "name": product.find("name").text,
                                    "product_type": product.find("productType").text,
                                    "sale_price": product.find("salePrice").text,
                                    "product_category": product.find("productCategory").text,
                                }
                            }
                        )
                    line_data.update(
                        {
                            "currency": line.find("currency").text,
                            "quantity": line.find("quantity").text,
                            "unit_price": line.find("unitPrice").text,
                            "taxes": line.find("taxes").text,
                        }
                    )
                    data["order_details"].append(line_data)
            existing_sale_orders = self.env["sale.order"].search(
                [("origin", "!=", False), ("origin", "=", data.get("order_reference", False))]
            )
            if len(existing_sale_orders) > 0:
                reference_numbers = ", ".join(existing_sale_orders.mapped("origin"))
                existing_sale_orders = ", ".join(existing_sale_orders.mapped("name"))
                return {
                    "error": f"[XML]Sale orders exist with same reference number {existing_sale_orders} | {reference_numbers}",
                    "status": 400,
                }
        except Exception as e:
            return {"error": e, "status": 400}
        return data

    def _create_json_from_csv(self, filepath):
        """
        @private - Create json object from the csv file
        """
        try:
            data = []
            with open(filepath, "r") as file:
                csvreader = csv.DictReader(file, delimiter=",")
                i = 0
                for row in csvreader:
                    if row["customer_details/code"] != "":
                        order_data = {
                            "order_reference": row["order_reference"],
                            "customer_details": {
                                "code": row["customer_details/code"],
                                "address_line_1": row["customer_details/address_line_1"],
                                "email": row["customer_details/email"],
                                "phone": row["customer_details/phone"],
                                "warehouse_code": row["customer_details/warehouse_code"],
                            },
                            "order_details": [
                                {
                                    "product_details": {"code": row["order_details/product_details/code"]},
                                    "quantity": row["order_details/quantity"],
                                    "unit_price": row["order_details/unit_price"],
                                }
                            ],
                        }
                        data.append(order_data)
                    else:
                        data[-1]["order_details"].append(
                            {
                                "product_details": {"code": row["order_details/product_details/code"]},
                                "quantity": row["order_details/quantity"],
                                "unit_price": row["order_details/unit_price"],
                            }
                        )
                    i += 1
            data = [
                x
                for x in data
                if self.env["sale.order"].search_count([("origin", "!=", False), ("origin", "=", x["order_reference"])])
                == 0
            ]  # Check sale order existence
            if not data:
                data = {"error": "[CSV]No valid data exist", "error_code": 400}
        except Exception as e:
            data = {"error": f"File format is not compatible ({e})", "error_code": 400}
        return data

    def cron_create_sale_orders(self):
        """
        @private - Create the sale order from xml file
        """
        try:
            folder_path = self.env["ir.config_parameter"].sudo().get_param("odoo_ecommerce_api.files_folder_path")
            files = [x for x in os.listdir(folder_path) if (x.endswith(".xml") or x.endswith(".csv"))]
            for filename in files:
                filepath = os.path.join(folder_path, filename)
                if filename.endswith(".xml"):
                    data = self._create_json_from_xml(filepath)
                    so_creation_type = "xml"
                elif filename.endswith(".csv"):
                    data = self._create_json_from_csv(filepath)
                    so_creation_type = "csv"
                else:
                    data = {"error": f"Invalid file {filename}", "error_code": 400}
                    so_creation_type = "normal"
                if "error" in data:
                    _logger.info(data)
                    self.env["ecommerce.api.log"].sudo().create_log(
                        data=False,
                        response=data,
                        sale_order_ids=False,
                        so_creation_type=so_creation_type,
                        file_name=filename,
                    )
                else:
                    sale_order_status = self.sudo().create_ecommerce_sale_order(
                        data, so_creation_type=so_creation_type, file_name=filename
                    )
                    if "error" in sale_order_status:
                        _logger.info(sale_order_status)
                        self.env["ecommerce.api.log"].sudo().create_log(
                            data=False,
                            response=sale_order_status,
                            sale_order_ids=False,
                            so_creation_type=so_creation_type,
                            file_name=filename,
                        )
        except Exception as e:
            error = {"error": e, "status": 400}
            _logger.info(error)
            self.env["ecommerce.api.log"].sudo().create_log(
                data=False, response=error, sale_order_ids=False, so_creation_type="", file_name=False
            )

    # ====================================================================================================

    def validate_order_ept(self):
        res = super(SaleOrder, self).validate_order_ept()
        stamps_delivery = self.env["delivery.carrier"].search(
            [
                ("delivery_type", "=", "stamps"),
                ("is_dropshipping_delivery", "=", True),
            ],
            limit=1,
        )
        for order in self.filtered(lambda so: so.is_drop_shipping):
            for picking in order.picking_ids:
                picking.carrier_id = stamps_delivery.id if stamps_delivery else False
        return res

    def create_invoice_record(self, sale_id):
        for rec in sale_id:
            sku_count = len(rec.order_line.filtered(lambda line: line.product_id.detailed_type == "product"))
            picking_packing_cost = rec.company_id.dropshipping_picking_packing_cost if (sku_count > 0) else 0
            additional_pick_pack = 0
            if sku_count > rec.company_id.dropshipping_min_pick_pack_cost_upto_sku_count:
                additional_pick_pack = sku_count - rec.company_id.dropshipping_min_pick_pack_cost_upto_sku_count
            additional_pick_pack_cost = (
                additional_pick_pack * rec.company_id.dropshipping_additional_picking_packing_cost
            )
            picking_packing_cost += additional_pick_pack_cost

            shipping_cost = rec.company_id.dropshipping_shipping_cost

            if "through_server_action" in self._context:
                invoice_id = rec.with_context(through_server_action_create_invoice=True)._create_invoices()
            else:
                invoice_id = rec.with_context(through_ecommerce_api=True)._create_invoices()
            if invoice_id:
                picking_packing_cost_dic = {
                    # "product_id": line_rec.product_id.id,
                    "name": "Picking/Packing Cost",
                    "quantity": 1,
                    "price_unit": picking_packing_cost and picking_packing_cost or 0.00,
                    "tax_ids": False,
                }
                invoice_id.write({"invoice_line_ids": [(0, 0, picking_packing_cost_dic)]})
                shipping_cost_dic = {
                    # "product_id": line_rec.product_id.id,
                    "name": "Shipping Cost",
                    "quantity": 1,
                    "price_unit": shipping_cost and shipping_cost or 0.00,
                    "tax_ids": False,
                }
                invoice_id.write({"invoice_line_ids": [(0, 0, shipping_cost_dic)]})

    def button_action_create_invoice(self):
        for record in self.browse(self._context["active_ids"]):
            self.with_context(through_server_action=True).create_invoice_record(record)

    def button_action_edit_invoice(self):
        for record in self.browse(self._context["active_ids"]):
            self.write_invoice_record(record)

    def write_invoice_record(self, sale_id):
        invoice_line = []
        for rec in sale_id:
            sku_count = len(rec.order_line.filtered(lambda line: line.product_id.detailed_type == "product"))
            picking_packing_cost = rec.company_id.dropshipping_picking_packing_cost if (sku_count > 0) else 0
            additional_pick_pack = 0
            if sku_count > rec.company_id.dropshipping_min_pick_pack_cost_upto_sku_count:
                additional_pick_pack = sku_count - rec.company_id.dropshipping_min_pick_pack_cost_upto_sku_count
            additional_pick_pack_cost = (
                additional_pick_pack * rec.company_id.dropshipping_additional_picking_packing_cost
            )
            picking_packing_cost += additional_pick_pack_cost

            shipping_cost = rec.company_id.dropshipping_shipping_cost
            
            invoice_id = rec.invoice_ids.filtered(lambda i : i.state == 'draft')
            if invoice_id:
                invoice_id = invoice_id[0]
                invoice_id.invoice_line_ids = False
                for line in rec.order_line:
                    invoice_line_dict = {
                            "product_id": line.product_id.id,
                            "price_unit": line.set_price_unit(),
                            "name": line.product_id.name,
                            "quantity": line.product_uom_qty,
                            "product_uom_id": line.product_id.uom_id.id,
                            "tax_ids": [(6,0,line.tax_id.ids)] if line.tax_id else False,
                            "move_id": invoice_id.id,

                    }
                    invoice_line.append((0,0,invoice_line_dict))
                invoice_id.write({"invoice_line_ids": invoice_line})
                if invoice_id:
                    picking_packing_cost_dic = {
                        # "product_id": line_rec.product_id.id,
                        "name": "Picking/Packing Cost",
                        "quantity": 1,
                        "price_unit": picking_packing_cost and picking_packing_cost or 0.00,
                        "tax_ids": False,
                    }
                    invoice_id.write({"invoice_line_ids": [(0, 0, picking_packing_cost_dic)]})
                    shipping_cost_dic = {
                        # "product_id": line_rec.product_id.id,
                        "name": "Shipping Cost",
                        "quantity": 1,
                        "price_unit": shipping_cost and shipping_cost or 0.00,
                        "tax_ids": False,
                    }
                    invoice_id.write({"invoice_line_ids": [(0, 0, shipping_cost_dic)]})
                for ord_line in rec.order_line:
                    for inv_line in invoice_id.invoice_line_ids:
                        if ord_line.product_id.id == inv_line.product_id.id:
                            ord_line.invoice_lines = [(4,inv_line.id)]

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if "through_ecommerce_api" in self._context:
            for line_rec in self:
                unit_price = line_rec.price_unit
                if line_rec.order_id.partner_id.property_product_pricelist:
                    for item_id in line_rec.order_id.partner_id.property_product_pricelist.item_ids.filtered(
                        lambda p: p.product_tmpl_id.id == line_rec.product_id.product_tmpl_id.id
                    ):
                        unit_price = item_id.fixed_price
            res["price_unit"] = unit_price

        if "through_server_action_create_invoice" in self._context:
            for line_rec in self:
                unit_price = line_rec.price_unit
                if line_rec.order_id.pricelist_id:
                    for item_id in line_rec.order_id.pricelist_id.item_ids.filtered(
                        lambda p: p.product_tmpl_id.id == line_rec.product_id.product_tmpl_id.id
                    ):
                        unit_price = item_id.fixed_price
            res["price_unit"] = unit_price
        return res
    


    def set_price_unit(self):
        unit_price = self.price_unit
        if self.order_id.pricelist_id:
            for item_id in self.order_id.pricelist_id.item_ids.filtered(
                lambda p: p.product_tmpl_id.id == self.product_id.product_tmpl_id.id
            ):
                unit_price = item_id.fixed_price
        return unit_price