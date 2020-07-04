# -*- coding: utf-8 -*-
# © 2017 Jérôme Guerriat
# © 2017 Niboo SPRL (https://www.niboo.be/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def print_pro_forma(self):
        """
        :return: Action to get pro forma invoice document
        """
        return self.env['report'].get_action(
            self, 'sale_proforma_order.report_proforma_document')
