# -*- coding: utf-8 -*-
# Copyright 2017 Comunitea - <comunitea@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MRP Picking per Mrp",
    "summary": "Not acumulative picking in mrp productions",
    "version": "8.0.1.0.0",
    "category": "Production",
    "website": "https://www.comunitea.com",
    "author": "Kiko Sánchez",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
    ],
    "data": [
        'views/mrp_production.xml',
    ],
}
