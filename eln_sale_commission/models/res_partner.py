# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class ResPartner(models.Model):
    """Commission like property field"""
    _inherit = "res.partner"

    commission = fields.Many2one(company_dependent=True, required=False)
    atypical = fields.Float('Atypical')
