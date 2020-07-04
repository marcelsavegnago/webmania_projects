# -*- coding: utf-8 -*-

import time
import math
from datetime import datetime
from django.utils.encoding import smart_str, smart_unicode

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if vals.get('state', 'False') == 'purchase':
            for o in self:
                for l in o.order_line:
                    if l.product_id and o.partner_id:
                        for sl in l.product_id.seller_ids:
                            if sl.name and sl.name.id == o.partner_id.id:
                                sl.cost_logistic = (l.prix_revient or 0)
        return res

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    prix_revient = fields.Float("Cout logistique")

    @api.onchange('price_unit','product_id')
    def on_change_price_rev(self):
        for o in self:
            prix_revient = (o.price_unit or 0)
            from_currency = o.currency_id
            to_currency = o.company_id.currency_id
            if from_currency and to_currency:
                date_ordp = datetime.now()
                if o.order_id.date_order:
                    date_ordp = fields.Datetime.from_string(o.order_id.date_order)

                rate_from = from_currency.rate_ids.filtered(
                    lambda r: fields.Datetime.from_string(r.name).date() == date_ordp.date())
                rate_to = to_currency.rate_ids.filtered(
                    lambda r: fields.Datetime.from_string(r.name).date() == date_ordp.date())
                rate_from = rate_from[0].rate if rate_from else from_currency.rate
                rate_to = rate_to[0].rate if rate_to else to_currency.rate
                prix_revient = (float(prix_revient or 0) / float(rate_from or 1)) * float(rate_to or 1)
                prix_revient = to_currency.round(prix_revient)
            if o.order_id.partner_id:
                prix_revient = (prix_revient or 0) + (o.order_id.partner_id.cost_logistique or 0)
            o.prix_revient = prix_revient
