// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt
frappe.provide("erpnextfints.tools");


frappe.pages['assign_payment_entries'].on_page_load = function(wrapper) {
	erpnextfints.tools.assignWizardObj = new erpnextfints.tools.assignWizard(
		wrapper);
};

erpnextfints.tools.assignWizard = class assignWizard {
	constructor(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Assign Payment Wizard"),
			single_column: true
		});
		this.parent = wrapper;
		this.page = this.parent.page;
		this.make();
	}

	make() {
		const me = this;

		me.clear_page_content();
		me.make_assignWizard_tool();
		me.add_actions();
	}

	add_actions() {
		const me = this;

		me.page.show_menu();
		me.page.add_menu_item(__("Assign All"), function() {
			frappe.call({
				method: "erpnextfints.utils.client.auto_assign_payments",
				args: {},
				callback: function(r) {
					if(r.message.success === true ){
						var result = [];
						if(Array.isArray(r.message.payments) && r.message.payments.length ){
							result.push(__("Assingment was successfull"));
							r.message.payments.forEach(function(item) {
								result.push(
									__("Payment") + " " +
									get_doc_link("Payment Entry",item.PaymentName) +
									" " + __("from customer") + " " +
									get_doc_link("Customer",item.CustomerName) + " " +
									__("has been assinged to sale invoice") + " " +
									get_doc_link("Sales Invoice",item.SaleName)
								);
							});
						}else{
							result.push(__("No payments were found for assignment"));
						}
						erpnextfints.tools.assignWizardList.refresh();
						frappe.msgprint(result);
					} else {
						frappe.msgprint(__("Failed to assign payments"));
					}
				}
			});
		}, true);
	}

	clear_page_content() {
		const me = this;
		me.page.clear_fields();
		$(me.page.body).find('.frappe-list').remove();
	}

	make_assignWizard_tool() {
		const me = this;
		frappe.model.with_doctype("Sales Invoice", () => {
			erpnextfints.tools.assignWizardList = new erpnextfints.tools.AssignWizardTool({
				parent: me.parent,
				doctype: "Sales Invoice",
				page_title: __(me.page.title),
			});
			frappe.pages['assign_payment_entries'].refresh = function(/* wrapper */) {
				window.location.reload(false);
			};
		});
	}
};


erpnextfints.tools.AssignWizardTool = class AssignWizardTool extends frappe.views.BaseList {
	constructor(opts) {
		super(opts);
		this.show();
	}

	setup_defaults() {
		super.setup_defaults();
		this.page_length = 100;
		this.sort_by = 'customer';
		this.sort_order = 'asc';
		this.fields = ['name', 'customer', 'outstanding_amount','posting_date', 'due_date', 'currency'];
	}

	setup_view() {
		this.render_header();
	}

	setup_side_bar() {
		//
	}

	set_breadcrumbs() {
		frappe.breadcrumbs.add("ERPNextFinTS");
	}

	make_standard_filters() {
		//
	}

	freeze() {
		// this.$result.find('.list-count').html(`<span>${__('Refreshing')}...</span>`);
	}

	get_args() {
		const args = super.get_args();

		return Object.assign({}, args, {
			...args.filters.push(["Sales Invoice", "docstatus", "=", 1],
				["Sales Invoice", "outstanding_amount", ">", 0])
		});
	}

	get_row_call_args(customer) {
		return {
			method: "frappe.client.get_list",
			args: {
				doctype: "Payment Entry",
				fields: ["name","party","posting_date", "unallocated_amount","remarks"],
				filters: {
					"docstatus":0,
					"party":customer,
				},
				order_by: 'posting_date',
			},
			freeze: this.freeze_on_refresh || false,
			freeze_message: this.freeze_message || (__('Loading') + '...')
		};
	}

	render() {
		const me = this;
		this.$result.find('.list-row-container').remove();
		$('[data-fieldname="name"]').remove();
		$('[data-fieldname="status"]').remove();
		me.data.map((value) => {
			frappe.call(this.get_row_call_args(value.customer)).then(r => {
				if(Array.isArray(r.message) && r.message.length){
					const row = $('<div class="list-row-container">').data("data", value).appendTo(me.$result).get(0);
					new erpnextfints.tools.AssignWizardRow(row, value, r.message);
				}
			});
		});
	}

	render_header() {
		const me = this;
		if ($(this.wrapper).find('.payment-assign-wizard-header').length === 0) {
			me.$result.append(frappe.render_template("sale_invoice_header"));
		}
	}
};

erpnextfints.tools.AssignWizardRow = class AssignWizardRow {
	constructor(row, data, payments) {
		this.data = data;
		this.data.payments = payments;
		this.row = row;
		this.make();
		this.bind_events();
	}

	make() {
		$(this.row).append(frappe.render_template("sale_invoice_row", this.data));
	}

	bind_events() {
		const me = this;

		$(me.row).on('click', '.hide_row', function() {
			me.row.remove();
		});
		$(me.row).on('click', '.assign_payment', function() {
			frappe.call({
				method: "erpnextfints.utils.client.add_payment_reference",
				args: {
					"sales_invoice": me.data.name,
					"payment_entry": $(this).attr("data-name"),
				},
				callback(r) {
					var payment_entry_ref = r.message;
					if(payment_entry_ref.outstanding_amount == payment_entry_ref.allocated_amount){
						me.row.remove();
					}else{
						erpnextfints.tools.assignWizardList.refresh();
					}
				}
			});
		});
	}
};

function get_doc_link(doctype, name){
	return '<a href="#Form/' + doctype + '/' +
		name+'"><b>' +
		name + `</b></a>`;
}
