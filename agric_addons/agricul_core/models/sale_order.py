# -*- coding: utf-8 -*-

import time
import math
from itertools import groupby

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.multi
    # def order_lines_layouted(self):
    #     """
    #     Returns this order lines classified by sale_layout_category and separated in
    #     pages according to the category pagebreaks. Used to render the report.
    #     """
    #     self.ensure_one()
    #     report_pages = [[]]
    #     for category, lines in groupby(self.order_line, lambda l: l.layout_category_id):
    #         lst_lines = list(lines)
    #         # If last added category induced a pagebreak, this one will be on a new page
    #         if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
    #             report_pages.append([])
    #         # Append category to current report page
    #         tot_ht = sum([line.price_subtotal for line in lst_lines])
    #         tot_taxes = sum([line.price_tax for line in lst_lines])
    #         tot_taxed = sum([line.price_total for line in lst_lines])
    #         report_pages[-1].append({
    #             'name': category and category.name or 'Uncategorized',
    #             'subtotal': category and category.subtotal,
    #             'pagebreak': category and category.pagebreak,
    #             'tot_taxed': tot_taxed,
    #             'tot_ht': tot_ht,
    #             'tot_taxes': tot_taxes,
    #             'lines': lst_lines,
    #         })
    #
    #     return report_pages