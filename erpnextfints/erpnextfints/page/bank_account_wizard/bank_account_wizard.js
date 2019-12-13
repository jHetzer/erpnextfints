// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt
frappe.provide("erpnextfints.tools");

{% include "erpnextfints/public/js/controllers/iban_tools.js" %}

frappe.pages['bank_account_wizard'].on_page_load = function(wrapper) {
  erpnextfints.tools.bankWizardObj = new erpnextfints.tools.bankWizard(
    wrapper);
}

erpnextfints.tools.bankWizard = class BankWizard {
  constructor(wrapper) {
    this.page = frappe.ui.make_app_page({
      parent: wrapper,
      title: __("Bank Account Wizard"),
      single_column: true
    });
    this.parent = wrapper;
    this.page = this.parent.page;
    this.make();
  }

  make() {
    const me = this;

    me.$main_section = $(
      `<div class="reconciliation page-main-content"></div>`).appendTo(me
      .page.main);
    const empty_state = __(
      "Upload a bank statement, link or reconcile a bank account")
    me.$main_section.append(
      `<div class="flex justify-center align-center text-muted"
			style="height: 50vh; display: flex;"><h5 class="text-muted">${empty_state}</h5></div>`
    )
    me.clear_page_content();
    me.make_bankwizard_tool();
    me.add_actions();
  }

  add_actions() {
    const me = this;

    me.page.show_menu();

    me.page.add_menu_item(__("Create All"), function() {
      var items = erpnextfints.tools.bankWizardList.ref_items;

      function createAllBankAccount(dataArray, index){
        erpnextfints.iban_tools.setPartyBankAccount({
          doc: dataArray[index],
        }, function(e) {
          if (e.message.status == true) {
            //me.row.remove();
            erpnextfints.tools.bankWizardList.ref_items.splice(index,1);
            erpnextfints.tools.bankWizardList.render();
            setTimeout(
              function(){
                frappe.hide_msgprint();
                createAllBankAccount(dataArray, index + 1);
              }, 700
            );
          }
        });
      }
      createAllBankAccount(items, 0);

    }, true)
  }

  clear_page_content() {
    const me = this;
    me.page.clear_fields();
    $(me.page.body).find('.frappe-list').remove();
    me.$main_section.empty();
  }

  make_bankwizard_tool() {
    const me = this;
    frappe.call({
      method: "erpnextfints.utils.client.get_missing_bank_accounts",
      args: {},
      callback(r) {
        frappe.model.with_doctype("Payment Entry", () => {
          erpnextfints.tools.bankWizardList = new erpnextfints.tools.bankWizardTool({
              parent: me.parent,
              doctype: "Payment Entry",
              page_title: __(me.page.title),
              ref_items: r.message
            });
          frappe.pages['bank_account_wizard'].refresh = function(
            wrapper) {
            window.location.reload(false);
          }
        })
      }
    });
  }

}


erpnextfints.tools.bankWizardTool = class BankWizardTool extends frappe.views.BaseList {
  constructor(opts) {
    super(opts);
    this.show();
  }

  setup_defaults() {
    super.setup_defaults();
    //this.page_title = __("Bank Reconciliation");
    //this.doctype = 'Payment Entry';
    this.fields = ['party_type', 'party', 'sender', 'iban', 'bic',
      'paid_from', 'paid_to', 'payment_type'
    ]
  }

  setup_view() {
    this.render_header();
  }

  setup_side_bar() {
    //
  }

  make_standard_filters() {
    //
  }

  before_refresh() {
    //erpnextfints.tools.bankWizardObj.clear_page_content()
    frappe.model.with_doctype("Payment Entry", () => {
      frappe.call({
        method: "erpnextfints.utils.client.get_missing_bank_accounts",
        args: {},
        callback(r) {
          this.ref_items = r.message;
          //erpnextfints.tools.bankWizardObj.make();
        }
      });
    });
  }

  freeze() {
    this.$result.find('.list-count').html(
      `<span>${__('Refreshing')}...</span>`);
  }
  render() {
    const me = this;
    me.data = me.ref_items;
    //Add Query filter to party_type field
    me.page.fields_dict.party_type.df.get_query = function() {
      return {
        filters: {
          "name": ["in", ["Customer", "Supplier"]]
        }
      }
    }
    me.page.btn_secondary.click(function(e) {
      window.location.reload(false);
    });
    this.$result.find('.list-row-container').remove();
    $('[data-fieldname="name"]').remove();
    $('[data-fieldname="payment_type"]').remove();

    me.data.map((value) => {
      if (me.ref_items.filter(item => (item.name === value.name)).length >
        0) {
        const row = $('<div class="list-row-container">').data("data",
          value).appendTo(me.$result).get(0);
        //new erpnext.accounts.ReconciliationRow(row, value);
        new erpnextfints.tools.bankWizardRow(row, value);
      }
    })
  }

  render_header() {
    const me = this;
    if ($(this.wrapper).find('.bank-account-wizard-header').length === 0) {
      me.$result.append(frappe.render_template("bank_account_wizard_header"));
    }
  }
}
erpnextfints.tools.bankWizardRow = class BankWizardRow {
  constructor(row, data) {
    this.data = data;
    this.row = row;
    this.make();
    this.bind_events();
  }

  make() {
    $(this.row).append(frappe.render_template("bank_account_wizard_row",
      this.data))
  }

  bind_events() {
    const me = this;
    /*$(me.row).on('click', '.clickable-section', function() {
      me.bank_entry = $(this).attr("data-name");
      frappe.set_route("Form", "Payment Entry", me.bank_entry)
    })
		*/
    $(me.row).on('click', '.new-bank-account', function() {
      erpnextfints.iban_tools.setPartyBankAccount({
        doc: me.data
      }, function(e) {
        if (e.message.status == true) {
          var index = erpnextfints.tools.bankWizardList
            .ref_items.findIndex(x => x.name === me.data.name);
          if(index >= 0){
            erpnextfints.tools.bankWizardList
              .ref_items.splice(index,1);
          }
          me.row.remove();
        }
      });
    })
  }
}
