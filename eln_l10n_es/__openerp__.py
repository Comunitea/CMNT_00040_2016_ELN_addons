# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "El Nogal - Spanish Charts of Accounts (PGCE 2008)",
    "version": "8.0.0.0.0",
    "category": 'Accounting & Finance',
    "description": """l10n_es - module customizations for El Nogal""",
    "author": 'Pedro Gómez',
    "website": 'www.elnogal.com',
    "license": "AGPL-3",
    "depends": [
        "l10n_es",
        "l10n_es_dua",
        "l10n_es_aeat_sii",
        "l10n_es_dua_sii",
        "l10n_es_aeat_mod303",
    ],
    "init_xml": [],
    "data": [
        "data/tax_codes_common.xml",
        "data/taxes_common.xml",
        "data/fiscal_positions_common.xml",
        "data/fiscal_position_taxes_dua.xml",
        "data/aeat_sii_map_data.xml",
        "data/products_dua.xml",
        "data/tax_code_map_mod303_data.xml",
        "data/aeat_export_mod303_2023_data.xml",
    ],
    "demo_xml": [],
    "installable": True,
}
