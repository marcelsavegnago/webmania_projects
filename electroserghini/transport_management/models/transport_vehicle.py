# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class VehicleCreation(models.Model):
    _name = 'transport.vehicle'
    _rec_name = 'name' 

    name = fields.Char(string="Nom du véhicule", required=True)
    driver_name = fields.Many2one('res.partner', string="Nom du contact", required=True)
    vehicle_image = fields.Binary(string='Image', store=True, attachment=True)
    licence_plate = fields.Char(string="Plaque d'immatriculation", required=True)
    mob_no = fields.Char(string="Numéro de portable", required=True)
    vehicle_address = fields.Char(string="Address")
    active_available = fields.Boolean(string="Active", default=True)


