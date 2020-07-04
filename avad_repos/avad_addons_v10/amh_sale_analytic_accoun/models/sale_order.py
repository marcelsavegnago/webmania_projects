# -*- coding: utf-8 -*-
#  Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#  Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Compte analytique'
    )

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.account_analytic_id:
            res.update({
                'account_analytic_id': self.account_analytic_id.id,
            })
        return res
