// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

{% include "erpnextfints/public/js/controllers/fints_interactive.js" %}

frappe.ui.form.on('FinTS Login', {
	onload: function(frm) {
		erpnextfints.interactive.progressbar(frm);
		if(frm.doc.account_iban){
			frm.toggle_display("transaction_settings_section",true);
		}else{
			frm.toggle_display("transaction_settings_section",false);
		}
	},
	setup: function(frm) {
		frm.set_query("erpnext_account", function() {
			return {
				filters: {
					'account_type': 'Bank',
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});
	},
	refresh: function(frm) {
		frm.events.enable_received(frm);
		frm.events.enable_pay(frm);
		// frm.set_df_property("account_nr","options",frm.fields_dict.account_nr.value)
		// if(frm.fields_dict.account_nr.df.reqd && )
		// frm.toggle_reqd("account_nr",true);
		if(frm.doc.iban_list){
			frm.set_df_property("account_iban","options",JSON.parse(frm.doc.iban_list));
		}
		if(!frm.doc.account_iban){
			frm.toggle_display("account_iban",false);
		}
		/*
		if(!frm.doc.__unsaved && frm.doc.account_nr){
			frm.toggle_display("transaction_settings_section",true)
		}else{
			frm.toggle_display("transaction_settings_section",false)
		}
		*/
	},
	enable_received: function(frm){
		frm.toggle_reqd("default_customer", frm.doc.enable_received);
	},
	enable_pay: function(frm){
		frm.toggle_reqd("default_supplier", frm.doc.enable_pay);
	},
	/* account_nr: function(frm) {
		if(frm.doc.account_nr){
			frm.save();
		}
	},*/
	get_accounts: function(frm) {
		if (frm.doc.__unsaved){
			frm.save().then(() => {
				frm.events.call_get_login_accounts(frm);
			});
		}else{
			frm.events.call_get_login_accounts(frm);
			frappe.hide_progress();
		}
	},
	call_get_login_accounts: function(frm){
		frappe.call({
			method:"erpnextfints.utils.client.get_accounts",
			args: {
				'fints_login': frm.doc.name,
				'user_scope': frm.doc.name
			},
			callback: function(r) {
				// console.log(r)
				frm.toggle_display("account_iban",true);
				frm.set_value("account_iban","");
				frm.set_value("failed_connection",0);

				var ibanList = r.message.accounts.map(x => x[0]);
				frm.set_df_property("account_iban","options",ibanList);
				// frm.toggle_reqd("account_nr",true);
				// console.log(JSON.stringify(ibanList));
				frm.set_value("iban_list", JSON.stringify(ibanList));
				frm.toggle_reqd("account_iban",true);
			},
			error: function(/* r */) {
				// console.log(r);
				frappe.hide_progress();
				frm.set_df_property("account_iban","options","");
				frm.toggle_display("account_iban",false);

				frappe.run_serially([
					() => frm.set_value("account_iban",""),
					() => frm.set_value("iban_list",""),
					() => frm.set_value("failed_connection",frm.doc.failed_connection + 1),
					() => frm.save(),
				]);
			}
		});
	}
});
