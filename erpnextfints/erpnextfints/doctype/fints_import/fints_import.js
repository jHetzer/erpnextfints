// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

frappe.ui.form.on('FinTS Import', {
	onload: function(frm) {
		frappe.realtime.on("fints_import_progress", function(data) {
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
	},
	refresh: function(frm) {
		if(frm.doc.fints_login && frm.doc.docstatus == 0){
			frm.page.set_primary_action(__("Start Import"), function() {
				frm.events.call_import_transaction(frm);
			}).addClass('btn btn-primary');
		}
	},
	fints_login: function(frm) {
		if(frm.doc.fints_login){
			frm.save()
		}
	},
	from_date: function(frm) {
		if(frm.doc.fints_login){
			frm.save()
		}
	},
	import_transaction: function(frm){
		//frappe.show_progress(frm.docname,1,100,"Connect via FinTS")
		frm.events.call_import_transaction(frm);
		/*
		if (frm.doc.__unsaved){
			frm.save().then(() => {
				frm.events.call_import_transaction(frm);
			})
		}else{
			frm.events.call_import_transaction(frm);
			//frappe.hide_progress();
		}
		*/

	},
	call_import_transaction: function(frm){
		//frappe.show_progress(frm.docname,1,100,"Connect via FinTS")
		frappe.call({
			method:"erpnextfints.erpnextfints.doctype.fints_import.fints_import.import_transactions",
			args: {
				'docname': frm.docname,
				"fints_login": frm.doc.fints_login
			},
			callback: function(r) {
				console.log(r)
				frappe.hide_progress();
			},
			error: function(r) {
				console.log(r);
				frappe.hide_progress();
			}
		})
	}
});
