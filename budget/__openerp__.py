# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Arnaud Wüst, Guewen Baconnier, Leonardo Pistone
#    Copyright 2009-2014 Camptocamp SA
#
#    Copyright (C) 2015-2016 Comunitea Servicios Tecnológicos All Rights Reserved
#    $kiko Sánchez <kiko@comunitea.com>
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
 "version": "1.1",
 "author": "Camptocamp,Odoo Community Association (OCA)",
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

Active Budget Version
=====================

Every Budget has zero or one active Version. This is marked by a flag and that
can be set with a button. All other versions are disabled.

If a budget version is duplicated, the old one is automatically disabled as
well.

    """,
 "complexity": "expert",
 "depends": ["base",
             "account",
             "report_webkit",
             "analytic_multicurrency",
             ],
 "data": ["report/budget_header_webkit.xml",
          "budget_report.xml",
          "wizard/report_budget_view.xml",
          "budget_view.xml",
          "analytic_view.xml",
          "security/ir.model.access.csv",
          "security/security.xml",
          ],
 "installable": True,
 "application": True,
 }
