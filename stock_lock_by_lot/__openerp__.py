# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# © 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": 'Stock Lock By Lot',
    "description": 'Lock stock moves by lot - Simplified version based on the OCA module stock_lot_lock',
    "version": '8.0.1.0.1',
    "author": 'OdooMRP team,'
              'Avanzosc,'
              'Serv. Tecnol. Avanzados - Pedro M. Baeza,'
              'Odoo Community Association (OCA),'
              'Pedro Gómez',
    "website": 'http://www.elnogal.com',
    "category": 'Warehouse Management',
    "depends": [
        'stock',
        'product',
        'mrp',
    ],
    "data": [
        'security/security.xml',
        'wizard/mrp_product_produce_view.xml',
        'wizard/stock_transfer_details_view.xml',
        'wizard/wiz_lock_by_lot_view.xml',
        'views/product_category_view.xml',
        'views/stock_production_lot_view.xml',
        'views/stock_quant_view.xml',
    ],
    "installable": True,
    "license": 'AGPL-3',
}
