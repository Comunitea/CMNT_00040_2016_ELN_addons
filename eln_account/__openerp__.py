# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2013 QUIVAL, S.A. All Rights Reserved
#    $Pedro Gómez Campos$ <pegomez@elnogal.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'eln_account',
    'version': '1.0',
    'author': 'Pedro Gómez',
    'website': 'www.elnogal.com',
    'category' : 'Accounting & Finance',
    'description': """Different account customizations for El Nogal""",
    'depends': [
        'account',
        'sale_early_payment_discount',
        'account_check_deposit',
        'eln_product',
        'product_ranking',
        'product_trademark',
        'account_refund_original',
        'commercial_route', # sólo para que genere correctamente el sql de la vista account.invoice.report cuando se hace update de commercial_route individualmente
    ],
    'data': [
        'views/account_invoice_view.xml',
        'report/account_invoice_report_view.xml',
    ],
    'installable': True,
    'images': [],
}
