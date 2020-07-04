# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class WizardCancelSommeil(models.TransientModel):

    _name = "wizard.cancel.sommeil"

    def _default_sommeil(self):
        res = False
        sommeil = self._context.get('active_ids', [])
        if sommeil:
            sm = self.env['pat.sommeil'].browse(sommeil)
            res = sm[0].id if sm else False
        return res

    sommeil_id = fields.Many2one("pat.sommeil", "Sommeil", default=_default_sommeil)
    motif = fields.Char("Motif d'annulation")

    def action_do(self):
        for o in self:
            if o.sommeil_id:
                o.sommeil_id.write({'motif': o.motif, 'state': 'annule'})