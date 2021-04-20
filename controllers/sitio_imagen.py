# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
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
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('code', '=', 'cat_0_1')], limit=1)

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
            'url_get': '/shop',
            'id_svg': 'green_cloud'
        }

        if category:
            values['main_object'] = category

        if post.get('xhr'):
            return request.render("sitio_imagen.content_product_imagen", values,
                                  headers={'Cache-Control': 'no-cache'})

        return request.render("website_sale.products", values)

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

        return request.render("website_sale.cart", values)

    @http.route(['''/shop/thanks''', '''/shop/thanks/<string:res>'''], type='http', auth="public", website=True)
    def thanks(self, res='', **kwargs):
        # return request.render("sitio_imagen.thanks")

        sale_order_id = request.session.get('sale_last_order_id')

        if res == 'lp':
            request.website.sale_reset()
            return request.render("sitio_imagen.thanks_leolandia")
        elif res == 'p':
            request.website.sale_reset()
            return request.render("sitio_imagen.thanks")
        elif res == 'pt':
            sale_order_id = request.session.get('sale_last_order_id')
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            return request.render("website_sale.confirmation", {'order': order})
        elif res == 'ptl':
            return request.render("sitio_imagen.thanks_transferer")
        else:
            request.website.sale_reset()
            return request.render("sitio_imagen.thanks")

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
        print('shop override')

        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']

        category = Category.search([('code', '=', 'cat_2_4')], limit=1)

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
            'url_get': '/shop/libros-chicos-2-4',
            'id_svg': 'yellow_cloud'
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

        category = Category.search([('code', '=', 'cat_4_5')], limit=1)

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
            'url_get': '/shop/libros-chicos-4-5',
            'id_svg': 'pink_cloud'
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

        category = Category.search([('code', '=', 'cat_6_7')], limit=1)

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
            'url_get': '/shop/libros-chicos-6-7',
            'id_svg': 'violet_cloud'
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

        category = Category.search([('code', '=', 'cat_8_9')], limit=1)

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
            'url_get': '/shop/libros-chicos-8-9',
            'id_svg': 'blue_cloud'
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

        category = Category.search([('code', '=', 'cat_10_12')], limit=1)

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
            'url_get': '/shop/libros-chicos-10-12',
            'id_svg': 'orange_cloud'
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
            pdf, _ = request.env.ref('sitio_imagen.action_report_saleorder_imagen').sudo().render_qweb_pdf(
                [sale_order_id])
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return request.redirect('/shop')

    # CONFIRMACION DE PAGO
    #
    def send_email_leolandia(self, partner_name, partner_email):
        template = request.env['template.email.website'].sudo().search([
            ('name', '=', 'TEMP-EMAIL-LEO'),
            ('activo', '=', True),
            ('website_id', '=', request.website.id)
        ])

        if template:
            string_email = str(template.html).replace('partner_name', partner_name)
            request.website.send_email("Confirmación de pago", partner_email,
                                       string_email)

            logging.warning("Email enviado a {0}".format(partner_email))

    def send_email_transfer(self, partner_name, partner_email, order_referen, price):
        template = request.env['template.email.website'].sudo().search([
            ('name', '=', 'TEMP-EMAIL-TRANSFER'),
            ('activo', '=', True),
            ('website_id', '=', request.website.id)
        ])

        if template:
            string_email = str(template.html).replace('partner_name', partner_name) \
                .replace("order_referen", order_referen).replace("price_curso", '{:.2f}'.format(price))
            request.website.send_email("Datos de pago", partner_email, string_email)

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

    def validate_order(self, sale_order_id):
        order = request.env['sale.order'].sudo().browse(sale_order_id)
        payment_tx_id = order.get_portal_last_transaction()
        res = '0'

        if payment_tx_id.state == 'done' and payment_tx_id.acquirer_id.provider == 'paypal':
            logging.warning("Pago realizado con metodo paypal")

            if order.invoice_status != 'invoice':
                logging.warning("Orden aun no facturada")
                order.action_confirm()  # confirmamos la orden de venta
                order._force_lines_to_invoice_policy_order()
                invoices = order._create_invoices()
                payment_tx_id.invoice_ids = [(6, 0, invoices.ids)]
                request.website.sale_reset()
                logging.warning("Orden confirmada y factura creada...")

            if not order.partner_id.email_pago_enviado:
                logging.warning("Email de confirmacion de pago no enviado")

                if order.only_services:
                    logging.warning("Orden unicamente con servicios")

                    # consulto el curso leolandia
                    curso = request.env['curso.producto'].sudo().search([
                        ('codigo', '=', 'CUR-LEO-01')
                    ])

                    if any(line.product_id.barcode == curso.producto.barcode for line in order.order_line):
                        self.send_email_leolandia(order.partner_id.name, order.partner_id.email)
                        logging.warning("Actualizando cliente...")
                        self.update_partner(order.partner_id.id, estado='pagado', email_pago=True)
                        res = 'lp'
                    else:
                        res = 'p'
                        logging("Correo no definido para otros servicios")
                else:
                    res = 'p'
                    logging.warning("Correo no definido para productos almacenables")
            else:
                # consulto el curso leolandia
                curso = request.env['curso.producto'].sudo().search([
                    ('codigo', '=', 'CUR-LEO-01')
                ])

                if any(line.product_id.barcode == curso.producto.barcode for line in order.order_line):
                    res = 'lp'
                else:
                    res = 'p'

        if payment_tx_id.state == 'pending' and payment_tx_id.acquirer_id.provider == 'transfer':
            logging.warning('Pending Transfer')
            res = 'pt'
            if not order.partner_id.email_transfer:
                logging.warning("Email de transferencia bancaria no enviado")

                # consulto el curso leolandia
                curso = request.env['curso.producto'].sudo().search([
                    ('codigo', '=', 'CUR-LEO-01')
                ])

                if any(line.product_id.barcode == curso.producto.barcode for line in order.order_line):
                    logging.warning("Transferencia leolandia")
                    self.send_email_transfer(order.partner_id.name, order.partner_id.email, order.name,
                                             order.amount_total)
                    self.update_partner(order.partner_id.id, estado='pendiente', email_pago=False,
                                        email_transfer=True)
                    res = 'ptl'

        return res

    @http.route()
    def payment_confirmation(self, **post):
        logging.warning("Override Payment Confirmation")

        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            res = self.validate_order(sale_order_id)
            return request.redirect('/shop/thanks?res={0}'.format(res))
        else:
            return request.redirect('/shop')

    @http.route(['/test_email'], type='http', auth="public", website=True)
    def final_shop_curso(self, **kwargs):
        template = request.env['template.email.website'].sudo().search([
            ('name', '=', 'TEMP-EMAIL-LEO'),
            ('activo', '=', True),
            ('website_id', '=', request.website.id)
        ])

        if template:
            string_email = str(template.html).replace('partner_name', 'José Musun')
            request.website.send_email("Confirmación de inscripción", "stdjosemusun@gmail.com", string_email)

    @http.route(['''/shop/recovery_cart''', '''/shop/recovery_cart/<string:access_token>'''], type='http',
                auth="public", website=True)
    def recovery_cart(self, access_token):
        abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)

        if abandoned_order:
            request.session['sale_order_id'] = abandoned_order.id

            return request.redirect('/shop/payment')
