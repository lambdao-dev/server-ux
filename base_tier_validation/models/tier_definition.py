# Copyright 2017 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class TierDefinition(models.Model):
    _name = "tier.definition"
    _description = "Tier Definition"

    @api.model
    def _get_default_name(self):
        return _("New Tier Validation")

    @api.model
    def _get_tier_validation_model_names(self):
        res = []
        return res

    name = fields.Char(
        string="Description",
        required=True,
        default=lambda self: self._get_default_name(),
        translate=True,
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Referenced Model",
        domain=lambda self: [("model", "in", self._get_tier_validation_model_names())],
    )
    model = fields.Char(related="model_id.model", index=True, store=True)
    review_type = fields.Selection(
        string="Validated by",
        default="individual",
        selection=[
            ("individual", "Specific user"),
            ("group", "Any user in a specific group"),
            ("field", "Field in related record"),
        ],
    )
    allow_write_for_reviewer = fields.Boolean(
        string="Allow Write For Reviewers",
        default=False,
    )
    reviewer_id = fields.Many2one(comodel_name="res.users", string="Reviewer")
    reviewer_group_id = fields.Many2one(
        comodel_name="res.groups", string="Reviewer group"
    )
    reviewer_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Reviewer field",
        domain="[('id', 'in', valid_reviewer_field_ids)]",
    )
    valid_reviewer_field_ids = fields.One2many(
        comodel_name="ir.model.fields",
        compute="_compute_domain_reviewer_field",
    )
    definition_type = fields.Selection(
        string="Definition", selection=[("domain", "Domain")], default="domain"
    )
    definition_domain = fields.Char()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=30)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notify_on_create = fields.Boolean(
        string="Notify Reviewers on Creation",
        help="If set, all possible reviewers will be notified by email when "
        "this definition is triggered.",
    )
    notify_on_pending = fields.Boolean(
        string="Notify Reviewers on reaching Pending",
        help="If set, all possible reviewers will be notified by email when "
        "this status is reached."
        "Usefull in an Approve by sequence scenario. "
        "An notification request to review is sent out when it's their turn to review.",
    )
    notify_on_accepted = fields.Boolean(
        string="Notify Reviewers on Accepted",
        help="If set, reviewers will be notified by email when a review related "
        "to this definition is accepted.",
    )
    notify_on_rejected = fields.Boolean(
        string="Notify Reviewers on Rejected",
        help="If set, reviewers will be notified by email when a review related "
        "to this definition is rejected.",
    )
    notify_on_restarted = fields.Boolean(
        string="Notify Reviewers on Restarted",
        help="If set, reviewers will be notified by email when a reviews related "
        "to this definition are restarted.",
    )
    has_comment = fields.Boolean(string="Comment", default=False)
    approve_sequence = fields.Boolean(
        string="Approve by sequence",
        default=False,
        help="Approval order by the specified sequence number",
    )
    approve_sequence_bypass = fields.Boolean(
        help="Bypassed (auto validated), if previous tier was validated "
        "by same reviewer",
    )

    @api.onchange("review_type")
    def onchange_review_type(self):
        self.reviewer_id = None
        self.reviewer_group_id = None

    @api.depends("review_type", "model_id")
    def _compute_domain_reviewer_field(self):
        for rec in self:
            rec.valid_reviewer_field_ids = (
                self.env["ir.model.fields"]
                .sudo()
                .search([("model", "=", rec.model), ("relation", "=", "res.users")])
            )
