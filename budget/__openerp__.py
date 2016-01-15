# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Arnaud Wüst, Guewen Baconnier
#    Copyright 2009-2013 Camptocamp SA
#
#    Copyright (c) 2013 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    Copyright (C) 2015- Comunitea Servicios Tecnologicos All Rights Reserved
#    $Kiko Sánchez$ <kiko@comunitea.com>
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
{"name": "Multicurrency Analytic Budget",
 "version": "1.0",
 "author": "Camptocamp",
 "category": "Generic Modules/Accounting",
 "website": "http://camptocamp.com",
 "description": """
Budget Module
=============

Features:

* Create budget, budget items and budget versions.
* Budget versions are multi currencies and multi companies.

This module is for real advanced budget use, otherwise prefer to use the
OpenERP official one.
    """,
 "complexity": "expert",
 "depends": ["base",
             "account",
             "report_webkit",
             ],
 "data": ["budget_view.xml",
          "report/budget_header_webkit.xml",
          "budget_report.xml",

          "wizard/report_budget_view.xml",
          "analytic_view.xml",
          
          "security/ir.model.access.csv"
          ],
 "installable": True,
 "application": True,
 }
