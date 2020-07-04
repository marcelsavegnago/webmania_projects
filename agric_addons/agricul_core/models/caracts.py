# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class PermeabiliteSol(models.Model):
    _name = 'amh.caracts.perm'
    _description = "permeabilite du sol"

    name = fields.Char("")

