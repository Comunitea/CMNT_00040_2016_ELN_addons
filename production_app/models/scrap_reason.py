# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


REASON_TYPES = [
    ('technical', 'Technical'),
    ('organizative', 'Organizative')]


class ScrapReason(models.Model):
    _name = 'scrap.reason'

    name = fields.Char('Reason')
