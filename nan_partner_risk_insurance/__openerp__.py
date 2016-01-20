# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Albert Cervera i Areny (http://www.nan-tic.com). All Rights Reserved
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
	"name" : "Partner Risk Insurance",
	"version" : "2.0",
	"description" : """This module adds a new tab in the partner form to introduce risk insurance information.""",
	"author" : "NaN·tic / Pedro G.",
	"website" : "http://www.NaN-tic.com",
	"depends" : [ 
		'base', 
	], 
	"category" : "Custom Modules",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		'partner_view.xml',
	],
	"active": False,
	"installable": True
}
