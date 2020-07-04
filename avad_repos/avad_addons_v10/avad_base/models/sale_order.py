# -*- coding: utf-8 -*-

import time
import math
from datetime import datetime
from django.utils.encoding import smart_str, smart_unicode

from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('our_project_id','our_sommeil_id')
    def get_medecins(self):
        for o in self:
            if o.our_project_id:
                o.partner_id = o.our_project_id.patient_id
                o.medecin_prescripteur_id = o.our_project_id.medecin_prescripteur_id
                o.medecin_traitant_id = o.our_project_id.medecin_traitant_id
            if o.our_sommeil_id:
                o.partner_id = o.our_sommeil_id.patient_id
                o.medecin_prescripteur_id = o.our_sommeil_id.medecin_prescripteur_id
                #o.medecin_traitant_id = o.our_sommeil_id.medecin_traitant_id

    our_project_id = fields.Many2one('project.project', string='Demande')
    our_sommeil_id = fields.Many2one('pat.sommeil', string='Sommeil')
    medecin_prescripteur_id = fields.Many2one('res.partner', 'Medecin Prescripteur',
                                              domain=[('type_client', '=', 'medecins')] , compute = get_medecins, store=True)
    medecin_traitant_id = fields.Many2one('res.partner', 'Medecin Traitant',
                                          domain=[('type_client', '=', 'medecins')], compute = get_medecins, store=True)

    @api.onchange('our_project_id', 'our_sommeil_id')
    def _get_partner_if_none(self):
        for o in self:
            if not o.partner_id:
                if o.our_project_id:
                    o.partner_id = o.our_project_id.patient_id
                    o.medecin_prescripteur_id = o.our_project_id.medecin_prescripteur_id
                    o.medecin_traitant_id = o.our_project_id.medecin_traitant_id
                    o.onchange_partner_id()
                if o.our_sommeil_id:
                    o.partner_id = o.our_sommeil_id.patient_id
                    o.medecin_prescripteur_id = o.our_sommeil_id.medecin_prescripteur_id
                    #o.medecin_traitant_id = o.our_sommeil_id.medecin_traitant_id
                    o.onchange_partner_id()

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for o in self:
            if o.our_project_id:
                forfaits = []
                for sol in o.order_line:
                    if sol.forfait_id:
                        forfaits.append(sol.forfait_id.name)
                forfaits = list(set(forfaits))
                msg_frfs = ''
                if len(forfaits):
                    for f in forfaits:
                        msg_frfs += " " + f + ";"
                    msg_frfs = "Forfaits: " + msg_frfs

                o.our_project_id.action_validate_avad()
                #o.our_project_id.send_sms_msg(add_msg=msg_frfs)

    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)
        # for o in res:
        #     if o.our_sommeil_id and o.our_sommeil_id.state == 'open':
        #         o.our_sommeil_id.demmarer()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    forfait_id = fields.Many2one("product.forfait", "Forfait")
    used_in_inv_rec = fields.Boolean("facturation récurrente", default=False)


    @api.onchange("product_id", "name", "product_uom_qty")
    def onchange_product_id_domain_forfait(self):
        for o in self:
            forfaits = []
            if o.product_id:
                forfaits = [f.id for f in o.product_id.forfait_ids]
            return {
                'domain': {
                    'forfait_id': [('id', 'in', forfaits)]
                }
            }

    # @api.constrains('used_in_inv_rec')
    # def check_recurent_contract(self, vals):
    #     for o in self:
    #         if o.used_in_inv_rec:
    #             #test d majout sur le contrat
    #             pass
    #         else:
    #             # test de suppression du contract
    #             pass
