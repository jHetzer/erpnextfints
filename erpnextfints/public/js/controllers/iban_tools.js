// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

frappe.provide("erpnextfints.iban_tools");

erpnextfints.iban_tools = {
	// https://stackoverflow.com/questions/21928083/iban-validation-check
	isValidIBANNumber: function(input) {
		var CODE_LENGTHS = {
			AD: 24, AE: 23, AT: 20, AZ: 28, BA: 20, BE: 16, BG: 22, BH: 22, BR: 29,
			CH: 21, CR: 21, CY: 28, CZ: 24, DE: 22, DK: 18, DO: 28, EE: 20, ES: 24,
			FI: 18, FO: 18, FR: 27, GB: 22, GI: 23, GL: 18, GR: 27, GT: 28, HR: 21,
			HU: 28, IE: 22, IL: 23, IS: 26, IT: 27, JO: 30, KW: 30, KZ: 20, LB: 28,
			LI: 21, LT: 20, LU: 20, LV: 21, MC: 27, MD: 24, ME: 22, MK: 19, MR: 27,
			MT: 31, MU: 30, NL: 18, NO: 15, PK: 24, PL: 28, PS: 29, PT: 25, QA: 29,
			RO: 24, RS: 22, SA: 24, SE: 24, SI: 19, SK: 24, SM: 27, TN: 24, TR: 26
		};
		// var iban = String(input).toUpperCase().replace(/[^A-Z0-9]/g, ''), // keep only alphanumeric characters
		var iban = String(input).toUpperCase(), // keep only alphanumeric characters
			code = iban.match(/^([A-Z]{2})(\\\\d{2})([A-Z\\\\d]+)$/), // match and capture (1) the country code, (2) the check digits, and (3) the rest
			digits;
		// check syntax and length
		if (!code || iban.length !== CODE_LENGTHS[code[1]]) {
			return false;
		}
		// rearrange country code and check digits, and convert chars to ints
		digits = (code[3] + code[1] + code[2]).replace(/[A-Z]/g, function (letter) {
			return letter.charCodeAt(0) - 55;
		});
		// final check
		return erpnextfints.iban_tools.mod97(digits);
	},
	mod97: function(string) {
		var checksum = string.slice(0, 2), fragment;
		for (var offset = 2; offset < string.length; offset += 7) {
			fragment = String(checksum) + string.substring(offset, offset + 7);
			checksum = parseInt(fragment, 10) % 97;
		}
		return checksum;
	},
	// https://github.com/jquery-validation/jquery-validation/blob/master/src/additional/bic.js
	isValidBic: function(value) {
		return /^([A-Z]{6}[A-Z2-9][A-NP-Z1-9])(X{3}|[A-WY-Z0-9][A-Z0-9]{2})?$/.test( value.toUpperCase() );
	},
	getBankDetailsByIBAN: function(iban,callback) {
		const regex = /(?<=.{12})./gi;
		// https://openiban.com/#additional-info
		const supported_countries = [
			"BE", // Belgium
			"DE", // Germany
			"NL", // Netherlands
			"LU", // Luxembourg
			"CH", // Switzerland
			"AT", // Austria
			"LI", // Liechtenstein
		];
		var ibanCountryCode = iban.substring(0, 2).toUpperCase();
		if(supported_countries.indexOf(ibanCountryCode) > -1){
			var url = "https://openiban.com/validate/" +
				iban.replace(regex, "0") +
				"?getBIC=true&validateBankCode=true";
			$.ajax({
				url: url,
				type: 'GET',
				success: function(data){
					if(data.checkResults.bankCode){
						callback(data);
					}else{
						frappe.throw(__("Could not fetch bank details"));
					}
				},
				error: function(/* data */) {
					frappe.throw(__("Could not fetch bank details"));
				}
			});
		}else{
			frappe.throw(__("Unsupported IBAN country code: {0}",["<b>"+ibanCountryCode+"</b>"]));
		}
	},
	createPartyBankAccount: function(frm, bankInfo, resultCallback) {
		frappe.call({
			method: "erpnextfints.utils.client.new_bank_account",
			args: {
				payment_doc: frm,
				bankData: bankInfo.bankData,
			},
			callback: resultCallback,
			/*
			callback: function(r) {
				console.log(r);
			},*/
		});
	},
	setPartyBankAccount: function(frm, callback) {
		erpnextfints.iban_tools.getBankDetailsByIBAN(frm.doc.iban, function(data) {
			if (data.checkResults.bankCode) {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "FinTS Login",
						fields: ["default_customer", "default_supplier"],
					},
					// quiet: false,
					callback: function(r) {
						if (r.message.some(e =>
							e.default_customer === frm.doc.party ||
							e.default_supplier === frm.doc.party
						)) {
							frappe.msgprint(__("Default party selected, please change party"));
						} else {
							let dialog = new frappe.ui.Dialog({
								title: __('Create Bank Account'),
								fields: [{
									label: 'Bank Account',
									fieldtype: 'Section Break',
								}, {
									label: 'IBAN',
									fieldname: 'iban',
									fieldtype: 'Data',
									read_only: 1,
									default: frm.doc.iban,
								}, {
									label: 'BIC',
									fieldname: 'bic',
									fieldtype: 'Data',
									read_only: 1,
									default: frm.doc.bic,
								}, {
									label: 'Sender',
									fieldname: 'sender',
									fieldtype: 'Data',
									read_only: 1,
									default: frm.doc.sender,
								}, {
									fieldname: 'col_break1',
									fieldtype: 'Column Break',
								}, {
									label: 'Party',
									fieldname: 'party',
									fieldtype: 'Data',
									read_only: 1,
									default: frm.doc.party,
								}, {
									label: 'GL Account',
									fieldname: 'gl_account',
									fieldtype: 'Data',
									read_only: 1,
									default: (
										frm.doc.payment_type == "Pay"
									) ? frm.doc.paid_from : frm.doc.paid_to
								}, {
									label: 'Bank',
									fieldtype: 'Section Break',
								}, {
									label: 'Bank Name',
									fieldname: 'bank_name',
									fieldtype: 'Data',
									read_only: 1,
									default: data.bankData.name,
								}, {
									fieldname: 'col_break2',
									fieldtype: 'Column Break',
								}, {
									label: 'Bank Code',
									fieldname: 'bank_code',
									fieldtype: 'Data',
									read_only: 1,
									default: data.bankData.bankCode,
								}, ],
								primary_action_label: __('Submit'),
								primary_action: function(/* values */) {
									erpnextfints.iban_tools.createPartyBankAccount(frm.doc, data, callback);
									dialog.hide();
								},
							});
							dialog.show();
						}
					},
					// error: function(e){},
				});
			} else {
				frappe.throw(__("Could not fetch bank details"));
			}
		});
	}
};
