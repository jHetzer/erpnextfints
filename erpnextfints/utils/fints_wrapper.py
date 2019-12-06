# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
from frappe.model.document import Document
from dateutil.relativedelta import relativedelta
from frappe.utils import now_datetime
from fints.client import FinTS3PinTanClient
from fints.client import FinTSClientMode
import frappe
import mt940


class FinTSConnection:
    def __init__(self, fints_login_docname, debug=False):
        self.fints_login = frappe.get_doc("FinTS Login", fints_login_docname)
        self.name = self.fints_login.name
        self.debug = debug
        frappe.publish_realtime("fints_login_progress", {"progress": "40",
            "fints_login": self.name,"message": "Init connection", "reload": False}, user=frappe.session.user)
        self.__init_fints_connection()

    def __init_fints_connection(self):
        try:
            if not hasattr(self, 'fints_connection'):
                password = self.fints_login.get_password('fints_password')
                self.fints_connection = FinTS3PinTanClient(
                    self.fints_login.blz,
                    self.fints_login.fints_login,
                    password,
                    self.fints_login.fints_url,
                    mode=FinTSClientMode.INTERACTIVE
                )
                #self.fints_connection.set_tan_mechanism('942')
        except Exception as e:
            frappe.throw("Could not conntect to fints server with error<br>{0}".format(e))
    def get_fints_connection(self):
        return self.fints_connection

    def get_fints_accounts(self):
        frappe.publish_realtime("fints_login_progress", {"progress": "70",
            "fints_login": self.name,"message": "Load accounts", "reload": False}, user=frappe.session.user)
        if not hasattr(self, 'fints_accounts'):
            try:
                self.fints_accounts = self.fints_connection.get_sepa_accounts()
            except Exception as e:
                frappe.throw("Could not load sepa accounts with error:<br>{0}".format(e))

        frappe.publish_realtime("fints_login_progress", {"progress": "100",
            "fints_login": self.name,"message": "", "reload": False}, user=frappe.session.user)

        return self.fints_accounts

    def __get_fints_account_by_property(self, property, value):
        try:
            account = None
            for acc in self.get_fints_accounts():
                if getattr(acc,property) == value:
                    account = acc
                    break
        except AttributeError:
            frappe.throw(_("SEPA account object has no property '{0}'").format(property))
        # Account can be None
        return account

    def get_fints_account_by_iban(self, iban):
        return self.__get_fints_account_by_property("iban",iban)

    def get_fints_account_by_nr(self, account_nr):
        return self.__get_fints_account_by_property("accountnumber",account_nr)

    def get_fints_transactions(self, start_date=None, end_date=None):
        if end_date is None:
            end_date = now_datetime().date() - relativedelta(days=1)
        account = self.get_fints_account_by_iban(self.fints_login.account_nr)
        return frappe.json.loads(
            frappe.json.dumps(
                self.fints_connection.get_transactions(account, start_date, end_date),
                cls=mt940.JSONEncoder
            )
        )
