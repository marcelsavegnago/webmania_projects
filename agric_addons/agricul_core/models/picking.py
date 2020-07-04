# -*- coding: utf-8 -*-

import time
import math
from itertools import groupby

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.depends('group_id')
    def compute_date_commande(self):
        for o in self:
            o.order_date_origin = False
            if o.group_id:
                orders = self.env['sale.order'].search([('name', '=', o.group_id.name)])
                if orders and len(orders):
                    o.order_date_origin = orders[0].confirmation_date or orders[0].date_order
                else:
                    orders = self.env['purchase.order'].search([('name', '=', o.group_id.name)])
                    if orders and len(orders):
                        o.order_date_origin = orders[0].date_order

    order_date_origin = fields.Datetime("Date commande", compute=compute_date_commande)
