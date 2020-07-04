# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, _, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    vat = fields.Char('Identifiant fiscal', help="Tax Identification Number. Used by the some of the legal statements.")
    ice = fields.Char('Ice', size=32, required=False)

    _sql_constraints = [('partner_ice_unique', 'unique(ice)', "Ce code ICE est deja utilise"),
                        ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
