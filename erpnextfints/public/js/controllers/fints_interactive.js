// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt

frappe.provide("erpnextfints.interactive");

erpnextfints.interactive = {
	progressbar: function(frm) {
		frappe.realtime.on("fints_progressbar", function(data) {
			if(data.docname === frm.doc.name) {
				if(data.reload && data.reload === true) {
					frm.reload_doc();
				}
				if(data.progress==100) {
					frappe.hide_progress();
				} else {
					frappe.show_progress(data.docname,data.progress,100,data.message);
				}
			}
		});
	},
}
