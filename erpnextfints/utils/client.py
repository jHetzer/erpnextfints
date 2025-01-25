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
    :return: List of max 10 transactions and all new payment entries
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
    from erpnextfints.utils.fints_controller import FinTSController, TanInteractionRequired

    interactive = {"docname": user_scope, "enabled": True}

    try:
        return {
            "accounts": FinTSController(fints_login,
                                        interactive).get_fints_accounts()
        }
    except TanInteractionRequired:
        pass


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


@frappe.whitelist()
def has_page_permission(page_name):
    """Check if user has permission for a page doctype.

    Based on frappe/desk/desk_page.py
    :param page_doc: page doctype object
    :type page_doc: page doctyp
    :return: Boolean
    """
    from erpnextfints.utils.bank_account_controller import \
        has_page_permission
    return has_page_permission(page_name)


@frappe.whitelist()
def add_payment_reference(payment_entry, sales_invoice):
    """Add payment reference to payment entry for sales invoice.

    Create new bank account and if missing a bank entry.
    :param payment_entry: json formated payment_doc
    :param sales_invoice: json formated bank information
    :type payment_entry: str
    :type sales_invoice: str
    :return: Payment reference name
    """
    from erpnextfints.utils.assign_payment_controller import \
        AssignmentController

    return AssignmentController().add_payment_reference(
        payment_entry,
        sales_invoice
    )


@frappe.whitelist()
def auto_assign_payments():
    """Query assignable payments and create payment references.

    Try to assign payments in 3 steps:
    1. payment to sale assingment
    2. multiple payments to sale assingment
    3. payment to sale assingment

    :return: List of assigned payments
    """
    from erpnextfints.utils.assign_payment_controller import \
        AssignmentController

    return AssignmentController().auto_assign_payments()


@frappe.whitelist()
def resolve_tan_interaction(fints_login: str, values: str | dict):
    """
    When a user was requested to perform a 2FA, this method is called as a callback to resolve the interaction.

    This method is called twice:
    1. When the user is requested to choose the TAN mode
    2. When the user is requested to mark the required action (confirm access or enter TAN) as performed

    :param values: dict containing the interaction values
        The following keys are expected:
            possible_tan_modes: list of possible TAN modes
            tan_mode: selected TAN mode
            mfa_confirmation: Indicates Step 2, that the user performed the MFA (or entered a TAN)
            tan: entered TAN (optional: if TAN needs to be entered for chosen tan_mode)
    :return: doesn't return anything, but raises information via socket to the user
    """
    from erpnextfints.utils.fints_controller import FinTSController, TanInteractionRequired # , InitFailedException

    if isinstance(values, str):
        values = frappe.parse_json(values)

    tan_mode = None

    if values.get("possible_tan_modes") and values.get("tan_mode") and isinstance(values["possible_tan_modes"], list) and isinstance(values["tan_mode"], str):
        tan_mode = values["tan_mode"]

    tan_medium = values.get("tan_medium") if tan_mode else None

    try:
        if values.get("mfa_confirmation"):
            # for tan generators, the TAN is permitted here (may also be empty for Mobile TAN 2.0)
            FinTSController(fints_login, {"docname": fints_login, "enabled": True}, tan_mode=tan_mode, tan_medium=tan_medium, tan=values.get("tan"))

        else:
            # get index of tan_mode in possible_tan_modes
            FinTSController(fints_login, {"docname": fints_login, "enabled": True}, tan_mode=tan_mode, tan_medium=tan_medium)

    except TanInteractionRequired:
        pass # will have triggered user interaction via socket
