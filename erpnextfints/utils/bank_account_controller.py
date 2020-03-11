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
            ignore_permissions = False
            payment_doc = json.loads(payment_doc)

            if has_page_permission('bank_account_wizard'):
                ignore_permissions = True
            else:
                raise PermissionError(_(
                    'User {0} does not have access to this method'
                ).format(frappe.bold(frappe.session.user)))

            # Check for FinTS Login default parties
            if frappe.get_all(
                'FinTS Login',
                or_filters=[
                    ['default_customer', '=', payment_doc.get('party')],
                    ['default_supplier', '=', payment_doc.get('party')]
                ],
                ignore_permissions=ignore_permissions
            ):
                raise ValueError(_(
                    'Default party selected, please change party'
                ))

            bankData = json.loads(bankData)
            bankName = bankData.get('name')

            if not frappe.db.exists('Bank', {'bank_name': bankName}):
                frappe.get_doc({
                    'doctype': 'Bank',
                    'bank_name': bankName}
                ).insert(ignore_permissions=ignore_permissions)

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
                'bank_account_no': bankData.get('bankCode'),
                'swift_number': bankData.get('bic'),
                'is_company_account': False,
                'is_default': False,
            })
            bankAccountName = ''.join([
                payment_doc.get('sender'), " - ",
                bankData.get('name')
            ])
            if not frappe.db.exists('Bank Account', bankAccountName):
                newBankAccount = frappe.get_doc(
                    bankAccount,
                    ignore_permissions=ignore_permissions
                )
                newBankAccount.insert(ignore_permissions)
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


def has_page_permission(page_name):
    """Check if user has permission for a page doctype.

    Based on frappe/desk/desk_page.py
    :param page_doc: page doctype object
    :type page_doc: page doctyp
    :return: Boolean
    """
    if (
        frappe.session.user == 'Administrator'
        or 'System Manager' in frappe.get_roles()
    ):
        return True

    page_doc = frappe.get_doc('Page', page_name)
    page_roles = [d.role for d in page_doc.get('roles')]
    if page_roles:
        if frappe.session.user == 'Guest' and 'Guest' not in page_roles:
            return False
        elif set(page_roles).intersection(set(frappe.get_roles())):
            # check if roles match
            return True
    else:
        return False


def validate_unique_iban(doc, method):
    """Bank Account IBAN should be unique."""
    doctype = "Bank Account"
    bankAccountName = frappe.db.get_value(
        doctype,
        filters={
            "iban": doc.iban,
            "name": [
                "!=",
                doc.name
            ]
        })
    if bankAccountName:
        frappe.throw(_("IBAN already exists in bank account: {0}").format(
            getlink(doctype, bankAccountName)
        ))
