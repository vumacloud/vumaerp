/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    /**
     * Get E-VAT data for receipt
     */
    get_evat_data() {
        return {
            evat_submitted: this.evat_submitted || false,
            evat_sdc_id: this.evat_sdc_id || '',
            evat_sdc_time: this.evat_sdc_time || '',
            evat_receipt_number: this.evat_receipt_number || '',
            evat_qrcode: this.evat_qrcode || '',
        };
    },

    /**
     * Set E-VAT data from server response
     */
    set_evat_data(data) {
        if (data) {
            this.evat_submitted = data.evat_submitted || false;
            this.evat_sdc_id = data.evat_sdc_id || '';
            this.evat_sdc_time = data.evat_sdc_time || '';
            this.evat_receipt_number = data.evat_receipt_number || '';
            this.evat_qrcode = data.evat_qrcode || '';
        }
    },

    /**
     * Export for JSON - include E-VAT fields
     */
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.evat_data = this.get_evat_data();
        return result;
    },

    /**
     * Initialize from JSON - include E-VAT fields
     */
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (json.evat_data) {
            this.set_evat_data(json.evat_data);
        }
    },
});
