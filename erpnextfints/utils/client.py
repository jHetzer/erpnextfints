# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def import_fints_transactions(fints_import, fints_login, user_scope):
    """Create payment entries by FinTS transactions.

    :param fints_import: fints_import doc name
    :param fints_login: fints_login doc name
    :param user_scope: Current open doctype page
    :type fints_import: str
    :type fints_login: str
    :type user_scopet: str
    :return: List of max 10 transcations and all new payment entries
    """
    from erpnextfints.utils.fints_controller import FinTSController
    interactive = {"docname": user_scope, "enabled": True}

    return FinTSController(fints_login, interactive) \
        .import_fints_transactions(fints_import)


@frappe.whitelist()
def get_accounts(fints_login, user_scope):
    """Create payment entries by FinTS transactions.

    :param fints_login: fints_login doc name
    :param user_scope: Current open doctype page
    :type fints_login: str
    :type user_scopet: str
    :return: FinTS accounts json formated
    """
    from erpnextfints.utils.fints_controller import FinTSController
    interactive = {"docname": user_scope, "enabled": True}

    return {
        "accounts": FinTSController(
            fints_login,
            interactive).get_fints_accounts()
    }


@frappe.whitelist()
def new_bank_account(payment_doc, bankData):
    """Create new bank account.

    Create new bank account and if missing a bank entry.
    :param payment_doc: json formated payment_doc
    :param bankData: json formated bank information
    :type payment_doc: str
    :type bankData: str
    :return: Dict with status and bank details
    """
    from erpnextfints.utils.bank_account_controller import \
        BankAccountController
    return BankAccountController().new_bank_account(payment_doc, bankData)


@frappe.whitelist()
def get_missing_bank_accounts():
    """Get possibly missing bank accounts.

    Query payment entries for missing bank accounts.
    :return: List of payment entry data
    """
    from erpnextfints.utils.bank_account_controller import \
        BankAccountController
    return BankAccountController().get_missing_bank_accounts()
