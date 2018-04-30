
# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api



class PrintingPrinter(models.Model):
    """
    Printers
    """

    _inherit = 'printing.printer'

    barcode = fields.Char("Barcode")
    warehouse_location = fields.Many2one('stock.location')





class IrActionsReportXml(models.Model):
    
    _inherit = 'ir.actions.report.xml'
    

    @api.multi
    def behaviour(self):
        return super(IrActionsReportXml, self).behaviour()  

        
        results = super(IrActionsReportXml, self).behaviour()
        
        force_printer = self._context.get('force_printer', False)
        printer_id = self._context.get('printer_id', False)
        printer = self.env('printers').browse(printer_id)
        if force_printer and printer:
            for result in results:
                results[result]['printer']= printer
                results[result]['action']='server'
            return results    
        return super(IrActionsReportXml, self).behaviour()  
        
        