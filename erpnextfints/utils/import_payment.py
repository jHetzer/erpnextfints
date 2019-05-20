from __future__ import unicode_literals

import frappe
import hashlib


class ImportPaymentEntry:
    def __init__(self, fints_login, allow_error=False, debug=False):
        self.debug = debug
        self.allow_error = allow_error
        self.payment_entries = []
        self.fints_login = fints_login
        self.default_customer = fints_login.default_customer

    def get_customer_by_value(self, sender, iban=None):
        party = None
        is_default = False
        customer_name = frappe.get_value('Customer', sender, 'name')

        if iban:
            iban_sql_query = ("SELECT `name` " +
                        "FROM `tabCustomer` " +
                        "WHERE `iban` = '{0}'".format(iban))
            customer_by_iban = frappe.db.sql(iban_sql_query, as_dict=True)
            if len(customer_by_iban) == 1:
                party = customer_by_iban[0].name
        if not party and customer_name:
            party = customer_name
        if not party:
            party = self.default_customer
            is_default = True

        return {"is_default": is_default, "party": party}

    def fints_import(self, fints_transaction):
        total_items = len(fints_transaction)

        for idx,t in enumerate(fints_transaction):

            if t["status"].lower() == "c":
                amount = float(t["amount"]["amount"])
                customerMapping = t["applicant_name"]
                uniquestr = "{0},{1},{2},{3},{4}".format(
                    t["date"],
                    amount,
                    customerMapping,
                    t["posting_text"],
                    t['purpose']
                )
                transaction_id = hashlib.md5(uniquestr.encode('utf-8')).hexdigest()
                if not frappe.db.exists('Payment Entry', {'reference_no': transaction_id}):
                    new_payment_entry = frappe.get_doc({'doctype': 'Payment Entry'})
                    new_payment_entry.payment_type = "Receive"
                    new_payment_entry.party_type = "Customer";

                    # date is in YYYY.MM.DD (json)
                    new_payment_entry.posting_date = t["date"]
                    new_payment_entry.company = self.fints_login.company
                    new_payment_entry.paid_to = self.fints_login.erpnext_account
                    new_payment_entry.paid_amount = amount
                    new_payment_entry.received_amount = amount
                    new_payment_entry.iban = t["applicant_iban"]
                    new_payment_entry.bic = t["applicant_bin"]

                    customer = self.get_customer_by_value(
                        t["applicant_name"],
                        t["applicant_iban"]
                    )
                    new_payment_entry.party = customer["party"]
                    if customer["is_default"]:
                        remarks = ("Sender '{0}':<br>{1} {2}").format(
                            t["applicant_name"],
                            t["posting_text"],
                            t['purpose']
                        )
                    else:
                        remarks = "{0} {1}".format(t["posting_text"],t['purpose'])
                    new_payment_entry.remarks = remarks

                    new_payment_entry.reference_no = transaction_id
                    new_payment_entry.reference_date = t["date"]
                    if self.debug:
                        frappe.msgprint(frappe.as_json(new_payment_entry))
                    self.payment_entries.append(new_payment_entry.insert())
