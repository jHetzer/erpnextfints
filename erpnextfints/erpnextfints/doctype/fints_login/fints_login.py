# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from erpnextfints.utils.fints_wrapper import FinTSConnection


class FinTSLogin(Document):
    pass


@frappe.whitelist()
def get_accounts(docname, debug=False):
    fints_conn = FinTSConnection(docname)
    return {"accounts":fints_conn.get_fints_accounts()}
