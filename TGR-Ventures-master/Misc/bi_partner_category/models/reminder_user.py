from odoo import fields, models


class ReminderUser(models.Model):
    _name = "reminder.user"

    name = fields.Char(string="Name")
    reminder_user_line_ids = fields.One2many("reminder.user.line", "reminder_id", string="Reminder Lines")


class ReminderUserLine(models.Model):
    _name = "reminder.user.line"

    reminder_id = fields.Many2one("reminder.user", string="Reminder ID")
    users_id = fields.Many2one("res.users", string="Users")
