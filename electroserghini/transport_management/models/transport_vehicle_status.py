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


class VehicleStatus(models.Model):
    _name = 'transport.vehicle.status'

    name = fields.Char(string="Nom du véhicule")
    fuel_costs = fields.Float(string="Frais carburant",required=True)
    travelling_expenses = fields.Float(string="Frais de déplacement",required=True)
    amount_of_checks = fields.Float(string="Montant des chèques")
    amount_of_cash = fields.Float(string="Montant d'espèces")
    amount_of_effects = fields.Float(string="Montant des effets")
    transportation_name = fields.Many2one('transport.vehicle', string="Chauffeur",domain=[('active_available', '=', True)],required=True)
    transport_date = fields.Date(string="Date de départ",required=True)
    no_parcels = fields.Char(string="Nombre d'articles")
    sale_order = fields.Text(string='Réf. Bon de commande')
    delivery_order = fields.Text(string="Réf. Bon de livraison")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('start', 'Départ'),
        ('cancel', 'Annuler'),
        ('done', 'Arrivée'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    departure_city = fields.Selection([
    ('Meknes','Meknes')
    ], string='Ville de d  part',default='Meknes',index=True,required=True)

    destination_city_wm = fields.Selection([
('Agadir','Agadir'),
('Al Hoceima','Al Hoceima'),
('Asilah','Asilah'),
('Azemmour','Azemmour'),
('Azrou','Azrou'),
('Ben Slimane','Ben Slimane'),
('Beni Mellal','Beni Mellal'),
('Berkane','Berkane'),
('Berrechid','Berrechid'),
('Bouskoura','Bouskoura'),
('Bouznika','Bouznika'),
('Casablanca','Casablanca'),
('Dar Bouazza','Dar Bouazza'),
('Errachidia','Errachidia'),
('El Jadida','El Jadida'),
('Essaouira','Essaouira'),
('Fes','Fes'),
('Had Soualem','Had Soualem'),
('Ifrane','Ifrane'),
('Kenitra','Kenitra'),
('Khemisset','Khemisset'),
('khenifra','khenifra'),
('Khouribga','Khouribga'),
('Laayoune','Laayoune'),
('Larache','Larache'),
('Marrakech','Marrakech'),
('Meknes','Meknes'),
('Mohammedia','Mohammedia'),
('Nador','Nador'),
('Oualidia','Oualidia'),
('Ouarzazate','Ouarzazate'),
('Oujda','Oujda'),
('Rabat','Rabat'),
('Safi','Safi'),
('Sale','Sale'),
('Sefrou','Sefrou'),
('Settat','Settat'),
('Sidi Kacem','Sidi Kacem'),
('Sidi Rahal','Sidi Rahal'),
('Tamaris','Tamaris'),
('Tanger','Tanger'),
('aza','aza'),
('Tetouan','Tetouan'),
('Tiflet','Tiflet'),
('Tiznit','Tiznit')
], string='Ville de destination',  index=True,required=True)


    def start_action(self):
        vehicle = self.env['transport.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': False}
        vehicle.write(vals)
        self.write({'state': 'start'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
        vehicle = self.env['transport.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': True}
        vehicle.write(vals)

    def action_done(self):
        self.write({'state': 'done'})
        vehicle = self.env['transport.vehicle'].search([('name', '=', self.name)])
        vals = {'active_available': True}
        vehicle.write(vals)

    def action_reshedule(self):
        self.write({'state': 'draft'})
