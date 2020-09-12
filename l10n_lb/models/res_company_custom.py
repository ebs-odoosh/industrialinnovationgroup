from odoo import fields, models, api, _


class ResConfigSettingCustom(models.Model):
    _inherit = "res.company"

    vat_amount_default = fields.Float(
        string='Default VAT Amount',
        required=False,
        default=0.0
    )
