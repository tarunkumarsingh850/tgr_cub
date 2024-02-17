# See LICENSE file for full copyright and licensing details.
"""
Describes methods for sync/ Import product queues.
"""
import math
import logging
import time
import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from .api_request import req, create_search_criteria
from ..python_library.php import Php
from datetime import datetime, time

_logger = logging.getLogger("MagentoProductQueue")


class MagentoProductQueue(models.Model):
    """
    Describes sync/ Import product queues.
    """

    _name = "sync.import.magento.product.queue"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Sync/ Import Product Queue"

    name = fields.Char(help="Sequential name of imported/ Synced products.", copy=False)
    instance_id = fields.Many2one(
        comodel_name="magento.instance",
        string="Instance",
        help="Product imported from or Synced to this Magento Instance.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("partially_completed", "Partially Completed"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="draft",
        copy=False,
        help="Status of Order Data Queue",
        compute="_compute_queue_state",
        store=True,
    )
    log_book_id = fields.Many2one(
        comodel_name="common.log.book.ept", help="Related Log book which has all logs for current queue."
    )
    log_lines_ids = fields.One2many(
        related="log_book_id.log_lines", help="Log lines of Common log book for particular product " "queue"
    )
    line_ids = fields.One2many("sync.import.magento.product.queue.line", "queue_id", help="Queue Lines")
    total_count = fields.Integer(
        string="Total Records", compute="_compute_record", help="Returns total number of Import product queue lines"
    )
    draft_count = fields.Integer(
        string="Draft Records",
        compute="_compute_record",
        help="Returns total number of draft Import product queue lines",
    )
    failed_count = fields.Integer(
        string="Fail Records",
        compute="_compute_record",
        help="Returns total number of Failed Import product queue lines",
    )
    done_count = fields.Integer(
        string="Done Records", compute="_compute_record", help="Returns total number of done Import product queue lines"
    )
    cancel_count = fields.Integer(
        string="Cancel Records",
        compute="_compute_record",
        help="Returns total number of cancel Import product queue lines",
    )
    is_process_queue = fields.Boolean("Is Processing Queue", default=False)
    running_status = fields.Char(default="Running...")
    is_action_require = fields.Boolean(default=False)
    process_count = fields.Integer(string="Queue Process Times", help="it is used know queue how many time processed")
    company_id = fields.Many2one("res.company", string="Company")

    @api.depends("line_ids.state")
    def _compute_queue_state(self):
        """
        Computes state from different states of queue lines.
        """
        for record in self:
            if record.total_count == record.done_count + record.cancel_count:
                record.state = "completed"
            elif record.total_count == record.draft_count:
                record.state = "draft"
            elif record.total_count == record.failed_count:
                if record.state != "failed":
                    record.state = "failed"
                    note = f"""
                    Attention {self.name} Product Queue is failed.\n
                    You need to process it manually
                    """
                    self.env["magento.instance"].create_activity(
                        model_name=self._name,
                        res_id=self.id,
                        message=note,
                        summary=self.name,
                        instance=self.instance_id,
                    )
            else:
                record.state = "partially_completed"

    @api.depends("line_ids.state")
    def _compute_record(self):
        """
        This will calculate total, draft, failed and done products sync/import from Magento.
        """
        for queue in self:
            total_count = len(queue.line_ids) if queue.line_ids else 0
            draft_count = len(queue.line_ids.filtered(lambda x: x.state == "draft"))
            failed_count = len(queue.line_ids.filtered(lambda x: x.state == "failed"))
            done_count = len(queue.line_ids.filtered(lambda x: x.state == "done"))
            cancel_count = len(queue.line_ids.filtered(lambda x: x.state == "cancel"))
            queue.sudo().write(
                {
                    "total_count": total_count,
                    "draft_count": draft_count,
                    "failed_count": failed_count,
                    "done_count": done_count,
                    "cancel_count": cancel_count,
                }
            )

    @api.model
    def create(self, vals):
        """
        Creates a sequence for Ordered Data Queue
        :param vals: values to create Ordered Data Queue
        :return: SyncImportMagentoProductQueue Object
        """
        sequences = self.env["ir.sequence"].search(
            [("company_id", "=", self.env.company.id), ("name", "=", "Product Queue")]
        )
        if not sequences:
            sequence_obj = (
                self.env["ir.sequence"]
                .sudo()
                .create(
                    {
                        "company_id": self.env.company.id,
                        "padding": 6,
                        "name": "Product Queue",
                    }
                )
            )
            end_code = sequence_obj.next_by_id(sequence_obj.id)
        else:
            end_code = sequences.next_by_id(sequences.id)

        name = f"Product Queue/{end_code}"
        vals.update({"name": name or ""})
        return super(MagentoProductQueue, self).create(vals)

    @staticmethod
    def _get_product_search_filter(**kwargs):
        filters = {
            "created_at": {"to": kwargs.get("to_date")},
            "status": 1,
            "type_id": {"in": kwargs.get("product_type")},
        }
        if kwargs.get("from_date"):
            filters.get("created_at", {}).update({"from": kwargs.get("from_date")})
        return filters

    def _create_product_queue(self, instance):
        queue = self.search([("instance_id", "=", instance.id), ("state", "=", "draft")])
        queue = queue.filtered(lambda q: len(q.line_ids) < 50)
        if not queue:
            queue = self.create({"instance_id": instance.id, "state": "draft"})
            message = f"Product Queue #{queue.name} Created!!"
            instance.show_popup_notification(message)
        return queue

    def create_product_queues(self, instance, from_date, to_date, p_type, is_update=True, current=0):
        """
        Creates product queues when sync/ import products from Magento.
        :param instance: current instance of Magento
        :param from_date:  Sync product start from this date
        :param to_date: Sync product end to this date
        :return:
        """
        queues = []
        queue_line = self.env["sync.import.magento.product.queue.line"]
        current_page = instance.magento_import_product_page_count
        from_date = datetime.combine(datetime.strptime(from_date[0:10], "%Y-%m-%d").date(), time.min).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        to_date = datetime.combine(datetime.strptime(to_date[0:10], "%Y-%m-%d").date(), time.max).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        filters = self._get_product_search_filter(from_date=from_date, to_date=to_date, product_type=p_type)
        products = self._get_product_response(instance, filters, current_page, get_pages=True)
        self._update_import_product_counter(instance, products)
        total_page = math.ceil(int(products.get("total_count")) / 50)
        if current:
            current_page = current
        for page in range(current_page, total_page + 1):
            products = self._get_product_response(instance, filters, page=page)
            if not products.get("items", []):
                self._update_import_product_counter(instance, products)
                break
            queue = self._create_product_queue(instance)
            queues.append(queue.id)
            try:
                for product in products.get("items"):
                    # Create new queue if the 50 queue_line count is reached.
                    if len(queue.line_ids) == 50:
                        queue = self._create_product_queue(instance)
                    queue_line.create_product_queue_line(
                        product=product,
                        instance_id=instance.id,
                        is_update=is_update,
                        queue_id=queue.id,
                        company_id=instance.company_id.id,
                    )
                self._cr.commit()
            except Exception as error:
                _logger.error(error)
                instance.write({"magento_import_product_page_count": page})
                self._cr.commit()
        instance.write({"magento_import_product_page_count": 1})
        self._cr.commit()
        return queues

    def _update_import_product_counter(self, instance, response):
        if not response.get("total_count", 0):
            instance.write({"magento_import_product_page_count": 1})
            # Commit if there are no any products found.
            self._cr.commit()
        return True

    @staticmethod
    def _get_product_response(instance, filters, page=1, get_pages=False):
        s_fields = []
        if get_pages:
            page = 1
            s_fields.append("total_count")
        search_criteria = create_search_criteria(filters, page_size=20, page=page, fields=s_fields)
        query_string = Php.http_build_query(search_criteria)
        api_url = f"/V1/products?{query_string}"
        return req(instance, api_url, is_raise=True)

    def import_specific_product(self, instance, product_sku_lists, is_update):
        """
        Creates product queues when sync/ import products from Magento.
        :param instance: current instance of Magento
        :param product_sku_lists:  Dictionary of Product SKUs
        :return:
        """
        queue_line = self.env["sync.import.magento.product.queue.line"]
        queues, log_line_id = [], []
        queue = self._create_product_queue(instance)
        queues.append(queue.id)
        for product_sku in product_sku_lists:
            try:
                sku = Php.quote_sku(product_sku)
                api_url = f"/V1/products/{sku}"
                response = req(instance, api_url)
            except Exception as error:
                if len(product_sku_lists) > 1:
                    log_line = self.env["common.log.lines.ept"].create(
                        {"message": f"Magento Product Not found for SKU {product_sku}", "default_code": product_sku}
                    )
                    log_line_id.append(log_line.id)
                    continue
                else:
                    raise UserError(_("Error while requesting products" + str(error)))
            if response:
                if len(queue.line_ids) >= 50:
                    queue = self._create_product_queue(instance)
                    queues.append(queue.id)
                queue_line.create_product_queue_line(
                    product=response,
                    instance_id=instance.id,
                    is_update=is_update,
                    queue_id=queue.id,
                    company_id=instance.company_id.id,
                )
        if log_line_id:
            self.create_log_of_missing_sku(instance, queue, log_line_id)
        return queues

    def create_log_of_missing_sku(self, instance, queue_id, log_line_id):
        """
        create common log record for the missing SKU.
        :param instance:
        :param queue_id:
        :param log_line_id:
        :return:
        """
        model_id = self.env["common.log.lines.ept"].get_model_id("sync.import.magento.product.queue")
        log_book_id = self.env["common.log.book.ept"].create(
            {
                "type": "import",
                "module": "magento_ept",
                "model_id": model_id,
                "res_id": queue_id.id or False,
                "magento_instance_id": instance.id,
                "log_lines": [(6, 0, log_line_id)],
            }
        )
        if queue_id:
            queue_id.log_book_id = log_book_id.id
        return True

    @api.model
    def retrieve_dashboard(self, *args, **kwargs):
        dashboard = self.env["queue.line.dashboard"]
        return dashboard.get_data(table="sync.import.magento.product.queue.line")

    def process_product_queues(self, is_manual=False):
        start = datetime.now()
        for queue in self.filtered(lambda q: q.state not in ["completed"]):
            cron_name = f"{queue._module}.ir_cron_parent_to_process_product_queue_data"
            process_cron_time = queue.instance_id.get_magento_cron_execution_time(cron_name)
            # To maintain that current queue has started to process.
            self._cr.commit()
            log = queue.log_book_id
            if not log:
                log = queue.instance_id.create_log_book(model=queue._name)
            queue.write({"is_process_queue": True, "log_book_id": log.id})
            domain = ["draft", "cancel", "failed"]
            queue.write({"process_count": queue.process_count + 1})
            if not is_manual and queue.process_count >= 3:
                queue.write({"process_count": queue.process_count + 1})
                note = f"""
                Attention {queue.name} Product Queue are processed 3 times and it failed. \n
                You need to process it manually
                """
                queue.instance_id.create_schedule_activity(queue=queue, note=note)
                domain.remove("failed")
                queue.write({"is_process_queue": False})
            lines = queue.line_ids.filtered(lambda l: l.state in domain)
            lines.process_queue_line()
            message = f"Product Queue #{queue.name} Processed!!"
            queue.instance_id.show_popup_notification(message)
            if not log.log_lines:
                log.sudo().unlink()
            # To maintain that current queue process are completed and new queue will be executed.
            queue.write({"is_process_queue": False})
            self._cr.commit()
            if (datetime.now() - start).seconds > (process_cron_time - 60):
                return True
        return True

    def check_product_magento(self):
        for rec in self:
            for line in rec.line_ids:
                product_id = []
                item = json.loads(line.data)
                if item.get("type_id") == "simple":
                    product_template = self.env["product.template"].search([("default_code", "=", line.product_sku)])
                    if not product_template:
                        values_product = {
                            "name": item.get("name"),
                            "default_code": item.get("sku"),
                        }
                        product_id = self.env["product.template"].create(values_product)
                    magento_product_template = self.env["magento.product.template"].search(
                        [("magento_sku", "=", line.product_sku)]
                    )
                    if not magento_product_template:
                        if product_template:
                            values = {
                                "magento_product_name": item.get("name"),
                                "magento_instance_id": line.instance_id.id,
                                "magento_sku": item.get("sku"),
                                "magento_product_template_id": item.get("id"),
                                "product_type": item.get("type_id"),
                                "sync_product_with_magento": True,
                                "odoo_product_template_id": product_template.id,
                            }
                            self.env["magento.product.template"].create(values)
                        else:
                            values = {
                                "magento_product_name": item.get("name"),
                                "magento_instance_id": line.instance_id.id,
                                "magento_sku": item.get("sku"),
                                "magento_product_template_id": item.get("id"),
                                "product_type": item.get("type_id"),
                                "sync_product_with_magento": True,
                                "odoo_product_template_id": product_id.id,
                            }
                            self.env["magento.product.template"].create(values)

                if item.get("type_id") == "configurable":
                    link = item.get("extension_attributes").get("configurable_product_link_data")
                    magento_sku = ""
                    for child_product_data in link:
                        product_con_id = []
                        product_template = self.env["product.template"].search([("default_code", "=", magento_sku)])
                        if not product_template:
                            values_product = {
                                "name": child_product_data.get("product_name"),
                                "default_code": child_product_data.get("simple_product_sku"),
                            }
                            product_con_id = self.env["product.template"].create(values_product)
                        magento_sku = child_product_data.get("simple_product_sku")
                        magento_product_product = self.env["magento.product.template"].search(
                            [("magento_sku", "=", magento_sku)]
                        )
                        if not magento_product_product:
                            if product_template:
                                values = {
                                    "magento_product_name": child_product_data.get("product_name"),
                                    "magento_instance_id": line.instance_id.id,
                                    "magento_sku": child_product_data.get("simple_product_sku"),
                                    "magento_product_template_id": child_product_data.get("simple_product_id"),
                                    "product_type": child_product_data.get("product_type"),
                                    "sync_product_with_magento": True,
                                    "odoo_product_template_id": product_template.id,
                                }
                                self.env["magento.product.template"].create(values)
                            else:
                                values = {
                                    "magento_product_name": child_product_data.get("product_name"),
                                    "magento_instance_id": line.instance_id.id,
                                    "magento_sku": child_product_data.get("simple_product_sku"),
                                    "magento_product_template_id": child_product_data.get("simple_product_id"),
                                    "product_type": child_product_data.get("product_type"),
                                    "sync_product_with_magento": True,
                                    "odoo_product_template_id": product_con_id.id,
                                }
                                self.env["magento.product.template"].create(values)
