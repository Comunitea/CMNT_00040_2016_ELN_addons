# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, models, fields
import openerp.addons.decimal_precision as dp

from openerp.exceptions import ValidationError

INDEX_SELECTION = [('inc','Inc'), ('dec','Dec'), ('both', 'Both')]
INDEX_ROTATION = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]


class StockLocationRack(models.Model):

    _name = "stock.location.rack"
    _order = 'sequence, name'

    name = fields.Char('Name', required=1)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    code = fields.Char('Code', required=1)
    sequence = fields.Integer('Sequence', default=0)
    x_number = fields.Integer('Pos X', required=1)
    y_number = fields.Integer('Pos Y count', required=1)
    z_number = fields.Integer('Pos Z count', required=1)
    index = fields.Selection(INDEX_SELECTION, 'Index pos')
    parent_id = fields.Many2one('stock.location', string="Parent location", required=1)
    rotation = fields.Selection(INDEX_ROTATION, 'Rotation', default='medium')
    need_check = fields.Boolean("Need check", default=True, help="Need check in PDA")


    @api.multi
    def update_rack_loc_ids(self):

        for rack in self:
            if rack.sequence:
                raise ValidationError("Need sequence in rack. Please reorder racks if neccesary")
            usage = self.parent_id.usage
            loc_order = str(rack.sequence).zfill(3)
            for y in range(1, rack.y_number+1):
                for z in range(1, rack.z_number+1):
                    pos_x = str(rack.x_number).zfill(2)
                    pos_y = str(y).zfill(2)
                    pos_z = str(z).zfill(2)
                    order_z = rack.z_number - z
                    if rack.index=='inc':
                        order_y = y
                        order_y2 = False
                    elif rack.index == 'dec':
                        order_y = rack.y_number - y
                        order_y2 = False
                    else:
                        order_y = y
                        order_y2 = rack.y_number - y
                    picking_order_dec = ''
                    picking_order = int('{}{}{}'.format(loc_order, str(order_y).zfill(2), str(order_z).zfill(2)))
                    if order_y2:
                        picking_order_dec = int('{}{}{}'.format(loc_order, str(order_y2).zfill(2), str(order_z).zfill(2)))

                    name = "{} / {}.{}".format(rack.name, pos_y, pos_z)
                    loc_barcode = "{}.{}.{}".format(rack.code, pos_y, pos_z)

                    vals = {'name': name,
                            'warehouse_id': rack.warehouse_id.id,
                            'location_id': rack.parent_id.id,
                            'usage': usage,
                            'posx': rack.x_number,
                            'posy': y,
                            'posz': z,
                            'loc_barcode': loc_barcode,
                            'picking_order': picking_order,
                            'picking_order_dec': picking_order_dec,
                            'rotation': rack.rotation,
                            'rack_id': rack.id,
                            'company_id': False}
                    domain_location = [('loc_barcode','=', loc_barcode), ('warehouse_id', '=', rack.warehouse_id.id)]
                    location = self.env['stock.location'].search(domain_location)
                    if location:
                        location.write(vals)
                    else:
                        self.env['stock.location'].create(vals)


class StockLocation (models.Model):

    _inherit = 'stock.location'


    picking_order = fields.Integer('Picking order')
    picking_order_dec = fields.Integer('Picking order (two side location)')
    rack_id = fields.Many2one('stock.location.rack')
    warehouse_id = fields.Many2one('stock.warehouse')
    rotation = fields.Selection(INDEX_ROTATION, 'Rotation')
    need_check = fields.Boolean("Need check", default=False, help="Need check in ")


    @api.model
    def name_to_id(self, name):
        location = self.search([('loc_barcode', '=', name)], limit=1)
        return location and location.id or False




