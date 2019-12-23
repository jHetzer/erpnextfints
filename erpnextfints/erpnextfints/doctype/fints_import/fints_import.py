# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime


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
                from_date = get_datetime(self.from_date).date()
                if from_date > get_datetime(self.to_date).date():
                    status = False
                    frappe.msgprint(_(
                        "'From Date' needs to be further in the past"
                        " then 'To Date'"))
        if self.to_date is not None:
            if not self.validate_past(self.to_date):
                status = False
                frappe.msgprint(_("'To Date' needs to be in the past"))
        return status

    def validate(self):
        if not self.before_save():
            frappe.throw(_("Validation of dates failed"))
