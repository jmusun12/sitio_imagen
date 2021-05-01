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
from . import email_service

from odoo.addons.payment.controllers.portal import PaymentProcessing


class PaymentProcessingImagen(PaymentProcessing):
    @http.route()
    def payment_status_page(self, **kwargs):
        logging.warning("Overriden Payment Status Page")
        sale_order_id = request.session.get('sale_order_id')

        if sale_order_id:
            return request.redirect("/shop/confirmation")
        else:
            # When the customer is redirect to this website page,
            # we retrieve the payment transaction list from his session
            tx_ids_list = self.get_payment_transaction_ids()
            payment_transaction_ids = request.env['payment.transaction'].sudo().browse(tx_ids_list).exists()

            render_ctx = {
                'payment_tx_ids': payment_transaction_ids.ids,
            }
            return request.render("payment.payment_process_page", render_ctx)
