# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import os
import json
import frappe
from frappe import _
from frappe.utils.csvutils import getlink


class BankAccountController:
    def __init__(self):
        self.cur_dir = os.path.dirname(__file__)

    def new_bank_account(self, payment_doc, bankData):
        """Create new bank account.

        Create new bank account and if missing a bank entry.
        :param payment_doc: json formated payment_doc
        :param bankData: json formated bank information
        :type payment_doc: str
        :type bankData: str
        :return: Dict with status and bank details
        """
        try:
            payment_doc = json.loads(payment_doc)
            bankData = json.loads(bankData)

            bankName = bankData.get('name')
            if not frappe.db.exists('Bank', {'bank_name': bankName}):
                frappe.get_doc({
                    'doctype': 'Bank',
                    'bank_name': bankName}
                ).submit()
            gl_account = None
            if payment_doc.get('payment_type') == "Pay":
                gl_account = payment_doc.get('paid_from')
            else:
                gl_account = payment_doc.get('paid_to')

            bankAccount = ({
                'doctype': 'Bank Account',
                'account_name': payment_doc.get('sender'),
                'account': gl_account,
                'bank': bankData.get('name'),
                'party_type': payment_doc.get('party_type'),
                'party': payment_doc.get('party'),
                'iban': payment_doc.get('iban'),
                'bank_account_no': bankData.get('64061854'),
                'swift_number': bankData.get('bic'),
                'is_company_account': False,
                'is_default': False,
            })
            bankAccountName = ''.join([
                payment_doc.get('sender'), " - ",
                bankData.get('name')
            ])
            if not frappe.db.exists('Bank Account', bankAccountName):
                newBankAccount = frappe.get_doc(bankAccount)
                newBankAccount.submit()
                frappe.msgprint(_("Successfully created Bank Account"))
                return {"bankAccount": newBankAccount, "status": True}
            else:
                frappe.msgprint(_("Bank account already exists"))
                return {
                    "bankAccount": frappe.get_doc(
                        'Bank Account',
                        bankAccountName),
                    "status": True
                }
        except Exception as e:
            frappe.throw(_(
                "Could not create bank account with error: {0}"
            ).format(e))

    def get_missing_bank_accounts(self):
        """Get possibly missing bank accounts.

        Query payment entries for missing bank accounts.
        :return: List of payment entry data
        """
        file_path = os.path.join(self.cur_dir, './sql/bank_wizard.sql')
        filehandle = open(file_path)
        sqlQuery = filehandle.read()
        filehandle.close()
        return frappe.db.sql(sqlQuery, as_dict=True)


def validate_unique_iban(doc, method):
    """Bank Account IBAN should be unique."""
    doctype = "Bank Account"
    bankAccountName = frappe.db.exists(doctype, {"iban": doc.iban})
    if bankAccountName:
        frappe.throw(_("IBAN already exists in bank account: {0}").format(
            getlink(doctype, bankAccountName)
        ))
