# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


REASON_TYPES = [
    ('technical', 'Technical'),
    ('organizative', 'Organizative')]


class StopReason(models.Model):
    _name = 'stop.reason'

    name = fields.Char('Reason')
    reason_type = fields.Selection(REASON_TYPES, 'Type', default='technical')