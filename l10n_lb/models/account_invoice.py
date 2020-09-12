from odoo import fields, models, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def tax_line_move_line_get(self):
        res = []
        # keep track of taxes already processed
        done_taxes = []
        # loop the invoice.tax.line in reversal sequence
        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            if tax_line.amount_total:
                tax = tax_line.tax_id
                if tax.amount_type == "group":
                    for child_tax in tax.children_tax_ids:
                        done_taxes.append(child_tax.id)
                if tax.is_withholding_tax:
                    res.append({
                        'invoice_tax_line_id': tax_line.id,
                        'tax_line_id': tax_line.tax_id.id,
                        'type': 'tax',
                        'name': tax_line.name,
                        'price_unit': -tax_line.amount_total,
                        'quantity': 1,
                        'price': -tax_line.amount_total,
                        'account_id': tax_line.account_id.id,
                        'account_analytic_id': tax_line.account_analytic_id.id,
                        'invoice_id': self.id,
                        'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                    })
                    move_line_dict = {
                        'type': 'src',
                        'name': 'Withholding tax expense',
                        'price_unit': tax_line.amount_total,
                        'quantity': 1,
                        'price': tax_line.amount_total,
                        'account_id': tax.withholding_expense_account_id.id,
                        'account_analytic_id': tax_line.account_analytic_id.id,
                        'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else [],
                        'invoice_id': self.id,
                    }
                    res.append(move_line_dict)
                else:
                    res.append({
                        'invoice_tax_line_id': tax_line.id,
                        'tax_line_id': tax_line.tax_id.id,
                        'type': 'tax',
                        'name': tax_line.name,
                        'price_unit': tax_line.amount_total,
                        'quantity': 1,
                        'price': tax_line.amount_total,
                        'account_id': tax_line.account_id.id,
                        'account_analytic_id': tax_line.account_analytic_id.id,
                        'invoice_id': self.id,
                        'tax_ids': [(6, 0, list(done_taxes))] if tax_line.tax_id.include_base_amount else []
                    })
                done_taxes.append(tax.id)
        return res

