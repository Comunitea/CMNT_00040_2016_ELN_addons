# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    gs1 = fields.Char(string='GS1 code',
      help='AECOC GS1 code of the Company. Used to coding GTIN-13, GTIN-14, GS1-128, SSCC, etc.')
