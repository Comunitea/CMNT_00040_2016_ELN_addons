# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


REASON_TYPES = [
    ('technical', 'Technical'),
    ('organizative', 'Organizative')
]


class StopReason(models.Model):
    _name = 'stop.reason'
    _order = 'name'

    name = fields.Char('Reason')
    reason_type = fields.Selection(REASON_TYPES, 'Type',
        default='technical')
    workcenter_ids = fields.Many2many(
        'mrp.workcenter',
        rel='stop_reasons_workcenter_rel',
        id1='reason_id', id2='workcenter_id'
    )
