# -*- encoding: utf-8 -*-

# NO MIGRAR
# SUSTITUIDO POR ELN RISK
# A DESINTALAR

{
    "name": "Partner Risk Analysis",
    "version": "0.1",
    "description": """This module adds a new button in the partner form to analyze current state of a partner risk.
It reports current information regarding amount of debt in invoices, orders, etc.

It also modifies the workflow of sale orders by adding a new step when partner's risk is exceeded.

Developed for Trod y Avia, S.L.""",
    "author": "NaN·tic",
    "website": "http://www.NaN-tic.com",
    "depends": [
        'base',
        'account',
        'sale',
        'sale_stock',
        'partner_risk_insurance',  # Pedro dependency, for partner risk states
        # 'eln_risk',
    ],
    "category": "Custom Modules",
    # "data": [
    #     'security/nan_partner_risk_groups.xml',
    #     'wizard/open_risk_window_view.xml',
    #     'views/risk_view.xml',
    #     'views/sale_view.xml',
    #     'views/sale_workflow.xml',
    # ],
    "active": False,
    "installable": True
}
