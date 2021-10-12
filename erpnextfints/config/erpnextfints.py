# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

from frappe import _


def get_data():  # noqa: D103
    return[{
        "label": _("Integrations"),
        "icon": "octicon octicon-git-compare",
        "items": [{
            "type": "doctype",
            "name": "FinTS Import",
            "label": _("FinTS Import"),
            "description": _("FinTS Import")
        }, {
            "type": "doctype",
            "name": "FinTS Login",
            "label": _("FinTS Login"),
            "description": _("FinTS Login")
        }, {
            "type": "doctype",
            "name": "FinTS Schedule",
            "label": _("FinTS Schedule"),
            "description": _("FinTS Schedule")
        }]
    }, {
        "label": _("Tools"),
        "icon": "octicon octicon-git-compare",
        "items": [{
            "type": "page",
            "name": "bank_account_wizard",
            "label": _("Bank Account Wizard"),
            "description": _("Create bank accounts for parties")
        }, {
            "type": "page",
            "name": "assign_payment_entries",
            "label": _("Assign Payment Entries"),
            "description": _("Assign payment entries to sale invoices")
        }]
    }]
