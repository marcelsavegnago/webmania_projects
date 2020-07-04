# -*- coding: utf-8 -*-

import time
import math
from itertools import groupby

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def order_lines_layouted(self):
        """
        Returns this sale order lines ordered by sale_layout_category sequence. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.invoice_line_ids, lambda l: l.layout_category_id):
            lst_lines = list(lines)
            # If last added category induced a pagebreak, this one will be on a new page
            if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
                report_pages.append([])
            # Append category to current report page
            tot_taxes = 0
            tot_ht = 0
            for line in lst_lines:
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                tot_ht += price_unit * line.quantity
                taxes = \
                line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id,
                                                      self.partner_id)['taxes']
                for tax in taxes:
                    val = self._prepare_tax_line_vals(line, tax)
                    tot_taxes += val['amount']
            tot_taxed = tot_taxes + tot_ht
            report_pages[-1].append({
                'name': category and category.name or 'Uncategorized',
                'subtotal': category and category.subtotal,
                'pagebreak': category and category.pagebreak,
                'tot_taxed': tot_taxed,
                'tot_ht': tot_ht,
                'tot_taxes': tot_taxes,
                'lines': lst_lines,
            })

        return report_pages
