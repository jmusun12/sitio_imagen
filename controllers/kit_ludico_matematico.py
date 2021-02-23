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


class WebSiteSaleInherit(WebsiteSale):
    @http.route(['/shop/kit-ludico-matematico'], type='http', auth="public", website=True)
    def kit_ludico(self, **kwargs):
        print('Kit lúdico')
        return request.render("sitio_imagen.tmp_kit_ludico_matematico")

        # return request.render("sitio_imagen.tmp_email_download")

    @http.route(['/shop/kit-email'], type='http', auth="public", website=True)
    def send_email_kit_ludico(self, **post):
        email = post.get('email')

        if email:
            print(email)

            cliente = request.env['res.partner'].search([
                ('email', '=', email.strip())
            ])

            codigo = request.env['codigos.cliente.website'].search([
                ('email', '=', email.strip())
            ])

            if not cliente and not codigo:
                print('Cliente no existe')
                name = post.get('name')
                institucion = post.get('institucion')
                grado = post.get('nivel')
                code = secrets.token_hex(20)

                request.env['codigos.cliente.website'].invalidate_cache()
                request.env['codigos.cliente.website'].sudo().create({
                    'name': name,
                    'code': code,
                    'email': email.strip(),
                    'state': 'generado',
                    'note': '{0} - {1}'.format(institucion, grado)
                })

                message = email_service.get_message(name, institucion, grado, code)
                request.website.send_email("¡Gracias por apuntarte a la aventura de jugar con las matemáticas!",
                                         email.strip(), message)
                print('Correo enviado')

                return request.render("sitio_imagen.tmp_kit_ludico_matematico", {
                    'exito': 'S',
                    'email': email
                })
            else:
                print('Cliente existe')
                return request.render("sitio_imagen.tmp_kit_ludico_matematico", {
                    'exito': 'N',
                    'email': email
                })
        else:
            print('No email')
            return request.render("sitio_imagen.tmp_kit_ludico_matematico")

    @http.route(['''/shop/plantilla/<string:code>'''], type='http', auth="public", website=True)
    def shop_template(self, code, **kwargs):
        if request.env['codigos.cliente.website'].sudo().search_count(
                [('code', '=', code), ('state', '=', 'generado'), ('download_count', '=', 0)]):
            codigo_cliente = request.env['codigos.cliente.website'].sudo().search([
                ('code', '=', code),
                ('state', '=', 'generado')
            ])

            if request.env['res.partner'].search_count([('email', '=', codigo_cliente['email'])]):
                return request.render("sitio_imagen.tmp_kit_ludico_matematico", {
                    'exito': 'N',
                    'email': codigo_cliente['email']
                })

            return request.render("sitio_imagen.tmp_download_template", {
                'enlace': '/shop/download-template/{0}'.format(code),
                'cliente': codigo_cliente
            })

        else:
            return request.render("sitio_imagen.tmp_code_error", {
                'code': code
            })

    @http.route(['''/shop/download-template/<string:code>'''], type='http', auth="public", website=True)
    def download_template(self, code, **kwargs):
        if request.env['codigos.cliente.website'].sudo().search_count(
                [('code', '=', code), ('state', '=', 'generado'), ('download_count', '=', 0)]):
            codigo_cliente = request.env['codigos.cliente.website'].sudo().search([
                ('code', '=', code),
                ('state', '=', 'generado')
            ])

            request.env['ir.rule'].clear_cache()
            codigo_cliente.write({
                'state': 'usado',
                'download_count': 1
            })

            if request.env['res.partner'].search_count([('email', '=', codigo_cliente['email'])]):
                return request.render("sitio_imagen.tmp_kit_ludico_matematico", {
                    'exito': 'N',
                    'email': codigo_cliente['email']
                })

            attachment = request.env['catalogo.producto'].search([
                ('key', '=', 'plantilla_mate_01')
            ])

            if attachment:
                request.env['ir.rule'].clear_cache()
                request.env['res.partner'].sudo().create({
                    'name': codigo_cliente['name'],
                    'email': codigo_cliente['email'],
                    'type': 'contact',
                    'comment': codigo_cliente['note'],
                    'type_partner': 'customer'
                })

                data = io.BytesIO(base64.standard_b64decode(attachment["file"]))
                # we follow what is done in ir_http's binary_content for the extension management
                extension = os.path.splitext(attachment["file_name"] or '')[1]
                extension = extension if extension else mimetypes.guess_extension(attachment["file_type"] or '')
                filename = attachment['file_name']
                filename = filename if os.path.splitext(filename)[1] else filename + extension
                return http.send_file(data, filename=filename, as_attachment=True)
        else:
            return request.render("sitio_imagen.tmp_code_error", {
                'code': code
            })
