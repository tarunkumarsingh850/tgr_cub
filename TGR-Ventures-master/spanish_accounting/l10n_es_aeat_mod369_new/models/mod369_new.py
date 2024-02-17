from odoo import api, fields, models,_
import unicodedata
import base64


class L10nEsAeatMod369Report(models.Model):
    _name = "aeat.369.model.report"
    _description = "AEAT 369 Report"
    _rec_name = "date_start"
    

    company_vat = fields.Char('Vat Number')
    year = fields.Integer('Year')
    period_type = fields.Selection([
            ("1T", "1T - Primer trimestre"),
            ("2T", "2T - Segundo trimestre"),
            ("3T", "3T - Tercer trimestre"),
            ("4T", "4T - Cuarto trimestre"),
            ("01", "01 - Enero"),
            ("02", "02 - Febrero"),
            ("03", "03 - Marzo"),
            ("04", "04 - Abril"),
            ("05", "05 - Mayo"),
            ("06", "06 - Junio"),
            ("07", "07 - Julio"),
            ("08", "08 - Agosto"),
            ("09", "09 - Septiembre"),
            ("10", "10 - Octubre"),
            ("11", "11 - Noviembre"),
            ("12", "12 - Diciembre"),
        ],)
    date_start = fields.Date('Date From')
    date_end = fields.Date('Date End')
    export_config_id = fields.Many2one(
        comodel_name="aeat.model.export.config",
        string="Config parent",
        ondelete="cascade",
    )
    representative_vat = fields.Char(
        string="L.R. VAT number",
        size=9,
        help="Legal Representative VAT number.",
    )

    support_type = fields.Selection(
        selection=[("C", "DVD"), ("T", "Telematics")],
        default="T"
    )
    calculation_date = fields.Datetime()
    partner_id = fields.Many2one('res.partner', "Customer")

    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Bank account",
        help="Company bank account used for the presentation",
        domain="[('acc_type', '=', 'iban'), ('partner_id', '=', partner_id)]",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
    )

    contact_name = fields.Char(
        string="Full Name",
        size=40,
        help="Must have name and surname.",
    )
    contact_phone = fields.Char(
        string="Phone",
        size=10,
    )
    contact_email = fields.Char(
        size=50,
    )

    statement_type = fields.Selection(
        selection=[("N", "Normal"), ("C", "Complementary"), ("S", "Substitutive")],
        default="N",
    )
    declaration_type = fields.Selection(
        string="Declaration type",
        selection=[("union", "Union"), ("export", "Export"), ("import", "Import")],
        states={"draft": [("readonly", False)]},
    )
    nrc_reference = fields.Char(
        string="NRC Reference",
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    declaration_inactive = fields.Boolean(
        string="Declaration without activity",
        states={"draft": [("readonly", False)]},
    )
    payment_type = fields.Selection(
        selection=[
            (
                "O",
                "[O] Reconocimiento de deuda con los Estados "
                "Miembros de Consumo con imposibilidad de pago",
            ),
            (
                "S",
                "[S] Ingreso parcial y Reconocimiento de deuda "
                "con los Estados Miembros de Consumo con imposibilidad de pago",
            ),
            ("I", "[I] A ingresar"),
            ("N", "[N] Negativa"),
            ("T", "[T] Ingreso por transferencia desde el extranjero"),
        ],
        string="Payment type",
        default="I",
        states={"draft": [("readonly", False)]},
    )

    line_ids = fields.One2many(
        string="lines",
        comodel_name="aeat.369.model.report.line",
        inverse_name = "report_id"
    )
    state = fields.Selection([('draft','Draft'),('processed','Process')], default='draft')
    file = fields.Binary('txt File')
    file_name = fields.Char('File Name')


    def button_calculate(self):
        line_val = []
        vals = {}
        self.line_ids = False
        eu_country_codes = self.env.ref("base.europe").country_ids.mapped("code")
        eu_country_codes.remove("ES")

        account_tag_id = self.env["account.account.tag"].search([("name", "=", "OSS")])
        for country_code in eu_country_codes:

            tax = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", self.date_start),
                        ("move_id.invoice_date", "<=", self.date_end),
                        ("company_id", "=", self.company_id.id),
                        ("parent_state", "=", "posted"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        ("move_id.move_type", "=", "out_invoice"),
                        ('move_id.partner_id.country_id.code','=',country_code)
                    ],
                    limit=1,
                )
                .mapped("tax_ids")
            )

            move_ids = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", self.date_start),
                        ("move_id.invoice_date", "<=", self.date_end),
                        ("company_id", "=", self.company_id.id),
                        ("parent_state", "=", "posted"),
                        ("move_id.move_type", "=", "out_invoice"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        ('move_id.partner_id.country_id.code','=',country_code)
                    ]
                )
                .mapped("move_id")
            )
            untaxed_amount = 0
            amount_tax = 0
            amount_total = 0
            for record in move_ids:
                # if record.invoice_line_ids and record.invoice_line_ids.tax_ids and any(record.invoice_line_ids.tax_ids.mapped('custom_country_id')):
                if record.invoice_line_ids[0].tax_ids[0].mapped("custom_country_id").code in [country_code]:
                    untaxed_amount += record.amount_untaxed
                    amount_tax += record.amount_tax
                    amount_total += record.amount_total

            if amount_total != 0:
                # if
                country_id = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                vals = {
                    "country_code": country_code,
                    "country_id": country_id.id,
                    "vat_type": tax.id if tax else "",
                    "base_taxable":round(untaxed_amount, 2),
                    "tax_amount": round(amount_tax, 2),
                    "amount":round(amount_total, 2),
                    "report_id": self.id
                }
                line_val.append((0,0,vals))
  
        for country_code in eu_country_codes:
            tax = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", self.date_start),
                        ("move_id.invoice_date", "<=", self.date_end),
                        ("company_id", "=", self.company_id.id),
                        ("parent_state", "=", "posted"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        ("move_id.move_type", "=", "out_refund"),
                        ('move_id.partner_id.country_id.code','=',country_code)
                    ],
                    limit=1,
                )
                .mapped("tax_ids")
            )

            move_ids = (
                self.env["account.move.line"]
                .search(
                    [
                        ("move_id.invoice_date", ">=", self.date_start),
                        ("move_id.invoice_date", "<=", self.date_end),
                        ("company_id", "=", self.company_id.id),
                        ("parent_state", "=", "posted"),
                        ("move_id.move_type", "=", "out_refund"),
                        ("tax_tag_ids", "in", account_tag_id.ids),
                        ('move_id.partner_id.country_id.code','=',country_code)
                    ]
                )
                .mapped("move_id")
            )
            untaxed_amount = 0
            amount_tax = 0
            amount_total = 0
            for record in move_ids:
                if record.invoice_line_ids.tax_ids:
                    if record.invoice_line_ids[0].tax_ids[0].mapped("custom_country_id").code in [country_code]:
                        untaxed_amount += record.amount_untaxed
                        amount_tax += record.amount_tax
                        amount_total += record.amount_total

            if amount_total != 0:
                country_id = self.env["res.country"].search([("code", "=", country_code)], limit=1)
                vals = {
                    "country_code": country_code,
                    "country_id": country_id.id,
                    "vat_type": tax.id if tax else "",
                    "base_taxable":round(untaxed_amount, 2),
                    "tax_amount": round(amount_tax, 2),
                    "amount":round(amount_total, 2),
                    "report_id": self.id

                }
                line_val.append((0,0,vals))
        self.line_ids = line_val
        self.state = 'processed'
      

    def reset_to_draft(self):
        self.state = 'draft'
    
    def get_print_vals(self):
        rslt = b''
        val_line_905 = ''
        for line in self.line_ids:
            val_line_905 += """{country_code} {vat_amount}00S            {amount_total}            {tax_amount}""".format(country_code=line.country_code, amount_total= str(line.amount).replace('.','0'), tax_amount=str(line.tax_amount).replace('.','0'), vat_amount= int(line.vat_type.amount))
        val = """{lt}T3690{year}{period_type}0000{rt}
                    {vat_number}
                        {lt}T36900{rt}                                                                                             {lt}/T36900{rt}
                        {lt}T36904{rt}MOSS D{payment_type}                                      0 {vat_number2}      {company_name} UN {year}{period_type_letter} {period_type_number}                0{val_line_905}{lt}/T36904{rt}
                        <T36905> HR 2500S            44400            11100FI  500S            66600             3330   </T36905>
                        <T36906> LUA02134567      BG 1100S            22200             2442        </T36906>
                        <T36909>  </T36909>
                    {lt}/T3690{year}{period_type}0000>""".format(year=self.year,period_type=self.period_type, 
                                                                 vat_number = self.company_id.vat[2:],vat_number2 = self.company_id.vat,
                                                                 payment_type=self.payment_type,company_name=self.company_id.name,
                                                                 period_type_letter=self.period_type and self.period_type[1] or '',
                                                                 period_type_number= self.period_type and self.period_type[0] or '',
                                                                 rt='>',lt="<",val_line_905=val_line_905)
                
        return self.env['account.financial.html.report']._boe_format_string(val)


class L10nEsAeatMod369LineGroupednew(models.Model):
    _name = "aeat.369.model.report.line"
    _description = "Grouped info by country for 369 model"


    report_id = fields.Many2one(
        string="Mod369 report", comodel_name="aeat.369.model.report"
    )
    country_id = fields.Many2one(string="Country", comodel_name="res.country")
    country_code = fields.Char(string="Country code", related="country_id.code")
    tax_id = fields.Many2one(string="Tax", comodel_name="account.tax")
    vat_type = fields.Many2one('account.tax',string="VAT Rate")
    service_type = fields.Selection(
        related="tax_id.service_type",
        string="Service type",
    )
    amount = fields.Float(string="Amount total")
    base_taxable = fields.Float('Taxable Base')
    tax_amount = fields.Float('Tax Amount')
