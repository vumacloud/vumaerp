# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class EtimsCustomerInfoWizard(models.TransientModel):
    _name = 'etims.customer.info.wizard'
    _description = 'eTIMS Customer Information'

    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    customer_name = fields.Char(string='Customer Name', readonly=True)
    customer_tin = fields.Char(string='Customer TIN', readonly=True)
    customer_status = fields.Char(string='Status', readonly=True)

    def action_update_partner(self):
        """Update partner with KRA info."""
        self.ensure_one()
        if self.partner_id and self.customer_name:
            self.partner_id.write({
                'name': self.customer_name,
                'etims_pin': self.customer_tin,
                'etims_pin_validated': True,
                'etims_pin_validation_date': fields.Datetime.now(),
            })
        return {'type': 'ir.actions.act_window_close'}
