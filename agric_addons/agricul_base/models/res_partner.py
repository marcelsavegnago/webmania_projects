# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class ResPartnerAMh(models.Model):
    _inherit = "res.partner"

    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company'), ('association', 'Association')],
        compute=False, inverse=False, default='person')
    is_association = fields.Boolean("Is Association")
    n_cin = fields.Char(string="CIN")
    genre_x = fields.Selection([('Mr.','Mr. '),('Mme.','Mme. ')], 'Genre', default='Mr.')
    #use_only_supplied_product = fields.Boolean("a suuprimer")

    # @api.depends('is_company', 'is_association')
    # def _compute_company_type(self):
    #     for partner in self:
    #         if partner.is_association and partner.is_company:
    #             partner.company_type = 'association'
    #         elif partner.is_company:
    #             partner.company_type = 'company'
    #         else:
    #             partner.company_type = 'person'


    def _write_company_type(self):
        for partner in self:
            partner.is_company = (partner.company_type in ['company', 'association'])
            partner.is_association = (partner.company_type == 'association')

    @api.onchange('company_type')
    def onchange_company_type(self):
        self.is_association = (self.company_type == 'association')
        self.is_company = (self.company_type in ['company', 'association'])
