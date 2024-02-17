# -*- coding: utf-8 -*-
import odoo
import json
import werkzeug
from odoo import http
import random
import string
from odoo.http import request, Response

# import simplejson
from urllib.parse import urlparse
from urllib.parse import urlunparse
from oauthlib.common import urlencode, urlencoded, quote
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.odoo_auth2.controllers.auth2_authentication import validate_token
from odoo import api


class RestAuth2Access(http.Controller):
    def _get_escaped_full_path(self, request):
        parsed = list(urlparse(request.httprequest.path))
        unsafe = {c for c in parsed[4]}.difference(urlencoded)
        for c in unsafe:
            parsed[4] = parsed[4].replace(c, quote(c, safe=""))

        return urlunparse(parsed)

    def _extract_params(self, request, post_dict):
        """
        Extract parameters from the request object. Such parameters will then be passed to
        OAuthLib to build its own Request object
        """
        uri = self._get_escaped_full_path(request)
        http_method = request.httprequest.method

        headers = dict(list(request.httprequest.headers.items()))
        if "wsgi.input" in headers:
            del headers["wsgi.input"]
        if "wsgi.errors" in headers:
            del headers["wsgi.errors"]
        if "HTTP_AUTHORIZATION" in headers:
            headers["Authorization"] = headers["HTTP_AUTHORIZATION"]
        body = urlencode(list(post_dict.items()))
        return uri, http_method, body, headers

    def _response(self, headers, body, status=200):
        try:
            fixed_headers = {str(k): v for k, v in list(headers.items())}
        except Exception:
            fixed_headers = headers
        response = werkzeug.Response(response=body, status=status, headers=fixed_headers)
        """It will return response of auth2"""
        return response

    @http.route("/oauth2/auth", type="http", auth="public", csrf=False)
    def auth_url(self, **kw):
        """This method is based on auth2 authentication Url It will reutrn Redirect URI call back"""
        uri, http_method, body, headers = self._extract_params(request, kw)
        user = self.get_user(kw)
        error = {}
        if user.login == "public":
            scope = kw.get("scope")
            params = {"mode": "login", "scope": scope, "redirect": "/oauth2/auth?%s" % werkzeug.url_encode(kw)}
            url = "/web/login"
            return self._response(
                {"Location": "{url}?{params}".format(url=url, params=werkzeug.url_encode(params))}, None, 302
            )
        else:
            client_id = request.env["auth.auth"].search(
                [("consumer_key", "=", kw["client_id"]), ("user_id", "=", user.id)]
            )
            if client_id:
                redirect_url = request.env["redirect.uri"].search(
                    [("redirect_id", "=", client_id.id), ("url", "=", kw["redirect_uri"])]
                )
                if redirect_url:
                    code = client_id.generate_token()
                    params = {
                        "code": code,
                        "state": kw["state"],
                    }
                    client_id.write({"auth_code": code})
                    return self._response(
                        {"Location": "{url}?{params}".format(url=redirect_url.url, params=werkzeug.url_encode(params))},
                        None,
                        302,
                    )
                else:
                    """Errors embedded in the Invalid Redirect URI"""
                    error.update({"error": "access_denied", "error_description": "Invalid Redirect URI"})
                    return Response(json.dumps(error))
            else:
                """Errors embedded in the redirect URI back to the client"""
                error.update({"error": "access_denied", "error_description": "Invalid Consumer ID"})
                return Response(json.dumps(error))

    @http.route("/oauth2/access_token", type="http", auth="public", csrf=False)
    def access_token(self, context=None, **kw):
        """This method is used for generate access token for auth2"""
        self.get_user(kw)
        error = {}
        uri, http_method, body, headers = self._extract_params(request, kw)
        # ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 120
        ACCESS_TOKEN_EXPIRE_SECONDS = 86400
        expires = datetime.now() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
        client_id = request.env["auth.auth"].search(
            [("consumer_key", "=", kw["client_id"]), ("consumer_secret", "=", kw["client_secret"])]
        )
        if client_id:
            # if redirect_url:
            refresh_token = client_id.refresh_token
            access_token = "".join([random.choice(string.ascii_letters + string.digits) for n in range(40)])
            body = json.dumps(
                {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "access_token_validity": expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    "refresh_token": refresh_token,
                }
            )
            status = 200
            token_vals = {
                "access_token": access_token,
                "access_token_validity": expires.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            }
            client_id.user_id.sudo().write({"auth2_access_token": access_token})
            client_id.sudo().write({"auth_code": "", "access_token_ids": [(0, 0, token_vals)]})
            return self._response(headers, body, status)
            # else:
            #     """Errors embedded in the redirect URI back to the client"""
            #     error.update({'error':'access_denied','error_description':'Invalid Redirct URI'})
            #     return werkzeug.Response('Access denied %r'%error)

        else:
            """Errors embedded in the redirect URI back to the client"""
            error.update({"error": "Unuthorized_client", "error_description": "Invalid Consumer ID"})
            return Response(json.dumps(error))

    def get_user(self, kw):
        """It will return current loged with user"""
        user_obj = request.env["res.users"].sudo()
        uid = kw.get("uid", False) or request.uid
        return user_obj.browse(int(uid))


class RestController(http.Controller):
    @validate_token
    @http.route("/api/employee", auth="none", type="http", methods=["GET"], csrf=False)
    def api_get_employee(self, model="res.users", values=None, context=None, token=None, **kw):
        """
        API to Get Employee
        """
        try:
            # authenticate()
            """This is used for authenticate the users token"""
            res = []
            env = api.Environment(request.cr, odoo.SUPERUSER_ID, {"active_test": False})
            partners = env[model].search([])

            for partner in partners:
                partner_vals = {
                    "name": partner.name,
                    "login": partner.login,
                }
                res.append(partner_vals)

            return Response(
                json.dumps(res, sort_keys=True, indent=4), content_type="application/json;charset=utf-8", status=200
            )
        except Exception as e:
            return Response(
                json.dumps({"error": e.__str__(), "status_code": 500}, sort_keys=True, indent=4),
                content_type="application/json;charset=utf-8",
                status=200,
            )
