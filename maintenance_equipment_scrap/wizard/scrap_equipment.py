# Copyright 2017-2020 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class WizardPerformEquipmentScrap(models.TransientModel):
    _name = "wizard.perform.equipment.scrap"
    _description = "Perform Scrap (Equipment)"

    scrap_date = fields.Date(required=True, default=fields.Date.context_today)
    equipment_id = fields.Many2one("maintenance.equipment", required=True)
    template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Email Template",
        compute="_compute_template_id",
        readonly=False,
        store=True,
        help="Email template to send to followers when the equipment is scrapped.",
    )

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Set default template_id based on equipment category, note that equipment_id
        # is required and set from the "action_perform_scrap" button context
        if "equipment_id" in res and not res.get("template_id"):
            equipment_id = self.env["maintenance.equipment"].browse(res["equipment_id"])
            res["template_id"] = equipment_id.category_id.equipment_scrap_template_id.id
        return res

    @api.depends("equipment_id.category_id.equipment_scrap_template_id")
    def _compute_template_id(self):
        for wizard in self:
            wizard.template_id = (
                wizard.template_id
                or wizard.equipment_id.category_id.equipment_scrap_template_id
            )

    def do_scrap(self):
        for wizard in self:
            wizard.equipment_id.scrap_date = wizard.scrap_date
            if wizard.template_id:
                wizard.template_id.send_mail(wizard.equipment_id.id)
