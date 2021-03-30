# -*- coding: utf-8 -*-
# Copyright 2019 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResCompnay(models.Model):
    _inherit = 'res.company'

    sales_app_product_pricelist = fields.Many2one(
        comodel_name='product.pricelist',
        string="Default Pricelist",
        domain=[('type','=','sale'),('in_app','=',True)])
