import hashlib
import hmac
import logging
from unicodedata import normalize
import psycopg2
import werkzeug

from odoo import http, _
from odoo.http import request
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, consteq, ustr
from odoo.tools.float_utils import float_repr
from datetime import datetime, timedelta

from odoo.addons.payment.controllers.portal import PaymentProcessing


class PaymentProcessingImagen(PaymentProcessing):
    @http.route()
    def payment_status_page(self, **kwargs):
        logging.warning("Override Payment Status Page")

        sale_order_id = request.session.get('sale_last_order_id')

        if sale_order_id:
            logging.warning("Sale Order existe")

        return super(PaymentProcessingImagen, self).payment_status_page(kwargs)
