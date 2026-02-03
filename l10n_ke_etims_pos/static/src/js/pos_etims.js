/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { useService } from "@web/core/utils/hooks";

/**
 * Kenya eTIMS Integration for Point of Sale
 *
 * This module extends the POS to:
 * 1. Display eTIMS submission status on orders
 * 2. Show eTIMS receipt information after payment
 * 3. Handle refunds with proper reason codes
 */

// Extend Order model to include eTIMS fields
patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.etims_submitted = false;
        this.etims_scu_no = null;
        this.etims_rcpt_no = null;
        this.etims_submission_error = null;
        this.etims_refund_reason = '01';  // Default reason
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.etims_submitted = json.etims_submitted || false;
        this.etims_scu_no = json.etims_scu_no || null;
        this.etims_rcpt_no = json.etims_rcpt_no || null;
        this.etims_submission_error = json.etims_submission_error || null;
        this.etims_refund_reason = json.etims_refund_reason || '01';
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.etims_submitted = this.etims_submitted;
        json.etims_scu_no = this.etims_scu_no;
        json.etims_rcpt_no = this.etims_rcpt_no;
        json.etims_submission_error = this.etims_submission_error;
        json.etims_refund_reason = this.etims_refund_reason;
        return json;
    },

    export_for_printing() {
        const receipt = super.export_for_printing(...arguments);
        receipt.etims_submitted = this.etims_submitted;
        receipt.etims_scu_no = this.etims_scu_no;
        receipt.etims_rcpt_no = this.etims_rcpt_no;
        return receipt;
    },

    is_return_order() {
        // Check if this is a return/refund order
        return this.get_total_with_tax() < 0;
    },

    set_etims_refund_reason(reason) {
        this.etims_refund_reason = reason;
    },

    get_etims_refund_reason() {
        return this.etims_refund_reason;
    },
});

// Extend PaymentScreen to show eTIMS status
patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
    },

    async _finalizeValidation() {
        const result = await super._finalizeValidation(...arguments);

        // Show eTIMS notification if available
        const order = this.currentOrder;
        if (order && order.etims_submitted) {
            this.notification.add(
                `eTIMS Receipt: ${order.etims_scu_no || 'Submitted'}`,
                { type: 'success', sticky: false }
            );
        } else if (order && order.etims_submission_error) {
            this.notification.add(
                `eTIMS Error: ${order.etims_submission_error}`,
                { type: 'warning', sticky: true }
            );
        }

        return result;
    },

    get isReturnOrder() {
        return this.currentOrder && this.currentOrder.is_return_order();
    },
});
