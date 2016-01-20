# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com). All Rights Reserved
#    Copyright (c) 2011 Pexego Sistemas Informáticos. All Rights Reserved
#                       Alberto Luengo Cabanillas <alberto@pexego.es>
#    Copyright (c) 2015 QUIVAL, S.A. - All Rights Reserved
#                       Pedro Gómez <pegomez@elnogal.com>
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

{
	"name" : "Partner Risk Analysis",
	"version" : "2.0",
	"description" : """This module adds a new button in the partner form to analyze current state of a partner risk.
It reports current information regarding amount of debt in invoices, orders, etc.

It also modifies the workflow of sale orders by adding a new step when partner's risk is exceeded.

Developed for Trod y Avia, S.L.""",
	"author" : "NaN·tic / Pedro G.",
	"website" : "http://www.NaN-tic.com",
	"depends" : [ 
		'base', 
		'account', 
		'sale',
		'account_payment',
		'nan_partner_risk_insurance',
	], 
	"category" : "Custom Modules",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		'security/risk_security.xml',
		'wizard/open_risk_window_view.xml',
		'risk_view.xml',
		'sale_view.xml',
		'sale_workflow.xml',
	],
	"active": False,
	"installable": True
}
