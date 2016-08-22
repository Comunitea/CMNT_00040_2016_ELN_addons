# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api

class MrpProductionReopen(models.Model):

    _inherit = 'mrp.production'

    product_qty = fields.Float(states={'draft':[('readonly',False)], 'reopen':[('readonly',False)]}, readonly=True)
    product_uos_qty = fields.Float(states={'draft':[('readonly',False)], 'reopen':[('readonly',False)]}, readonly=True)
    state = fields.Selection(selection_add=[('reopen', 'Reopen')])
       
    @api.multi
    def action_reopen(self):

        self.state = 'reopen'
        
        for move in self.move_lines2:
            if move.state == "done":
                move.state = 'draft'
        
        for products in self.move_created_ids2:
            if products.state == "done":
                move.state = 'draft'
        
        return True

    @api.multi
    def action_redone(self):
        
        for move in self.move_lines:
            if move.state == "draft":
                move.state = 'done'
        
        for products in self.move_created_ids:
            if products.state == "draft":
                move.state = 'done'
        
        self.state = 'done'
        
        return True

