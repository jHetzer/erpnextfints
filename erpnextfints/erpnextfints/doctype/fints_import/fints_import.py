# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime


class FinTSImport(Document):
    def validate_past(self, date, field_name):
        if isinstance(date, str):
            date = get_datetime(date).date()
        if date >= now_datetime().date():
            frappe.msgprint(
                _("'{0}' needs to be in the past").format(field_name)
            )
            return False
        if (now_datetime().date() - date).days >= 90:
            frappe.msgprint(
                _("'{0}' is more then 90 days in the past").format(field_name)
            )
            return False
        return True

    def before_save(self):
        status = True
        if self.from_date is not None:
            status = self.validate_past(self.from_date, "From Date")

            if self.to_date is not None:
                from_date = get_datetime(self.from_date).date()
                if from_date > get_datetime(self.to_date).date():
                    status = False
                    frappe.msgprint(_(
                        "'From Date' needs to be further in the past"
                        " then 'To Date'"))
        if self.to_date is not None:
            if not self.validate_past(self.to_date, "To Date"):
                status = False

        if not status:
            frappe.throw(_("Validation of dates failed"))

    def validate(self):
        self.before_save()
