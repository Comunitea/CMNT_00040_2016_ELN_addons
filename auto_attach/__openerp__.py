##############################################################################
#
# Copyright (c) 2007-2012 NaN Projectes de Programari Lliure, S.L.
#                         All Rights Reserved.
#                         http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


{
    "name": "Auto Attach",
    "version": "0.1",
    "description": """
This module makes it possible to automatically attach scanned documents to any 
object using NanScan [1].

[1] http://www.NaN-tic.com/nanscan
    """,
    "author": "NaN",
    "website": "http://www.NaN-tic.com",
    "depends": ["base"],
    "category": "Generic Modules/Attachments",
    "init_xml": [],
    "demo_xml": [],
    # "update_xml": [
    #     "wizard/process_document_queue_view.xml",
    #     "wizard/execute_documents_queue_view.xml",
    #     "wizard/analyze_documents_queue_view.xml",
    #     "wizard/verify_documents_queue_view.xml",
    #     "auto_attach_data.xml",
    #     "auto_attach_view.xml",
    #     "auto_attach_wizard.xml",
    #     "auto_attach_workflow.xml",
    #     "security/auto_attach_security.xml",
    #     "security/ir.model.access.csv",
    # ],
    "active": False,
    "installable": True
}
