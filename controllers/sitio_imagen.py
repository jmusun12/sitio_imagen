# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import base64
import io
import os
import mimetypes
import logging
import random
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
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('id', '=', 3)], limit=1)

        """
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 3
        """
        ppg = 9

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
            'url_get': '/shop'
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)


    @http.route()
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
            elif revive == 'squash' or (revive == 'merge' and not request.session.get('sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get('sale_order_id'):  # abandoned cart found, user have to choose what to do
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

        return request.render("website_sale.cart", values)

    @http.route(['/shop/thanks'], type='http', auth="public", website=True)
    def thanks(self, **kwargs):
        return request.render("sitio_imagen.thanks")

    @http.route(['/shop/contact'], type='http', auth="public", website=True)
    def contact(self, **kw):
        return request.render("sitio_imagen.page_contact_imagen")

    @http.route()
    def print_saleorder(self, **kwargs):
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            pdf, _ = request.env.ref('sitio_imagen.action_report_saleorder_imagen').sudo().render_qweb_pdf([sale_order_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop')

    @http.route(['''/shop/libros-chicos-2-4''', '''/shop/libros-chicos-2-4/page/<int:page>'''], type='http', auth="public", website=True)
    def libros_2_4(self, page=0, category=None, search='', ppg=False, **post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('id', '=', 4)], limit=1)

        """
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 3
        """
        ppg = 9

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
            'url_get': '/shop/libros-chicos-2-4'
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)

    @http.route(['''/shop/libros-chicos-4-5''', '''/shop/libros-chicos-4-5/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_4_5(self, page=0, category=None, search='', ppg=False, **post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('id', '=', 2)], limit=1)

        """
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 3
        """
        ppg = 9

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
            'url_get': '/shop/libros-chicos-4-5'
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)

    @http.route(['''/shop/libros-chicos-6-7''', '''/shop/libros-chicos-6-7/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_6_7(self, page=0, category=None, search='', ppg=False, **post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('id', '=', 7)], limit=1)

        """
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 3
        """
        ppg = 9

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
            'url_get': '/shop/libros-chicos-6-7'
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)

    @http.route(['''/shop/libros-chicos-8-9''', '''/shop/libros-chicos-8-9/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_8_9(self, page=0, category=None, search='', ppg=False, **post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('id', '=', 8)], limit=1)

        """
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 3
        """
        ppg = 9

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
            'url_get': '/shop/libros-chicos-8-9'
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)

    @http.route(['''/shop/libros-chicos-10-12''', '''/shop/libros-chicos-10-12/page/<int:page>'''], type='http',
                auth="public", website=True)
    def libros_10_12(self, page=0, category=None, search='', ppg=False, **post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('id', '=', 5)], limit=1)

        """
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 3
        """
        ppg = 9

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
            'url_get': '/shop/libros-chicos-10-12'
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)

    @http.route()
    def print_saleorder(self, **kwargs):        
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            pdf, _ = request.env.ref('sitio_imagen.action_report_saleorder_imagen').sudo().render_qweb_pdf([sale_order_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop')

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
                email_service.send_email(email.strip(), message)
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

    @http.route(['''/shop/plantilla/<string:code>'''], type='http', auth="public", website=True, method=['POST'])
    def download_template(self, code, **kwargs):
        request.env['codigos.cliente.website'].invalidate_cache()
        request.env['res.partner'].invalidate_cache()

        codigo_cliente = request.env['codigos.cliente.website'].sudo().search([
            ('code', '=', code),
            ('state', '=', 'generado')
        ])

        if codigo_cliente and codigo_cliente.download_count == 0:
            res_partner = request.env['res.partner'].search([
                ('email', '=', codigo_cliente['email'])
            ])

            if res_partner:
                return request.render("sitio_imagen.tmp_kit_ludico_matematico", {
                    'exito': 'N',
                    'email': codigo_cliente['email']
                })

            request.env['codigos.cliente.website'].sudo().search([
                ('code', '=', code),
                ('state', '=', 'generado')
            ]).write({
                'state': 'usado',
                'download_count': 1
            })

            attachment = request.env['catalogo.producto'].search([
                ('key', '=', 'plantilla_mate_01')
            ])

            if attachment:
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