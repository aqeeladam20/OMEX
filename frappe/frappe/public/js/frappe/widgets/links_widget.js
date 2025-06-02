import Widget from "./base_widget.js";

frappe.provide("frappe.utils");
frappe.provide("frappe.widget");

export default class LinksWidget extends Widget {
	constructor(opts) {
		opts.icon = opts.icon || "es-line-filetype";
		super(opts);
	}

	get_config() {
		return {
			name: this.name,
			links: JSON.stringify(this.links),
			link_count: this.links.length,
			label: this.label,
			hidden: this.hidden,
			description: this.description,
		};
	}

	set_body() {
		if (!this.options) {
			this.options = {};
			this.options.links = this.links;
		}
		this.widget.addClass("links-widget-box");

		// Add collapse functionality to widget header
		this.setup_collapsible_header();

		if (this.description) {
			const description = $(`
				<button class="btn-reset card-description-btn ml-2">
					${frappe.utils.icon("help", "sm")}
				</button>
			`).appendTo(this.widget.find(".widget-title"));

			description.popover({
				trigger: "hover",
				placement: "top",
				content: () => `<div class="card-description small">${__(this.description)}</div>`,
				html: true,
			});
		}

		// Create collapsible links container
		this.links_container = $('<div class="links-container"></div>').appendTo(this.body);

		const is_link_disabled = (item) => {
			return item.dependencies && item.incomplete_dependencies;
		};
		const disabled_dependent = (item) => {
			return is_link_disabled(item) ? "disabled-link" : "";
		};

		const get_link_for_item = (item) => {
			if (is_link_disabled(item)) {
				return `<span class="link-content ellipsis disabled-link">
					<span class="link-text">${item.link_title}</span>
					<div class="module-link-popover popover fade top in" role="tooltip" style="display: none;">
						<div class="arrow"></div>
						<h3 class="popover-title" style="display: none;"></h3>
						<div class="popover-content" style="padding: 12px;">
							<div class="small text-muted">${__("You need to create these first: ")}</div>
							<div class="small">${item.incomplete_dependencies.join(", ")}</div>
						</div>
					</div>
				</span>`;
			}

			if (item.youtube_id)
				return `
					<span class="link-content help-video-link ellipsis" data-youtubeid="${item.youtube_id}">
						<span class="link-text">${item.link_title}</span>
						<span class="link-arrow">${frappe.utils.icon("es-line-play", "xs")}</span>
					</span>
				`;

			return `
				<span class="link-content ellipsis">
					<span class="link-text">${item.link_title}</span>
					<span class="link-arrow">${frappe.utils.icon("es-line-arrow-up-right", "xs")}</span>
				</span>
			`;
		};

		this.link_list = this.links.map((item) => {
			const opts = {
				name: item.link_to,
				type: item.link_type,
				doctype: item.doctype,
				is_query_report: item.is_query_report,
				report_ref_doctype: item.report_ref_doctype,
			};

			if (item.link_type && item.link_type.toLowerCase() == "report" && !item.is_query_report) {
				opts.doctype = item.dependencies;
			}

			const route = frappe.utils.generate_route(opts);
			item.link_title = item.label ? item.label : item.name;

			const $link = $(`
				<a href="${route}" class="link-item ellipsis
					${item.onboard ? "onboard-spotlight" : ""} ${disabled_dependent(item)}"
					type="${item.type}" title="${item.link_title}"
				>
					${get_link_for_item(item)}
				</a>
			`);

			if (item.description) {
				$link.find(".link-text").popover({
					trigger: "hover",
					placement: "top",
					title: item.link_title,
					content: () =>
						`<div class="link-description small">${__(item.description)}</div>`,
					html: true,
					delay: { show: 600, hide: 100 },
				});
			}

			return $link;
		});
		
		if (this.in_customize_mode) {
			this.body.empty();
			this.links_container = $('<div class="links-container"></div>').appendTo(this.body);
		}
		this.link_list.forEach((link) => link.appendTo(this.links_container));
	}

	setup_collapsible_header() {
		if (!this.widget) return;
		
		const widgetTitle = this.widget.find('.widget-title');
		if (!widgetTitle.find('.collapse-indicator').length) {
			widgetTitle.append(`<span class="collapse-indicator">${frappe.utils.icon("chevron-down", "sm")}</span>`);
		}
		
		// Make header clickable
		widgetTitle.css('cursor', 'pointer');
		widgetTitle.off('click').on('click', (e) => {
			e.preventDefault();
			this.toggle_links_container();
		});
	}

	toggle_links_container() {
		if (!this.widget) return;
		
		const linksContainer = this.widget.find('.links-container');
		const indicator = this.widget.find('.collapse-indicator');
		
		if (linksContainer.hasClass('collapsed')) {
			// Expand
			linksContainer.removeClass('collapsed');
			indicator.removeClass('expanded').find('svg').css('transform', 'rotate(0deg)');
			this.widget.removeClass('widget-collapsed');
		} else {
			// Collapse  
			linksContainer.addClass('collapsed');
			indicator.addClass('expanded').find('svg').css('transform', 'rotate(180deg)');
			this.widget.addClass('widget-collapsed');
		}
	}

	setup_events() {
		this.link_list.forEach((link) => {
			// Bind Popover Event
			const link_label = link.find(".link-content");

			if (link.hasClass("disabled-link")) {
				const popover = link.find(".module-link-popover");

				link_label.mouseover(() => {
					if (this.in_customize_mode) return;
					popover.show();
				});
				link_label.mouseout(() => popover.hide());
			} else {
				link_label.click((event) => {
					if (this.in_customize_mode) return;

					if (link_label.hasClass("help-video-link")) {
						event.preventDefault();
						let yt_id = event.currentTarget.dataset.youtubeid;
						frappe.help.show_video(yt_id);
					}
				});
			}
		});
	}
}
