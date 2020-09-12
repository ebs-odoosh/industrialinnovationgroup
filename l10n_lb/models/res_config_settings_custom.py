from odoo import fields, models, api, _


class ResConfigSettingCustom(models.TransientModel):
    _inherit = "res.config.settings"

    vat_amount_default = fields.Float(
        string='Default VAT Amount',
        related='company_id.vat_amount_default',
        readonly=False
    )
