/** @odoo-module **/

// Replace page title
document.title = document.title.replace(/Odoo/gi, 'VumaERP');

// Observer to keep title updated
const titleObserver = new MutationObserver(() => {
    if (document.title.includes('Odoo')) {
        document.title = document.title.replace(/Odoo/gi, 'VumaERP');
    }
});

titleObserver.observe(document.querySelector('title'), { childList: true });

// Replace Odoo text in page on load
document.addEventListener('DOMContentLoaded', () => {
    // Update any "Powered by Odoo" footers
    document.querySelectorAll('a[href*="odoo.com"]').forEach(el => {
        if (el.textContent.toLowerCase().includes('odoo')) {
            el.textContent = el.textContent.replace(/Odoo/gi, 'VumaERP');
            el.href = 'https://vumacloud.com';
        }
    });
});
