import json
import base64
import io
import os
import mimetypes
import logging
import random
from pathlib import Path
import secrets
from . import email_service
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentProcessing


_logger = logging.getLogger(__name__)


class CursoLeolandiaController(WebsiteSale):
    def _registrar_cliente(self, post):
        post_email = post.get('email')
        email = post_email.strip()
        name = post.get('name')
        country_id = int(post.get('country'))
        phone = post.get('phone')

        partner = request.env['res.partner'].sudo().search([
            ('email', '=', email)
        ], limit=1)

        country = request.env['res.country'].search([
            ('id', '=', int(country_id))
        ])

        values = {
            'name': name,
            'email': email,
            'type': 'contact',
            'country_id': country.id,
            'street': country.name,
            'comment': 'Curso Loelandia 01',
            'type_partner': 'customer',
            'mobile': phone,
            'website_id': request.website.id,
            'company_id': request.website.company_id.id,
            'team_id': request.website.salesteam_id and request.website.salesteam_id.id,
            'user_id': request.website.salesperson_id and request.website.salesperson_id.id,
            'estado_compra': 'inscrito',
            'email_pago_enviado': False,
            'email_transfer': False
        }

        if partner:
            partner.write(values)
        else:
            partner = request.env['res.partner'].sudo().create(values)

            curso = request.env['curso.producto'].sudo().search([('id', '=', int(post.get('curso_id')))])
            inscritos = curso.suscritos + 1

            curso.write({
                'suscritos': inscritos
            })

        return partner

    def _create_orden_cliente(self, partner_id, post):
        partner = request.env['res.partner'].sudo().search([
            ('id', '=', partner_id)
        ], limit=1)

        product = request.env['product.product'].sudo().search([
            ('barcode', '=', post.get('product_id'))
        ])

        sale_order = partner.last_website_so_id
        logging.warning(partner_id)
        logging.warning(sale_order)

        if not sale_order:
            logging.warning("Creando orden")
            sale_order = request.website.sale_get_order(force_create=1)

            sale_order.partner_id = partner_id
            sale_order._cart_update(
                product_id=product.id,
                set_qty=1
            )

            sale_order.onchange_partner_shipping_id()
            sale_order.order_line._compute_tax_id()
            request.session['sale_last_order_id'] = sale_order.id
            request.website.sale_get_order(update_pricelist=True)
        else:
            request.session['sale_order_id'] = sale_order.id

    @http.route(['''/shop/curso-leolandia''',
                 '''/shop/curso-leolandia/<int:op>'''], type='http', auth="public", website=True)
    def curso_leolandia(self, access_token=None, op=0, **kwargs):
        curso = request.env['curso.producto'].sudo().search([
            ('codigo', '=', 'CUR-LEO-01')
        ])

        values = {
            "paises": request.env['res.country'].get_website_sale_countries(),
            'curso': curso.id,
            'product': curso.producto.barcode,
            'partner': {}
        }

        if op == '1':
            values['exito'] = 'S'
            values['url_payment'] = '/shop/payment'

        # error
        if op == '2':
            values['exito'] = 'N'
            values['msj'] = 'Lo sentimos, el curso ya no se encuentra disponible.'

        # el usuario ya se registro al curso
        if op == '3':
            values['exito'] = 'N'
            values['msj'] = 'Ya te has inscrito a la Primera Edición de Latinoamérica de LEOLANDIA Online con el correo electrónico que has proporcionado.'

        return request.render("sitio_imagen.tmpl_curso_leolandia", values)

    @http.route(['/shop/curso/registrate'], type='http', auth="public", website=True)
    def registrate_curso(self, **post):
        email = post.get('email')

        if email:
            curso = request.env['curso.producto'].sudo().search([('id', '=', int(post.get('curso_id')))])

            if not curso or (not curso.activo or curso.suscritos >= curso.maximo_suscritos):
                return request.redirect('/shop/curso-leolandia?op=' + str(2))

            request.website.sale_reset()
            partner = self._registrar_cliente(post)
            self._create_orden_cliente(partner.id, post)
            logging.warning(request.session['sale_last_order_id'])

            return request.redirect('/shop/curso-leolandia?op=' + str(1))
        else:
            return request.redirect('/shop/curso-leolandia')

    @http.route(['/shop/curso/gracias'], type='http', auth="public", website=True)
    def curso_gracias(self, **kwargs):
        request.website.sale_reset()
        return request.render("sitio_imagen.thanks_leolandia")


