from odoo import api, models
from bs4 import BeautifulSoup
import re


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        res = super(MailMessage, self).create(vals)
        if res and res.message_type == "comment":
            msg = vals.get("body")
            soup = BeautifulSoup(msg, "html.parser")
            links = soup.find_all("a")
            pattern = "<[^<]+?>"
            text_msg = re.sub(pattern, "", msg)
            ids = []
            for link in links:
                if "data-oe-model" in link.prettify():
                    ids.append(int(link["data-oe-id"]))
            # ids = [int(link['data-oe-id']) for link in links]
            for partner in ids:
                channel = self.env["mail.channel"].channel_get([partner])
                channel_id = self.env["mail.channel"].browse(channel["id"])
                channel_id.sudo().message_post(
                    partner_ids=ids,
                    body=text_msg,
                    message_type="comment",
                )
        return res
