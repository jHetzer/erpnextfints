from __future__ import unicode_literals

import frappe

def execute():
    frappe.reload_doc("erpnextfints", "doctype", "fints_login")
    frappe.db.sql("""
            Update
                `tabFinTS Login`
            set
                `tabFinTS Login`.enable_pay = 0
            where
                `tabFinTS Login`.default_supplier IS NULL
                and `tabFinTS Login`.enable_pay = 1""")
