/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";

// Override document title
patch(WebClient.prototype, {
    setup() {
        super.setup(...arguments);
        this._updateTitle();
    },

    _updateTitle() {
        const baseTitle = "VumaERP";
        if (document.title && !document.title.includes("VumaERP")) {
            // Replace "Odoo" with "VumaERP" in title
            document.title = document.title.replace(/Odoo/gi, "VumaERP");
        }
        if (!document.title) {
            document.title = baseTitle;
        }
    },
});

// Override any remaining Odoo text on page load
document.addEventListener("DOMContentLoaded", function () {
    // Update any remaining Odoo text
    const replaceOdooText = () => {
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        while ((node = walker.nextNode())) {
            if (node.nodeValue && node.nodeValue.includes("Odoo")) {
                // Don't replace in scripts or technical content
                const parent = node.parentElement;
                if (parent && !["SCRIPT", "STYLE", "CODE", "PRE"].includes(parent.tagName)) {
                    node.nodeValue = node.nodeValue.replace(/Odoo/g, "VumaERP");
                }
            }
        }
    };

    // Run after a short delay to catch dynamically loaded content
    setTimeout(replaceOdooText, 1000);
});
