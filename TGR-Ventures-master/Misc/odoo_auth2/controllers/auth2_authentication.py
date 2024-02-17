import functools
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.odoo_auth2.common import invalid_response


def authenticate():
    """This method is based on auth2 authentication.
            It will authenticate the users token.
            params :
            Authorization: Authorization should be part of request header
            and it must include Bearer
            Return: It will raise error if token is invalid.

    To use this method import it in your controler
    from odoo.addons.odoo_auth2.controllers.auth2_authentication import authenticate
    add authentication() in your controller:

    """
    headers = dict(list(request.httprequest.headers.items()))
    authHeader = headers["Authorization"]
    if authHeader.startswith("Bearer "):
        try:
            access_token = authHeader[7:]
            token = request.env["auth.access.token"].search([("access_token", "=", access_token)])
            if not token or not token.is_valid():
                raise UserError("Access Token Invalid.")
            user = token.token_id.user_id
            db = request.session.db
            request.session.authenticate(db, user.sudo().login, access_token)
            return request.env["ir.http"].session_info()
        except Exception as e:
            raise e
    else:
        raise UserError("Access Token Invalid Start with Bearer")


def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        headers = dict(list(request.httprequest.headers.items()))
        if not "Authorization" in headers:
            return invalid_response("access_token", "token is required", 401)
        authHeader = headers["Authorization"]
        if authHeader.startswith("Bearer "):
            try:
                access_token = authHeader[7:]
                token = request.env["auth.access.token"].search([("access_token", "=", access_token)])
                if not token or not token.is_valid():
                    return invalid_response("access_token", "token seems to have expired or invalid", 401)
                user = token.token_id.user_id
                db = request.session.db
                request.session.authenticate(db, user.sudo().login, access_token)
                return func(self, *args, **kwargs)
            except Exception as e:
                raise e
        else:
            raise UserError("Access Token Invalid Start with Bearer")

    return wrap
