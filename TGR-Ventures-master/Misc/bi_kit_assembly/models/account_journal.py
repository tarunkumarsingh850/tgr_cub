from odoo import fields, models, _
from datetime import date
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = "account.move"

    assembly_id = fields.Many2one("kit.assembly", string="Assembly")


class AssemblyJournal(models.Model):
    _inherit = "kit.assembly"

    def action_done_assembly(self):
        res = super(AssemblyJournal, self).action_done_assembly()
        kit_journal_id = self.env["ir.config_parameter"].sudo().get_param("bi_kit_assembly.journal_id")
        account_assembly_id = self.env["ir.config_parameter"].sudo().get_param("bi_kit_assembly.account_assembly_id")
        # if kit_journal_id:
        #     kit_journal_id = int(kit_journal_id)
        # else:
        #     raise UserError(_("Enter the Journal."))
        # if not account_assembly_id:
        #     raise UserError(_("Please configure the Account ID in Inventory Settings"))
        # else:
        #     account_assembly_id = int(account_assembly_id)
        for assembly in self:
            if assembly.is_disassembly:
                amount = round(assembly.product_id.last_cost, 2)
                finished_amount = amount
                assembly_name = f"Kit Disassembly {assembly.product_id.name}"
                journal_id = kit_journal_id
                # credit_account_id = (
                #     assembly.product_id.account_inventory_id.id
                #     if assembly.product_id.account_inventory_id
                #     else assembly.product_id.product_tmpl_id.account_inventory_id.id
                # )
                # if not credit_account_id:
                # raise UserError(_("Enter the Inventory Account against a Product."))
                credit_account_id = account_assembly_id
                new_lines = []
                new_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": assembly_name,
                            "account_id": credit_account_id,
                            "journal_id": journal_id,
                            "date": date.today(),
                            "debit": round(amount, 2) > 0.0 and amount or 0.0,
                            "credit": round(amount, 2) < 0.0 and -amount or 0.0,
                        },
                    )
                )
                total_amount = 0
                for each in assembly.kit_line_ids:
                    journal_name = f"Kit Disassembly {assembly.product_id.name}"
                    amount = round(each.product_id.last_cost, 2)
                    total_amount += amount
                    assembly_name = f"Kit Disassembly Consumed {each.product_id.name}"
                    journal_id = kit_journal_id
                    # debit_account_id = (
                    #     each.product_id.account_inventory_id.id
                    #     if each.product_id.account_inventory_id
                    #     else each.product_id.product_tmpl_id.account_inventory_id.id
                    # )
                    # if not debit_account_id:
                    #     raise UserError(_("Enter the Inventory Account against a Product."))
                    debit_account_id = account_assembly_id

                    new_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": assembly_name,
                                "account_id": debit_account_id,
                                "journal_id": journal_id,
                                "date": date.today(),
                                "debit": round(amount, 2) < 0.0 and -amount or 0.0,
                                "credit": round(amount, 2) > 0.0 and amount or 0.0,
                            },
                        )
                    )
                balance_amount = round(finished_amount - total_amount, 2)
                # adjustment_account = (
                #     each.product_id.account_inventory_id.id
                #     if each.product_id.account_inventory_id
                #     else each.product_id.product_tmpl_id.account_inventory_id.id
                # )
                adjustment_account = account_assembly_id
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
                                "debit": round(balance_amount, 2) < 0.0 and -balance_amount or 0.0,
                                "credit": round(balance_amount, 2) > 0.0 and balance_amount or 0.0,
                            },
                        )
                    )
                else:
                    new_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": "Stock Adjustment",
                                "account_id": adjustment_account,
                                "journal_id": journal_id,
                                "date": date.today(),
                                "credit": round(balance_amount, 2) * -1 < 0.0 and -balance_amount or 0.0,
                                "debit": round(balance_amount, 2) * -1 > 0.0 and balance_amount * -1 or 0.0,
                            },
                        )
                    )

                sequence = self.env["ir.sequence"].next_by_code("journal.sequence") or "/"
                vals = {
                    "name": journal_name + " " + sequence,
                    "narration": journal_name,
                    "ref": journal_name,
                    "journal_id": kit_journal_id,
                    "date": date.today(),
                    "assembly_id": assembly.id,
                    "line_ids": new_lines,
                }
            else:
                journal_name = f"Kit Assembly {assembly.product_id.name}"
                amount = round(assembly.product_id.last_cost, 2)
                finished_amount = amount
                assembly_name = f"Kit Assembly Finished {assembly.product_id.name}"
                journal_id = kit_journal_id
                # debit_account_id = (
                #     assembly.product_id.account_inventory_id.id
                #     if assembly.product_id.account_inventory_id
                #     else assembly.product_id.product_tmpl_id.account_inventory_id.id
                # )
                # if not debit_account_id:
                #     raise UserError(_("Enter the Inventory Account against a Product."))
                debit_account_id = account_assembly_id
                new_lines = []

                new_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": assembly_name,
                            "account_id": debit_account_id,
                            "journal_id": journal_id,
                            "date": date.today(),
                            "debit": amount > 0.0 and amount or 0.0,
                            "credit": amount < 0.0 and -amount or 0.0,
                        },
                    )
                )

                total_amount = 0
                for each in assembly.kit_line_ids:
                    amount = round(each.product_id.last_cost, 2)
                    total_amount += amount
                    assembly_name = f"Kit Assembly Consumed {each.product_id.name}"
                    journal_id = kit_journal_id
                    # credit_account_id = (
                    #     each.product_id.account_inventory_id.id
                    #     if each.product_id.account_inventory_id
                    #     else each.product_id.product_tmpl_id.account_inventory_id.id
                    # )
                    # if not credit_account_id:
                    #     raise UserError(_("Enter the Inventory Account against a Product."))
                    credit_account_id = account_assembly_id
                    new_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": assembly_name,
                                "account_id": credit_account_id,
                                "journal_id": journal_id,
                                "date": date.today(),
                                "debit": amount < 0.0 and -amount or 0.0,
                                "credit": amount > 0.0 and amount or 0.0,
                            },
                        )
                    )
                balance_amount = round(finished_amount - total_amount, 2)
                # adjustment_account = (
                #     each.product_id.account_inventory_id.id
                #     if each.product_id.account_inventory_id
                #     else each.product_id.product_tmpl_id.account_inventory_id.id
                # )
                adjustment_account = account_assembly_id
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
                                "debit": balance_amount < 0.0 and -balance_amount or 0.0,
                                "credit": balance_amount > 0.0 and balance_amount or 0.0,
                            },
                        )
                    )
                else:
                    new_lines.append(
                        (
                            0,
                            0,
                            {
                                "name": "Stock Adjustment",
                                "account_id": adjustment_account,
                                "journal_id": journal_id,
                                "date": date.today(),
                                "credit": balance_amount * -1 < 0.0 and -balance_amount or 0.0,
                                "debit": balance_amount * -1 > 0.0 and balance_amount * -1 or 0.0,
                            },
                        )
                    )
                sequence = self.env["ir.sequence"].next_by_code("journal.sequence") or "/"
                vals = {
                    "name": journal_name + " " + sequence,
                    "narration": journal_name,
                    "ref": journal_name,
                    "journal_id": kit_journal_id,
                    "date": date.today(),
                    "assembly_id": assembly.id,
                    "line_ids": new_lines,
                }
            # move = self.env["account.move"].create(vals)
            # move.with_context(warning=True).action_post()
        return res
