# -*- coding: utf-8 -*-

import time
import math

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = "product.template"

    forfait_ids = fields.Many2many('product.forfait', 'forfait_product_rel', 'product_id', 'forfait_id',
                                        string='Forfaits')
    sommeil_ok = fields.Boolean("Sommeil", default=False)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        if context.get('sommeil_id', False):
            try:
                x = int(context.get('sommeil_id', 'Error'))
                args += ['|', ('sommeil_ok', '=', True), ('sommeil_ok', '=', True)]
            except:
                pass
        else:
            args += ['|', ('sommeil_ok', '=', False), ('sommeil_ok', '=', False)]
        return super(ProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                    access_rights_uid=access_rights_uid)


class SellerProduct(models.Model):
    _inherit = "product.supplierinfo"

    cost_logistic = fields.Float("Prix revient logistique")