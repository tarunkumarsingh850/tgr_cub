"""
Describes methods for webhooks to create order, invoice, product and customer.
"""
import base64
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class Binary(http.Controller):
    """
    Describes methods for webhooks to create order, invoice, product and customer.
    """

    @http.route("/web/binary/download_sob_document", type="http", auth="public")
    @serialize_exception
    def download_document(self, model, id, filename=None):
        """
        Download link for files stored as binary fields.
        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        wizard_id = request.env[model].browse([int(id)])
        filecontent = base64.b64decode(wizard_id.file or "")
        return_val = False
        if not filecontent:
            return_val = request.not_found()
        else:
            if not filename:
                filename = "{}_{}".format(model.replace(".", "_"), id)
            return_val = request.make_response(
                filecontent,
                [("Content-Type", "application/octet-stream"), ("Content-Disposition", content_disposition(filename))],
            )
        return return_val
