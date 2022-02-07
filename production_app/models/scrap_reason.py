# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ScrapReason(models.Model):
    _name = 'scrap.reason'

    name = fields.Char('Reason')
    workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        rel='scrap_reasons_workcenter_rel',
        id1='reason_id', id2='workcenter_id'
    )
