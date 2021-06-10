# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import math
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

_logger = logging.getLogger(__name__)


class WebSiteSaleInherit(WebsiteSale):
    def _get_shop_values(self, category_code, search, page, ppg, url_get, svg, post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('code', '=', category_code)], limit=1)

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 12

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain

        products_count = Product.search_count(domain)
        pages_count = int(math.ceil(products_count / ppg))

        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category

        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'url_get': url_get,
            'id_svg': svg,
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        return self._get_shop_values('cat_0_1', search, page, ppg, '/shop', 'green_cloud', post)

    @http.route(['''/shop/cart''', '''/shop/cart/<string:access_token>'''], type='http', auth="public",
                website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        print('Call override cart')

        order = request.website.sale_get_order()

        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()

        order.recompute_coupon_lines()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get(
                    'sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get(
                    'sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})

        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        })
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values,
                                  headers={'Cache-Control': 'no-cache'})
        if post.get('type') == 'slide':
            order_lines = order.order_line
            values['lines_product'] = order_lines[:3]

            return request.render("sitio_imagen.cart_slide", values,
                                  headers={'Cache-Control': 'no-cache'})

        group_line_order = []
        group = []
        cont = 0
        order_lines = order.order_line
        for item in order_lines:
            if cont > 3:
                group_line_order.append(group)
                group = []
                cont = 0

            group.append(item)
            cont += 1

        if len(group):
            group_line_order.append(group)

        values['website_group_line_order'] = group_line_order
        values['step'] = request.session.get('step')
        request.session['step'] = 0

        return request.render("website_sale.cart", values)

    @http.route(['/shop/contact'], type='http', auth="public", website=True)
    def contact(self, **kw):
        return request.render("sitio_imagen.page_contact_imagen")

    @http.route()
    def print_saleorder(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            pdf, _ = request.env.ref('sitio_imagen.action_report_saleorder_imagen').sudo().render_qweb_pdf(
                [sale_order_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop')

    @http.route(['''/shop/libros-chicos-2-4''', '''/shop/libros-chicos-2-4/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_2_4(self, page=0, category=None, search='', ppg=False, **post):
        return self._get_shop_values('cat_2_4', search, page, ppg, '/shop/libros-chicos-2-4', 'yellow_cloud', post)

    @http.route(['''/shop/libros-chicos-4-5''', '''/shop/libros-chicos-4-5/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_4_5(self, page=0, category=None, search='', ppg=False, **post):
        return self._get_shop_values('cat_4_5', search, page, ppg, '/shop/libros-chicos-4-5', 'pink_cloud', post)

    @http.route(['''/shop/libros-chicos-6-7''', '''/shop/libros-chicos-6-7/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_6_7(self, page=0, category=None, search='', ppg=False, **post):
        return self._get_shop_values('cat_6_7', search, page, ppg, '/shop/libros-chicos-6-7', 'violet_cloud', post)

    @http.route(['''/shop/libros-chicos-8-9''', '''/shop/libros-chicos-8-9/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_8_9(self, page=0, category=None, search='', ppg=False, **post):
        return self._get_shop_values('cat_8_9', search, page, ppg, '/shop/libros-chicos-8-9', 'blue_cloud', post)

    @http.route(['''/shop/libros-chicos-10-12''', '''/shop/libros-chicos-10-12/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_10_12(self, page=0, category=None, search='', ppg=False, **post):
        return self._get_shop_values('cat_10_12', search, page, ppg, '/shop/libros-chicos-10-12', 'orange_cloud', post)

    @http.route()
    def print_saleorder(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            pdf, _ = request.env.ref('sitio_imagen.action_report_saleorder_imagen').sudo().render_qweb_pdf(
                [sale_order_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop')

    @http.route(['''/shop/recovery_cart''', '''/shop/recovery_cart/<string:access_token>'''], type='http',
                auth="public", website=True)
    def recovery_cart(self, access_token):
        abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)

        if abandoned_order:
            request.session['sale_last_order_id'] = abandoned_order.id

            return request.redirect('/shop/payment')

    @http.route(['/shop/cart/update_website'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update_website(self, product_id, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""

        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )

        request.session['step'] = 1
        logging.warning('cart_update_website')
        return request.redirect('/shop/cart')