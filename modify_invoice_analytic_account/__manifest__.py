# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2017 QUIVAL, S.A. All Rights Reserved
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
    'name': 'Modify Invoice Analytic Account',
     'version': '18.0.1.0.0',
    'author': 'Pedro Gómez',
    'category': 'Custom',
    'description': 'Modify invoice analytic account, analytic on related financial moves and recreate analytical moves',
    'website': 'http://www.elnogal.com',
    'license': 'AGPL-3',
    'depends': [
        'account'
    ],
    # 'data': [
    #     'wizard/modify_invoice_analytic_account_wzd_view.xml',
    # ],
    'installable': True,
    'auto_install': False
}
