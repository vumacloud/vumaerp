/** @odoo-module **/
/**
 * VumaERP White Label JavaScript
 * Handles dynamic text replacements throughout the application
 */

import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";

// Brand Configuration
const VUMAERP_BRAND = {
    name: "VumaERP",
    version: "17.0",
    tagline: "Enterprise Resource Planning",
    publisher: "VumaCloud",
    website: "https://vumacloud.com",
    support_url: "https://vumacloud.com/support",
    documentation_url: "https://vumacloud.com/docs",
};

// Text replacements mapping
const TEXT_REPLACEMENTS = [
    { from: /Odoo/g, to: VUMAERP_BRAND.name },
    { from: /odoo/g, to: "vumaerp" },
    { from: /www\.odoo\.com/g, to: VUMAERP_BRAND.website },
    { from: /odoo\.com/g, to: "vumacloud.com" },
    { from: /Powered by Odoo/gi, to: `Powered by ${VUMAERP_BRAND.publisher}` },
    { from: /Sent by Odoo/gi, to: `Sent by ${VUMAERP_BRAND.name}` },
];

/**
 * Replace Odoo references in text content
 */
function replaceOdooText(text) {
    if (!text || typeof text !== "string") return text;
    let result = text;
    for (const replacement of TEXT_REPLACEMENTS) {
        result = result.replace(replacement.from, replacement.to);
    }
    return result;
}

/**
 * Process DOM element and replace Odoo text
 */
function processElement(element) {
    if (!element) return;

    // Replace text content in text nodes
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );

    let node;
    while ((node = walker.nextNode())) {
        if (node.nodeValue && node.nodeValue.includes("Odoo")) {
            node.nodeValue = replaceOdooText(node.nodeValue);
        }
    }

    // Replace in title attributes
    element.querySelectorAll("[title]").forEach((el) => {
        if (el.title && el.title.includes("Odoo")) {
            el.title = replaceOdooText(el.title);
        }
    });

    // Replace in placeholder attributes
    element.querySelectorAll("[placeholder]").forEach((el) => {
        if (el.placeholder && el.placeholder.includes("Odoo")) {
            el.placeholder = replaceOdooText(el.placeholder);
        }
    });

    // Replace in alt attributes
    element.querySelectorAll("[alt]").forEach((el) => {
        if (el.alt && el.alt.includes("Odoo")) {
            el.alt = replaceOdooText(el.alt);
        }
    });
}

/**
 * Update document title
 */
function updateDocumentTitle() {
    if (document.title.includes("Odoo")) {
        document.title = replaceOdooText(document.title);
    }
    // Set default title if empty or generic
    if (!document.title || document.title === "Odoo") {
        document.title = VUMAERP_BRAND.name;
    }
}

/**
 * Initialize white labeling on page load
 */
function initWhiteLabel() {
    // Update document title
    updateDocumentTitle();

    // Process entire body
    processElement(document.body);

    // Observe DOM changes for dynamic content
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    processElement(node);
                }
            });
        });
        // Also update title for SPA navigation
        updateDocumentTitle();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWhiteLabel);
} else {
    initWhiteLabel();
}

// Re-run on window load to catch late-loading content
window.addEventListener("load", () => {
    setTimeout(() => {
        processElement(document.body);
        updateDocumentTitle();
    }, 500);
});

// Export for use in other modules
export { VUMAERP_BRAND, replaceOdooText, processElement };
