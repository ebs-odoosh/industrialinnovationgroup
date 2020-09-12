from odoo import fields, models, api


class EventType(models.Model):
    _name = 'sap.event.type'

    name = fields.Char(string="Code", required=True)
    description = fields.Char(
        string='Description',
        required=False)
    event_type_reason_ids = fields.One2many(
        comodel_name='sap.event.type.reason',
        inverse_name='event_type_id',
        string='Reasons',
        required=False)


class EventTypeReason(models.Model):
    _name = 'sap.event.type.reason'

    name = fields.Char(string="Code", required=True)
    description = fields.Char(
        string='Description',
        required=False)
    event_type_id = fields.Many2one(
        comodel_name='sap.event.type',
        string='Event Type',
        required=True, ondelete='cascade')
