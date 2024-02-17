import random
import string
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import AccessDenied


class RestAuth2(models.Model):
    _name = "auth.auth"
    _description = "Auth2 Authentication"

    user_id = fields.Many2one("res.users", "User", required=True)
    name = fields.Char(required=True, default="NEW")
    description = fields.Char("Description")
    consumer_key = fields.Char("Consumer Key")
    consumer_secret = fields.Char("Consumer Secret")
    refresh_token = fields.Char("Refresh Token")
    redirect_uri = fields.One2many("redirect.uri", "redirect_id", string="Redirect URI")
    access_token_ids = fields.One2many("auth.access.token", "token_id")
    auth_code = fields.Char("Authorization Code", help="It will store the Authorization Code temporary.")

    def update_key_secret(self):
        """It will update key"""
        self.consumer_key = self.generate_token()
        self.consumer_secret = self.generate_token()

    def generate_refresh(self):
        self.refresh_token = self.generate_token()

    def revoke_refresh(self):
        self.refresh_token = ""

    def generate_token(self):
        """It will generate token"""
        return "".join([random.choice(string.ascii_letters + string.digits) for n in range(30)])

    @api.model
    def create(self, vals):
        vals["name"] = vals["name"]
        return super(RestAuth2, self).create(vals)


class RedirectURI(models.Model):
    _name = "redirect.uri"
    _description = "Auth2 Call Back URI"

    redirect_id = fields.Many2one("auth.auth", "Redirect")
    url = fields.Char("URL")


class AuthAccess(models.Model):
    _name = "auth.access.token"
    _description = "Auth2 Access Token"

    token_id = fields.Many2one("auth.auth")
    access_token = fields.Char()
    access_token_validity = fields.Datetime("Token Validity")

    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.

        :param scopes: An iterable containing the scopes to check or None
        """
        self.ensure_one()
        return not self.is_expired() and self._allow_scopes(scopes)

    def is_expired(self):
        self.ensure_one()
        return datetime.now() > self.access_token_validity

    def _allow_scopes(self, scopes):
        self.ensure_one()
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)

        return resource_scopes.issubset(provided_scopes)


class ResUsers(models.Model):
    _inherit = "res.users"

    auth2_access_token = fields.Char()
    """It will authenticate user"""

    def _check_credentials(self, password, env):
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            auth_record = (
                self.env["auth.access.token"]
                .sudo()
                .search([("token_id.user_id", "=", self.id), ("access_token_validity", ">=", fields.Datetime.now())])
            )
            available_tokens = auth_record.mapped("access_token")
            if password in available_tokens:
                return
            raise
