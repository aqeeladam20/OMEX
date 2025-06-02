frappe.provide("frappe.treeview_settings");

frappe.treeview_settings["Account"] = {
	breadcrumb: "Accounts",
	title: __("Chart of Accounts"),
	get_tree_root: false,
	filters: [
		{
			fieldname: "company",
			fieldtype: "Select",
			options: erpnext.utils.get_tree_options("company"),
			label: __("Company"),
			render_on_toolbar: true,
			default: erpnext.utils.get_tree_default("company"),
			on_change: function () {
				var me = frappe.treeview_settings["Account"].treeview;
				var company = me.page.fields_dict.company.get_value();
				if (!company) {
					frappe.throw(__("Please set a Company"));
				}
				frappe.call({
					method: "erpnext.accounts.doctype.account.account.get_root_company",
					args: {
						company: company,
					},
					callback: function (r) {
						if (r.message) {
							let root_company = r.message.length ? r.message[0] : "";
							me.page.fields_dict.root_company.set_value(root_company);

							frappe.db.get_value(
								"Company",
								{ name: company },
								"allow_account_creation_against_child_company",
								(r) => {
									frappe.flags.ignore_root_company_validation =
										r.allow_account_creation_against_child_company;
								}
							);
						}
					},
				});
			},
		},
		{
			fieldname: "root_company",
			fieldtype: "Data",
			label: __("Root Company"),
			hidden: true,
			disable_onchange: true,
		},
	],
	root_label: "Accounts",
	get_tree_nodes: "erpnext.accounts.utils.get_children",
	on_get_node: function (nodes, deep = false) {
		if (frappe.boot.user.can_read.indexOf("GL Entry") == -1) return;

		let accounts = [];
		if (deep) {
			// in case of `get_all_nodes`
			accounts = nodes.reduce((acc, node) => [...acc, ...node.data], []);
		} else {
			accounts = nodes;
		}

		frappe.db.get_single_value("Accounts Settings", "show_balance_in_coa").then((value) => {
			if (value) {
				const get_balances = frappe.call({
					method: "erpnext.accounts.utils.get_account_balances",
					args: {
						accounts: accounts,
						company: cur_tree.args.company,
					},
				});

				get_balances.then((r) => {
					if (!r.message || r.message.length == 0) return;

					for (let account of r.message) {
						const node = cur_tree.nodes && cur_tree.nodes[account.value];
						if (!node || node.is_root) continue;

						// show Dr if positive since balance is calculated as debit - credit else show Cr
						const balance = account.balance_in_account_currency || account.balance;
						const dr_or_cr = balance > 0 ? __("Dr") : __("Cr");
						const format = (value, currency) => format_currency(Math.abs(value), currency);

						if (account.balance !== undefined) {
							node.parent && node.parent.find(".balance-area").remove();
							const balanceHtml = 
								'<span class="balance-area balance-' + (balance > 0 ? 'dr' : 'cr') + '">' +
									(account.balance_in_account_currency
										? format(
												account.balance_in_account_currency,
												account.account_currency
										  ) + " / "
										: "") +
									format(account.balance, account.company_currency) +
									" " +
									dr_or_cr +
								"</span>";
							$(balanceHtml).insertBefore(node.$ul);
						}
					}
				});
			}
		});
	},

	show_table_view: function() {
		const company = frappe.treeview_settings["Account"].treeview.page.fields_dict.company.get_value();
		if (!company) {
			frappe.throw(__("Please select a Company"));
			return;
		}

		// Create table view dialog
		const table_dialog = new frappe.ui.Dialog({
			title: __("Chart of Accounts - Table View"),
			size: "extra-large",
			fields: [
				{
					fieldtype: "HTML",
					fieldname: "accounts_table"
				}
			]
		});

		// Get all accounts data
		frappe.call({
			method: "erpnext.accounts.utils.get_coa_table_data",
			args: {
				company: company
			},
			callback: function(r) {
				if (r.message) {
					frappe.treeview_settings["Account"].render_accounts_table(r.message, table_dialog);
				}
			}
		});

		table_dialog.show();
	},

	render_accounts_table: function(accounts_data, dialog) {
		const table_html = `
			<div class="accounts-table-container">
				<div class="table-header">
					<h4>${__("Chart of Accounts")}</h4>
					<div class="table-controls">
						<input type="text" placeholder="${__("Search accounts...")}" class="form-control account-search" style="width: 300px; display: inline-block;">
						<button class="btn btn-default btn-sm export-btn">${__("Export to Excel")}</button>
					</div>
				</div>
				<table class="table table-striped accounts-table">
					<thead>
						<tr>
							<th style="width: 15%">${__("Account Code")}</th>
							<th style="width: 40%">${__("Account Name")}</th>
							<th style="width: 15%">${__("Account Type")}</th>
							<th style="width: 10%">${__("Root Type")}</th>
							<th style="width: 20%">${__("Balance")}</th>
						</tr>
					</thead>
					<tbody class="accounts-tbody">
						${frappe.treeview_settings["Account"].generate_table_rows(accounts_data)}
					</tbody>
				</table>
			</div>
			<style>
				.accounts-table-container {
					padding: 20px;
				}
				.table-header {
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 20px;
					padding-bottom: 10px;
					border-bottom: 2px solid var(--border-color);
				}
				.table-controls {
					display: flex;
					gap: 10px;
					align-items: center;
				}
				.accounts-table {
					font-size: 14px;
					margin-bottom: 0;
				}
				.accounts-table th {
					background: var(--gray-100);
					font-weight: 600;
					color: var(--gray-800);
					border-bottom: 2px solid var(--border-color);
					padding: 12px 8px;
				}
				.accounts-table td {
					padding: 10px 8px;
					vertical-align: middle;
					border-bottom: 1px solid var(--subtle-gray);
				}
				.account-name-cell {
					font-weight: 500;
				}
				.account-code-cell {
					font-family: monospace;
					color: var(--gray-600);
					font-size: 13px;
				}
				.account-type-cell {
					font-size: 12px;
					padding: 4px 8px;
					border-radius: 4px;
					display: inline-block;
				}
				.root-type-asset { background: #e0f2fe; color: #0277bd; }
				.root-type-liability { background: #fce4ec; color: #ad1457; }
				.root-type-equity { background: #e8f5e8; color: #2e7d32; }
				.root-type-income { background: #e8f5e8; color: #2e7d32; }
				.root-type-expense { background: #ffebee; color: #c62828; }
				.balance-cell {
					text-align: right;
					font-family: monospace;
					font-weight: 500;
				}
				.balance-dr { color: #2e7d32; }
				.balance-cr { color: #c62828; }
				.account-level-0 { font-weight: 700; font-size: 15px; }
				.account-level-1 { font-weight: 600; padding-left: 20px; }
				.account-level-2 { padding-left: 40px; }
				.account-level-3 { padding-left: 60px; }
			</style>
		`;

		dialog.fields_dict.accounts_table.$wrapper.html(table_html);

		// Add search functionality
		dialog.$wrapper.find('.account-search').on('input', function() {
			const searchTerm = $(this).val().toLowerCase();
			dialog.$wrapper.find('.accounts-tbody tr').each(function() {
				const text = $(this).text().toLowerCase();
				$(this).toggle(text.includes(searchTerm));
			});
		});

		// Add export functionality
		dialog.$wrapper.find('.export-btn').on('click', function() {
			frappe.treeview_settings["Account"].export_accounts_to_excel(accounts_data);
		});
	},

	generate_table_rows: function(accounts_data) {
		let rows = '';
		accounts_data.forEach(account => {
			const account_code = account.account_number || '';
			const account_name = account.account_name || account.name;
			const account_type = account.account_type || '';
			const root_type = account.root_type || '';
			const balance_formatted = account.balance ? 
				`${format_currency(Math.abs(account.balance), account.company_currency)} ${account.balance > 0 ? 'Dr' : 'Cr'}` : 
				'';
			const level = account.level || 0;
			const balance_class = account.balance > 0 ? 'balance-dr' : 'balance-cr';
			const root_type_class = `root-type-${(root_type || '').toLowerCase()}`;

			rows += `
				<tr>
					<td class="account-code-cell">${account_code}</td>
					<td class="account-name-cell account-level-${level}">${account_name}</td>
					<td class="account-type-cell ${root_type_class}">${account_type}</td>
					<td class="root-type-cell">${root_type}</td>
					<td class="balance-cell ${balance_class}">${balance_formatted}</td>
				</tr>
			`;
		});
		return rows;
	},

	export_accounts_to_excel: function(accounts_data) {
		// Prepare data for export
		const export_data = accounts_data.map(account => ({
			'Account Code': account.account_number || '',
			'Account Name': account.account_name || account.name,
			'Account Type': account.account_type || '',
			'Root Type': account.root_type || '',
			'Balance': account.balance || 0,
			'Balance Formatted': account.balance ? 
				`${format_currency(Math.abs(account.balance), account.company_currency)} ${account.balance > 0 ? 'Dr' : 'Cr'}` : 
				''
		}));

		// Use Frappe's built-in export functionality
		frappe.tools.downloadify(export_data, ['Account Code', 'Account Name', 'Account Type', 'Root Type', 'Balance', 'Balance Formatted'], 'Chart of Accounts');
	},
	
	add_tree_node: "erpnext.accounts.utils.add_ac",
	menu_items: [
		{
			label: __("New Company"),
			action: function () {
				frappe.new_doc("Company", true);
			},
			condition: 'frappe.boot.user.can_create.indexOf("Company") !== -1',
		},
		{
			label: __("Table View"),
			action: function () {
				frappe.treeview_settings["Account"].show_table_view();
			},
		},
	],
	fields: [
		{
			fieldtype: "Data",
			fieldname: "account_name",
			label: __("New Account Name"),
			reqd: true,
			description: __(
				"Name of new Account. Note: Please don't create accounts for Customers and Suppliers"
			),
		},
		{
			fieldtype: "Data",
			fieldname: "account_number",
			label: __("Account Number"),
			description: __("Number of new Account, it will be included in the account name as a prefix"),
		},
		{
			fieldtype: "Check",
			fieldname: "is_group",
			label: __("Is Group"),
			description: __(
				"Further accounts can be made under Groups, but entries can be made against non-Groups"
			),
		},
		{
			fieldtype: "Select",
			fieldname: "root_type",
			label: __("Root Type"),
			options: ["Asset", "Liability", "Equity", "Income", "Expense"].join("\n"),
			depends_on: "eval:doc.is_group && !doc.parent_account",
		},
		{
			fieldtype: "Select",
			fieldname: "account_type",
			label: __("Account Type"),
			options: frappe.get_meta("Account").fields.filter((d) => d.fieldname == "account_type")[0]
				.options,
			description: __("Optional. This setting will be used to filter in various transactions."),
		},
		{
			fieldtype: "Float",
			fieldname: "tax_rate",
			label: __("Tax Rate"),
			depends_on: 'eval:doc.is_group==0&&doc.account_type=="Tax"',
		},
		{
			fieldtype: "Link",
			fieldname: "account_currency",
			label: __("Currency"),
			options: "Currency",
			description: __("Optional. Sets company's default currency, if not specified."),
		},
	],
	ignore_fields: ["parent_account"],
	onload: function (treeview) {
		frappe.treeview_settings["Account"].treeview = {};
		$.extend(frappe.treeview_settings["Account"].treeview, treeview);
		function get_company() {
			return treeview.page.fields_dict.company.get_value();
		}

		// Add table view button
		treeview.page.add_inner_button(
			__("Table View"),
			function () {
				frappe.treeview_settings["Account"].show_table_view();
			},
			__("View"),
			"primary"
		);

		// tools
		treeview.page.add_inner_button(
			__("Chart of Cost Centers"),
			function () {
				frappe.set_route("Tree", "Cost Center", { company: get_company() });
			},
			__("View"),
			"default",
			true
		);

		treeview.page.add_inner_button(
			__("Opening Invoice Creation Tool"),
			function () {
				frappe.set_route("Form", "Opening Invoice Creation Tool", { company: get_company() });
			},
			__("View"),
			"default",
			true
		);

		treeview.page.add_divider_to_button_group(__("View"));

		// financial statements
		for (let report of [
			"Trial Balance",
			"General Ledger",
			"Balance Sheet",
			"Profit and Loss Statement",
			"Cash Flow",
			"Accounts Payable",
			"Accounts Receivable",
		]) {
			treeview.page.add_inner_button(
				__(report),
				function () {
					frappe.set_route("query-report", report, { company: get_company() });
				},
				__("View")
			);
		}
	},
	post_render: function (treeview) {
		frappe.treeview_settings["Account"].treeview["tree"] = treeview.tree;
		if (treeview.can_create) {
			treeview.page.set_primary_action(
				__("New"),
				function () {
					let root_company = treeview.page.fields_dict.root_company.get_value();
					if (root_company) {
						frappe.throw(__("Please add the account to root level Company - {0}"), [
							root_company,
						]);
					} else {
						treeview.new_node();
					}
				},
				"add"
			);
		}
	},
	toolbar: [
		{
			label: __("Add Child"),
			condition: function (node) {
				return (
					frappe.boot.user.can_create.indexOf("Account") !== -1 &&
					(!frappe.treeview_settings[
						"Account"
					].treeview.page.fields_dict.root_company.get_value() ||
						frappe.flags.ignore_root_company_validation) &&
					node.expandable &&
					!node.hide_add
				);
			},
			click: function () {
				var me = frappe.views.trees["Account"];
				me.new_node();
			},
			btnClass: "hidden-xs",
		},
		{
			condition: function (node) {
				return !node.root && frappe.boot.user.can_read.indexOf("GL Entry") !== -1;
			},
			label: __("View Ledger"),
			click: function (node, btn) {
				frappe.route_options = {
					account: node.label,
					from_date: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
					to_date: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
					company:
						frappe.treeview_settings["Account"].treeview.page.fields_dict.company.get_value(),
				};
				frappe.set_route("query-report", "General Ledger");
			},
			btnClass: "hidden-xs",
		},
	],
	extend_toolbar: true,
};
