# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _
from fints.client import FinTS3PinTanClient, FinTSClientMode
from dateutil.relativedelta import relativedelta
from frappe.utils import now_datetime
from frappe.utils.file_manager import save_file
from erpnextfints.utils.import_payment import ImportPaymentEntry
import frappe
import json
import mt940


class FinTSController:
    def __init__(self, fints_login_docname, interactive=False):
        self.fints_login = frappe.get_doc("FinTS Login", fints_login_docname)
        self.name = self.fints_login.name
        self.interactive = FinTSInteractive(
            interactive
        )
        self.__init_fints_connection()
        self.__init_tan_processing()
        with self.fints_connection:
            self.__get_fints_accounts()

    def __init_fints_connection(self):
        """Private: Initialise new fints connection.

        :return: None
        """
        self.interactive.show_progress_realtime(
            _("Initialise connection"), 10, reload=False
        )
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
        except Exception as e:
            frappe.throw(_(
                "Could not conntect to fints server with error<br>{0}"
            ).format(e))

    def __init_tan_processing(self):
        """Show a progressbar on client side.

        :todo: Implement PSD2 requirements
        :return: None
        """
        self.interactive.show_progress_realtime(
            _("Initialise TAN settings"), 20, reload=False
        )
        self.fints_connection.fetch_tan_mechanisms()

        if self.fints_connection.init_tan_response:
            raise NotImplementedError

    def __get_fints_accounts(self):
        """Fetch FinTS Accounts.

        :return: None
        """
        self.interactive.show_progress_realtime(
            _("Loading accounts"), 30, reload=False
        )
        if not hasattr(self, 'fints_accounts'):
            try:
                self.fints_accounts = self.fints_connection.get_sepa_accounts()
            except Exception as e:
                frappe.throw(_(
                    "Could not load sepa accounts with error:<br>{0}"
                ).format(e))

    def __get_fints_account_by_property(self, property, value):
        try:
            account = None
            for acc in self.fints_accounts:
                if getattr(acc, property) == value:
                    account = acc
                    break
        except AttributeError:
            frappe.throw(_(
                "SEPA account object has no property '{0}'"
            ).format(property))
        # Account can be None
        return account

    def get_fints_connection(self):
        """Get the FinTS Connection object.

        :return: FinTS3PinTanClient
        """
        return self.fints_connection

    def get_fints_accounts(self):
        """Get FinTS Accounts.

        :return: List of SEPAAccount objects.
        """
        self.interactive.show_progress_realtime(
            _("Loading accounts completed"), 100, reload=False
        )
        return self.fints_accounts

    def get_fints_account_by_iban(self, iban):
        """Get FinTS account by iban number.

        :param iban: bank iban number
        :type iban: str
        :return: SEPAAccount
        """
        return self.__get_fints_account_by_property("iban", iban)

    def get_fints_account_by_nr(self, account_nr):
        """Get FinTS account by account number.

        :param account_nr: bank account number
        :type account_nr: str
        :return: SEPAAccount
        """
        return self.__get_fints_account_by_property(
            "accountnumber",
            account_nr
        )

    def get_fints_transactions(self, start_date=None, end_date=None):
        """Get FinTS transcations.

        The code is not allowing to fetch transcation which are older
        than 90 days. Also only transcation from atleast one day ago can be
        fetched

        :param start_date: Date to start the fetch
        :param end_date: Date to end the fetch
        :type start_date: date
        :type end_date: date
        :return: Transaction as json object list
        """
        if start_date is None:
            start_date = now_datetime().date() - relativedelta(days=90)

        if end_date is None:
            end_date = now_datetime().date() - relativedelta(days=1)

        if (end_date - start_date).days >= 90:
            raise NotImplementedError

        with self.fints_connection:
            account = self.get_fints_account_by_iban(
                self.fints_login.account_iban)
            return frappe.json.loads(
                frappe.json.dumps(
                    self.fints_connection.get_transactions(
                        account,
                        start_date,
                        end_date
                    ),
                    cls=mt940.JSONEncoder
                )
            )

    def import_fints_transactions(self, fints_import):
        """Create payment entries by FinTS transactions.

        :param fints_import: fints_import doc name
        :type fints_import: str
        :return: List of max 10 transcations and all new payment entries
        """
        try:
            self.interactive.show_progress_realtime(
                _("Start transcation import"), 40, reload=False
            )
            curr_doc = frappe.get_doc("FinTS Import", fints_import)
            new_payments = None
            tansactions = self.get_fints_transactions(
                curr_doc.from_date,
                curr_doc.to_date
            )
            try:
                save_file(
                    fints_import + ".json",
                    json.dumps(
                        tansactions, ensure_ascii=False
                    ).replace(",", ",\n").encode('utf8'),
                    'FinTS Import',
                    fints_import,
                    folder='Home/Attachments/FinTS',
                    decode=False,
                    is_private=1,
                    df=None
                )
            except Exception as e:
                frappe.throw(_("Failed to attach file"), e)

            if(len(tansactions) == 0):
                frappe.msgprint(_("No transcations found"))
            else:
                if(len(tansactions) == 1):
                    curr_doc.start_date = tansactions[0]["date"]
                    curr_doc.end_date = tansactions[0]["date"]
                else:
                    curr_doc.start_date = tansactions[0]["date"]
                    curr_doc.end_date = tansactions[-1]["date"]

                importer = ImportPaymentEntry(
                    self.fints_login,
                    self.interactive
                )
                importer.fints_import(tansactions)

                if len(importer.payment_entries) == 0:
                    frappe.msgprint(_("No new payments found"))
                else:
                    # Save payment entries
                    frappe.db.commit()

                    frappe.msgprint(_(
                        "Found a total of '{0}' payments"
                    ).format(
                        len(importer.payment_entries)
                    ))
                new_payments = importer.payment_entries

            curr_doc.submit()
            self.interactive.show_progress_realtime(
                _("Payment entry import completed"), 100, reload=False
            )
            return {
                "transactions": tansactions[:10],
                "payments": new_payments
            }
        except Exception as e:
            frappe.throw(_(
                "Error parsing transactions<br>{0}"
            ).format(str(e)), frappe.get_traceback())


class FinTSInteractive:
    def __init__(self, configuration):
        if not configuration:
            self.docname = None
            self.enabled = False
        else:
            self.docname = configuration["docname"]
            self.enabled = configuration["enabled"]
        self.progress = 0

    def set_interactive_mode(self, enable):
        """Turn on/off interactive mode.

        :param enable: Turn on/off interactive mode
        :type enable: bool
        :return: None
        """
        self.enabled = enable

    def get_interactive_mode(self):
        """Get interactive mode.

        :return: bool
        """
        return self.enabled

    def show_progress_realtime(self, message, progress, reload=False):
        """Show a progressbar on client side.

        :param message: Message to display under the bar
        :param progress: 0 - 100
        :param reload: Reload the doc form, , defaults to False
        :type message: str
        :type progress: int
        :type reload: bool, optional
        :return: None
        """
        if self.enabled:
            frappe.publish_realtime(
                "fints_progressbar", {
                    "progress": progress,
                    "docname": self.docname,
                    "message": message,
                    "reload": False
                }, user=frappe.session.user)
