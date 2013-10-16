#This file is part nereid_basket module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from nereid import render_template, request, flash
from nereid.globals import session
from nereid.helpers import url_for
from werkzeug import redirect

from trytond.pyson import Eval
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.modules.nereid.i18n import _

from decimal import Decimal

__all__ = ['Basket']
__metaclass__ = PoolMeta


class Basket:
    __name__ = 'sale.basket'
    nereid_user = fields.Many2One('nereid.user', 'User',
        domain=[('party', '=', Eval('party'))],
        states={
            'readonly': (Eval('state') != 'draft') 
            }, depends=['state', 'party'])
    nereid_sessionid = fields.Char('Session ID', select=True,
        states={
            'readonly': (Eval('state') != 'draft') 
            }, depends=['state'])

    @classmethod
    def render(cls):
        """
        Get basket items
        """
        if not request.nereid_website.basket_guest and request.is_guest_user:
            return redirect(url_for('nereid.website.login'))

        Company = Pool().get('company.company')
        Product = Pool().get('product.product')

        products = []
        upsells = []
        untaxed_amount = Decimal('0.0')
        total_amount = Decimal('0.0')

        company = Transaction().context.get('company')
        if company:
            currency = Company(company).currency

        if not request.is_guest_user:
            baskets = cls.search([
                ('nereid_sessionid', '=', session.sid),
                ('nereid_user', '=', None),
                ('state', '=', 'draft')
                ])
            if baskets:
                cls.write(baskets, {
                    'party': request.nereid_user.party.id,
                    'nereid_user': request.nereid_user.id,
                    })

        if request.is_guest_user:
            condition = [
                ('nereid_sessionid', '=', session.sid),
                ('state', '=', 'draft')
                ]
        else:
            condition = [
                ('nereid_user', '=', request.nereid_user),
                ('state', '=', 'draft')
                ]
        lines = cls.search(condition)

        for line in lines:
            untaxed_amount += line.untaxed_amount
            total_amount += line.total_amount
        if lines:
            line = lines[0]
            currency = line.currency
        for line in lines:
            products.append(line.product)
        if products:
            upsells = Product.get_product_upsells(products, exclude=True)
        return render_template('basket.jinja', lines=lines, upsells=upsells,
            untaxed_amount=untaxed_amount, total_amount=total_amount,
            currency=currency)

    @classmethod
    def add(cls):
        """
        Add or update basket item
        """
        if not request.nereid_website.basket_guest and request.is_guest_user:
            return redirect(url_for('nereid.website.login'))

        Product = Pool().get('product.product')

        to_create = []
        form = request.form.copy()

        for key, value in form.iteritems():
            try: 
                qty = int(value)
            except ValueError:
                continue

            if qty <= 0:
                continue

            clause = [
                ('product.code', '=', key),
                ('state', '=', 'draft')
                ]
            if request.is_guest_user:
                clause.append(('nereid_sessionid', '=', session.sid))
            else:
                clause.append(('nereid_user', '=', request.nereid_user))

            lines = cls.search(clause, limit=1)

            if lines:
                cls.write(lines, {'quantity': qty})
            else:
                product, = Product.search(['code', '=', key], limit=1)
                unit_price = Product.get_sale_price([product],
                    qty or 0)[product.id]
                to_create.append({
                    'party': request.nereid_user.party.id,
                    'nereid_user': request.nereid_user.id,
                    'quantity': qty,
                    'product': product.id,
                    'unit_price': unit_price,
                    'nereid_sessionid': session.sid,
                    })

        if to_create:
            cls.create(to_create)
        flash(_('Your cart are updated'))
        return redirect(
            request.args.get('next', url_for('sale.basket.render'))
            )

    @classmethod
    def remove(cls, id):
        """
        Remove basket item
        """
        if not request.nereid_website.basket_guest and request.is_guest_user:
            return redirect(url_for('nereid.website.login'))

        try: 
            id = int(id)
        except ValueError:
            return redirect(
                request.args.get('next', url_for('sale.basket.render'))
                )

        clause = [
            ('id', '=', id),
            ('state', '=', 'draft')
            ]
        if request.is_guest_user:
            clause.append(('nereid_sessionid', '=', session.sid))
        else:
            clause.append(('nereid_user', '=', request.nereid_user))
        lines = cls.search(clause)
        if lines:
            cls.delete(lines)
        flash(_('Your cart are removed some products'))
        return redirect(
            request.args.get('next', url_for('sale.basket.render'))
            )

    @classmethod
    def checkout(cls):
        """
        Create Sale from basket
        """
        if request.is_guest_user:
            return redirect(url_for('nereid.website.login'))

        baskets = cls.search([
            ('nereid_user', '=', request.nereid_user),
            ('state', '=', 'draft')
            ])
        if not baskets:
            return redirect(url_for('sale.basket.render'))
        sale, = cls.create_sale(baskets)

        return redirect(url_for('sale.sale.render', uri=sale.id))
