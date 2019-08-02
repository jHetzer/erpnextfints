// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

frappe.ui.form.on('FinTS Login', {
	onload: function(frm) {
		frappe.realtime.on("fints_login_progress", function(data) {
			if (data.fints_login === frm.doc.name) {
				if (data.reload && data.reload === true) {
					frm.reload_doc();
				}
				if(data.progress==100) {
					frappe.hide_progress();
				} else {
					frappe.show_progress(data.fints_login,data.progress,100,data.message)
				}
			}
		});
		if(frm.doc.account_nr){
			frm.toggle_display("transaction_settings_section",true)
		}else{
			frm.toggle_display("transaction_settings_section",false)
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
		//frm.set_df_property("account_nr","options",frm.fields_dict.account_nr.value)
		//if(frm.fields_dict.account_nr.df.reqd && )
		//frm.toggle_reqd("account_nr",true);
		if(frm.doc.iban_list){
			frm.set_df_property("account_nr","options",JSON.parse(frm.doc.iban_list))
		}
		if(!frm.doc.account_nr){
			frm.toggle_display("account_nr",false);
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
		var field = "default_customer"
		if(frm.doc.enable_received){
			frm.toggle_reqd(field,true);
		}else{
			frm.toggle_reqd(field,false);
		}
	},
	enable_pay: function(frm){
		var field = "default_supplier"

		if(frm.doc.enable_pay){
			frm.toggle_reqd(field,true);
		}else{
			frm.toggle_reqd(field,false);
		}
	},
	/*account_nr: function(frm) {
		if(frm.doc.account_nr){
			frm.save();
		}
	},*/
	get_accounts: function(frm) {
		frappe.show_progress(frm.docname,10,100,"Prepare Connection")
		if (frm.doc.__unsaved){
			frm.save().then(() => {
				frm.events.call_get_login_accounts(frm);
			})
		}else{
			frm.events.call_get_login_accounts(frm);
			frappe.hide_progress();
		}
	},
	call_get_login_accounts: function(frm){
		frappe.call({
			method:"erpnextfints.erpnextfints.doctype.fints_login.fints_login.get_accounts",
			args: {
				'docname': frm.docname
			},
			callback: function(r) {
				console.log(r)
				frm.toggle_display("account_nr",true)
				frm.set_value("account_nr","");
				frm.set_value("failed_connection",0);

				var ibanList = r.message.accounts.map(x => x[0]);
				frm.set_df_property("account_nr","options",ibanList);
				//frm.toggle_reqd("account_nr",true);
				//console.log(JSON.stringify(ibanList));
				frm.set_value("iban_list", JSON.stringify(ibanList));
				frm.toggle_reqd("account_nr",true);
			},
			error: function(r) {
				console.log(r);
				frappe.hide_progress();
				frm.set_df_property("account_nr","options","")
				frm.toggle_display("account_nr",false)

				frappe.run_serially([
					() => frm.set_value("account_nr",""),
					() => frm.set_value("iban_list",""),
					() => frm.set_value("failed_connection",frm.doc.failed_connection + 1),
					() => frm.save(),
				]);
			}
		})
	}
});
