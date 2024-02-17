from odoo import fields, models, _
from datetime import date
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.move"

    packet_id = fields.Many2one("packet.management", string="Packet")


class PacketJournal(models.Model):
    _inherit = "packet.management"

    def action_done(self):
        res = super(PacketJournal, self).action_done()
        kit_journal_id = self.env["ir.config_parameter"].sudo().get_param("bi_kit_assembly.journal_id")
        if kit_journal_id:
            kit_journal_id = int(kit_journal_id)
        else:
            raise UserError(_("Enter the Journal."))
        journal_name = f"Packet Management {self.product_id.name}"
        amount = self.product_id.last_cost * sum(self.packet_line_ids.mapped("line_quantity"))
        finished_amount = amount
        packet_name = f"Packet Management {self.product_id.name}"
        journal_id = kit_journal_id
        debit_account_id = (
            self.product_id.account_inventory_id.id
            if self.product_id.account_inventory_id
            else self.product_id.product_tmpl_id.account_inventory_id.id
        )
        if not debit_account_id:
            raise UserError(_("Enter the Inventory Account against a Product."))
        new_lines = []

        new_lines.append(
            (
                0,
                0,
                {
                    "name": packet_name,
                    "account_id": debit_account_id,
                    "journal_id": journal_id,
                    "date": date.today(),
                    "credit": amount > 0.0 and amount or 0.0,
                    "debit": amount < 0.0 and -amount or 0.0,
                },
            )
        )

        total_amount = 0
        for each in self.packet_line_ids:
            amount = each.product_id.last_cost * each.line_quantity
            total_amount += amount
            packet_name = f"Packet Management {each.product_id.name}"
            journal_id = kit_journal_id
            credit_account_id = (
                each.product_id.account_inventory_id.id
                if each.product_id.account_inventory_id
                else each.product_id.product_tmpl_id.account_inventory_id.id
            )
            if not credit_account_id:
                raise UserError(_("Enter the Inventory Account against a Product."))
            new_lines.append(
                (
                    0,
                    0,
                    {
                        "name": packet_name,
                        "account_id": credit_account_id,
                        "journal_id": journal_id,
                        "date": date.today(),
                        "credit": amount < 0.0 and -amount or 0.0,
                        "debit": amount > 0.0 and amount or 0.0,
                    },
                )
            )
        balance_amount = finished_amount - total_amount
        adjustment_account = (
            each.product_id.account_standard_cost_revaluation_id.id
            if each.product_id.account_standard_cost_revaluation_id
            else each.product_id.product_tmpl_id.account_standard_cost_revaluation_id.id
        )
        if not adjustment_account:
            raise UserError(_("Enter the Adjustment Account against a Product for Creating a Journal Entry."))
        if balance_amount > 0:
            new_lines.append(
                (
                    0,
                    0,
                    {
                        "name": "Stock Adjustment",
                        "account_id": adjustment_account,
                        "journal_id": journal_id,
                        "date": date.today(),
                        "credit": balance_amount < 0.0 and -balance_amount or 0.0,
                        "debit": balance_amount > 0.0 and balance_amount or 0.0,
                    },
                )
            )
        if balance_amount < 0:
            new_lines.append(
                (
                    0,
                    0,
                    {
                        "name": "Stock Adjustment",
                        "account_id": adjustment_account,
                        "journal_id": journal_id,
                        "date": date.today(),
                        "credit": balance_amount * -1 > 0.0 and balance_amount * -1 or 0.0,
                        "debit": balance_amount * -1 < 0.0 and -balance_amount or 0.0,
                    },
                )
            )
        sequence = self.env["ir.sequence"].next_by_code("journal.sequence") or "/"
        vals = {
            "name": journal_name + sequence,
            "narration": journal_name,
            "ref": journal_name,
            "journal_id": kit_journal_id,
            "date": date.today(),
            "packet_id": self.id,
            "line_ids": new_lines,
        }
        move = self.env["account.move"].create(vals)
        move.with_context(warning=True).action_post()
        return res
