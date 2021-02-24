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
    def send_email_leolandia(self, partner_name, partner_email):
        template = request.env['template.email.website'].sudo().search([
            ('name', '=', 'TEMP-EMAIL-LEO'),
            ('activo', '=', True),
            ('website_id', '=', request.website.id)
        ])

        if template:
            string_email = str(template.html).replace('partner_name', partner_name)
            email_service.send_email("Confirmación de pago", partner_email,
                                     string_email)

            logging.warning("Email enviado a {0}".format(partner_email))

    def send_email_transfer(self, partner_name, partner_email):
        template = request.env['template.email.website'].sudo().search([
            ('name', '=', 'TEMP-EMAIL-TRANSFER'),
            ('activo', '=', True),
            ('website_id', '=', request.website.id)
        ])

        if template:
            string_email = str(template.html).replace('partner_name', partner_name)
            email_service.send_email("Datos de pago", partner_email, string_email)

            logging.warning("Email de transferencia enviado a {0}".format(partner_email))

    def update_partner(self, partner_id, estado, email_pago=False, email_transfer=False):
        partner = request.env['res.partner'].sudo().search([
            ('id', '=', partner_id)
        ])

        partner.write({
            'estado_compra': estado,
            'email_pago_enviado': email_pago,
            'email_transfer': email_transfer
        })

    @http.route()
    def payment_status_page(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            logging.warning("Orden existe en payment status")

            order = request.env['sale.order'].sudo().browse(sale_order_id)
            payment_tx_id = order.get_portal_last_transaction()

            if order.only_services:
                curso = request.env['curso.producto'].sudo().search([
                    ('codigo', '=', 'CUR-LEO-01')
                ])

                logging.warning("Solo servicios")

                if any(line.product_id.barcode == curso.producto.barcode for line in order.order_line):
                    if payment_tx_id.state == 'done':
                        logging.warning("Transaccion hecha")
                        order.action_confirm()  # confirmamos la orden de venta
                        order._force_lines_to_invoice_policy_order()
                        invoices = order._create_invoices()
                        payment_tx_id.invoice_ids = [(6, 0, invoices.ids)]
                        request.website.sale_reset()
                        logging.warning("Orden confirmada y factura creada...")

                        if not order.partner_id.email_pago_enviado:
                            self.send_email_leolandia(order.partner_id.name, order.partner_id.email)
                            self.update_partner(order.partner_id.id, estado='pagado', email_pago=True)
                            return request.redirect("/shop/curso/gracias")

                    if payment_tx_id.acquirer_id.provider == 'transfer':
                        if not order.partner_id.email_transfer:
                            self.send_email_transfer(order.partner_id.name, order.partner_id.email)
                            self.update_partner(order.partner_id.id, estado='pendiente', email_pago=False,
                                                email_transfer=True)
                            if any(line.product_id.barcode == curso.producto.barcode for line in order.order_line):
                                return request.redirect("/shop/curso/gracias")
                            else:
                                return request.render("website_sale.confirmation", {'order': order})
            else:
                if payment_tx_id.acquirer_id.provider == 'transfer':
                    if not order.partner_id.email_transfer:
                        self.send_email_transfer(order.partner_id.name, order.partner_id.email)
                        self.update_partner(order.partner_id.id, estado='pendiente', email_pago=False,
                                            email_transfer=True)

                return request.render("website_sale.confirmation", {'order': order})
        else:
            # When the customer is redirect to this website page,
            # we retrieve the payment transaction list from his session
            tx_ids_list = self.get_payment_transaction_ids()
            payment_transaction_ids = request.env['payment.transaction'].sudo().browse(tx_ids_list).exists()

            render_ctx = {
                'payment_tx_ids': payment_transaction_ids.ids,
            }
            return request.render("payment.payment_process_page", render_ctx)
