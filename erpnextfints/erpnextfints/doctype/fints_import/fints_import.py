# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime
from erpnextfints.utils.fints_wrapper import FinTSConnection
from erpnextfints.utils.import_payment import ImportPaymentEntry
from frappe.utils.file_manager import save_file
import json

class FinTSImport(Document):
    def validate_past(self, date):
        if isinstance(date, str):
            date = get_datetime(date).date()
        if date >= now_datetime().date():
            return False
        else:
            return True
    def before_save(self):
        status = True
        if self.from_date is not None:
            if not self.validate_past(self.from_date):
                status = False
                frappe.msgprint(_("'From Date' needs to be in the past"))
            if self.to_date is not None:
                if get_datetime(self.from_date).date() > get_datetime(self.to_date).date():
                    status = False
                    frappe.msgprint(_("'From Date' needs to be further in the past then 'To Date'"))
        if self.to_date is not None:
            if not self.validate_past(self.to_date):
                status = False
                frappe.msgprint(_("'To Date' needs to be in the past"))
        return status
    def validate(self):
        if not self.before_save():
            frappe.throw(_("Validation of dates failed"))

@frappe.whitelist()
def import_transactions(docname, fints_login, debug=False):
    try:
        curr_doc = frappe.get_doc('FinTS Import', docname)
        fints_conn = FinTSConnection(fints_login)
        tansactions = fints_conn.get_fints_transactions(
            curr_doc.from_date,
            curr_doc.to_date
        )
        try:
            save_file(
                docname + ".json",
                json.dumps(tansactions, ensure_ascii=False).replace(",",",\n").encode('utf8'),
                'FinTS Import',
                docname,
                folder='Home/Attachments/FinTS',
                decode=False,
                is_private=1,
                df=None
            )
        except Exception as e:
            frappe.throw("Failed to attach file",e)

        default_customer = fints_conn.fints_login.default_customer
        importer = ImportPaymentEntry(fints_conn.fints_login)
        importer.fints_import(tansactions)

        if len(importer.payment_entries) == 0:
            frappe.msgprint(_("No transcations found"))
        else:
            frappe.msgprint(_("Found a total of '{0}' payments").format(
                len(importer.payment_entries)
			))
            #frappe.msgprint(frappe.as_json(importer.payment_entries))
        if(len(tansactions) >= 2):
            curr_doc.start_date = tansactions[0]["date"]
            curr_doc.end_date = tansactions[-1]["date"]
        elif(len(tansactions) == 1):
            curr_doc.start_date = tansactions[0]["date"]
            curr_doc.end_date = tansactions[0]["date"]

        if debug:
            frappe.db.rollback()
        else:
            curr_doc.submit()
            frappe.db.commit()

        return {"transactions":tansactions[:10],"payments":importer.payment_entries}
    except Exception as e:
        frappe.throw(_("Error parsing transactions<br>{0}<br>{1}").format(str(e),frappe.get_traceback()))
