# -*- coding: utf-8 -*-
# Copyright 2023 El Nogal - Pedro Gómez <pegomez@elnogal.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "El Nogal Attendances customizations",
    "version": '8.0.1.0.1',
    "category": 'Human Resources',
    "description": """El Nogal Attendances customizations""",
    "author": 'Pedro Gómez',
    "website": 'www.elnogal.com',
    "depends": [
        'eln_hr',
        'hr_attendance',
        'hr_attendance_report',
     ],
    "init_xml": [],
    "data": [
        'views/hr_attendance_view.xml',
        'report/hr_employee_attendance_report.xml',
    ],
    "demo_xml": [],
    "installable": True
}
