# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-TODAY
#        Pexego Sistemas Informáticos (http://www.pexego.es) All Rights Reserved
#        $Javier Colmenero Fernández$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'EDI',
    'version': '0.1',
    'category': 'Tools',
    'description': """
        Importar/Exportar archivos EDI (Ventas, Albaranes y facturas)

        Este módulo modifica los objetos:
            Factura e impuestos(account.invoice, account.tax, account.invoice.tax): Se añade descuento global y se modifican los calculos de la factura.
            Empresa (res.partner), añade el campo GLN (Numero de localizacion global).
            Direccion (res.partner.address), añade el campo GLN, posición fiscal y código de centro.
            Tipo de pago (account.payment.type), añade un campo 'codigo EDI' para identificar con EDI cada tipo de pago.
            Unidades de medida (product.uom), añade un campo 'código EDI' para identificar con edi cada unidad de medida.

        Es necesario que asigne los valores correctos a los campos GLN para que el modulo funcione correctamente.
        Otros campos necesarios:
            -En el partner:
                Sección: Código de sección proveedor (para factura)
                Código de departamento: (Para factura y albarán)
                Marca de lote: Marca número de lote (Para albarán)
                Fecha requerida: Para las facturas
                Nombre de fichero: Para factura/albarán
            -En el tipo de pago: Código edi(42,14E)
            -En la unidad de medida: codigo edi(KGM, PCE)
            -En los impuestos: Código edi(VAT)
            -En la compañia:
                Código edi para el nombre de fichero:(Q,V)
                Código GS1

    """,
    'author': 'Pexego Sistemas Informáticos',
    'website': 'https://www.pexego.es',
    # 'depends': ['base', 'account', 'sale', 'account_payment', 'account_payment_extension','sale_payment', 'picking_invoice_rel'],
    'depends': ['base', 'account', 'sale', 'account_payment', 'account_payment_extension','sale_payment'],
    'init_xml': [],
    # 'update_xml': [
    #     'security/ir.model.access.csv',
    #     'eln_edi_view.xml',
    #     'eln_edi_data.xml',
    #     'wizard/edi_import_view.xml',
    #     'wizard/edi_export_view.xml',
    #     'wizard/stock_pack_moves_view.xml',
    #     'stock_view.xml',
    # ],
    'demo_xml': [],
    'installable': True,
    'certificate': '',
}
