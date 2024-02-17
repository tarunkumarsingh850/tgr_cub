from odoo import http
from odoo.http import request
import json
import xml.etree.ElementTree as ET


class SendStockApi(http.Controller):
    @http.route("/get_stock", type="http", auth="public", methods=["GET"], csrf=False)
    def get_stock(self, **args):
        data = []
        product_ids = (
            request.env["product.template"]
            .sudo()
            .search(
                [
                    ("eu_tiger_one_boolean", "=", True),
                    ("default_code", "not ilike", "FREE-"),
                    ("wholesale_price_value", ">", 0),
                    ("product_breeder_id", "!=", False),
                ]
            )
        )
        location = request.env["stock.location"].sudo()
        uk_location = location.search([("magento_location", "=", "uk_source")])
        eu_location = location.search([("magento_location", "=", "eu_source")])
        for product in product_ids:
            product = request.env["product.product"].sudo().search([("product_tmpl_id", "=", product.id)], limit=1)
            uk_stock = product.with_context(location=uk_location.id).free_qty
            eu_stock = product.with_context(location=eu_location.id).free_qty
            data.append(
                {
                    "SKU": product.default_code,
                    "ESPQty": eu_stock,
                    "GBRQty": uk_stock,
                    "Manufacturer": product.product_tmpl_id.product_breeder_id.breeder_name,
                    "Price": product.product_tmpl_id.wholesale_price_value,
                    "Item Class": product.product_tmpl_id.categ_id.name,
                    "lastmodifiedon": False,
                }
            )
        return json.dumps(data)

    @http.route("/get_stock_xml", type="http", auth="public", methods=["GET"], csrf=False)
    def get_stock_xml(self, **args):
        ET.Element("entry")
        ET.Element("content")
        # product_ids = request.env["product.template"].sudo().search(
        #     [
        #         ('eu_tiger_one_boolean','=',True),
        #         ('default_code','not ilike','FREE-'),
        #         ('wholesale_price_value','>',0),
        #         ('product_breeder_id','!=',False)
        #     ],
        #     limit=1
        # )
        # location = request.env["stock.location"].sudo()
        # uk_location = location.search([("magento_location", "=", "uk_source")])
        # eu_location = location.search([("magento_location", "=", "eu_source")])
        # for product in product_ids:
        #     product = request.env["product.product"].sudo().search([("product_tmpl_id","=",product.id)],limit=1)
        #     uk_stock = product.with_context(location=uk_location.id).free_qty
        #     eu_stock = product.with_context(location=eu_location.id).free_qty
        #     product_data = ET.SubElement(data, "m:properties")
        #     ET.SubElement(product_data, "d:SKU").text = product.default_code
        #     ET.SubElement(product_data, "d:ESPQty").text = str(eu_stock)
        #     ET.SubElement(product_data, "d:GBRQty").text = str(uk_stock)
        #     ET.SubElement(product_data, "d:Manufacturer").text = str(product.product_tmpl_id.product_breeder_id.breeder_name)
        #     ET.SubElement(product_data, "d:Price").text = str(product.product_tmpl_id.wholesale_price_value)
        #     ET.SubElement(product_data, "d:ItemClass").text = str(product.product_tmpl_id.categ_id.name)
        #     ET.SubElement(product_data, "d:lastmodifiedon").text = False
        # return tostring(ET.ElementTree(data).getroot()).decode('UTF-8')
        xml = """
<?xml version="1.0" encoding="utf-8"?>
<feed xml:base="https://backoffice.tgrventures.com/odata/tgr%20live" xmlns="http://www.w3.org/2005/Atom" xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices" xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata" xmlns:georss="http://www.georss.org/georss" xmlns:gml="http://www.opengis.net/gml">
    <id>http://schemas.datacontract.org/2004/07/</id>
    <title />
    <updated>2023-01-30T07:11:09Z</updated>
    <link rel="self" href="https://backoffice.tgrventures.com/odata/tgr%20live/StockPerWarehouse" />
        <title />
        <updated>2023-01-30T07:11:09Z</updated>
        <author>
            <name />
        </author>
        <content type="application/xml">
            <m:properties>
                <d:SKU xml:space="preserve">00S-00CH-AUTO-FEM-05          </d:SKU>
                <d:ESPQty m:type="Edm.Decimal">17.000000</d:ESPQty>
                <d:GBRQty m:type="Edm.Decimal">4.000000</d:GBRQty>
                <d:Manufacturer>00 Seeds</d:Manufacturer>
                <d:Price>9.75</d:Price>
                <d:ItemClass>Seeds THC</d:ItemClass>
                <d:LastModifiedDateTime m:type="Edm.DateTime">2022-12-13T09:19:34.333843</d:LastModifiedDateTime>
            </m:properties>
        </content>
    </entry>
</feed>
"""
        return xml
