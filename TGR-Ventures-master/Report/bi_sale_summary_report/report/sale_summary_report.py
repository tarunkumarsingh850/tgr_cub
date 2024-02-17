from odoo import api, models



class SaleSummaryReport(models.AbstractModel):
    _name = "report.bi_sale_summary_report.report_sale_summary"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet("Sale Summary Report")
        justify = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 12})
        justify.set_align("justify")
        bolda = workbook.add_format({"bold": True, "align": "left","border":1})
        boldc = workbook.add_format({"bold": True, "align": "center", "border":1})
        center = workbook.add_format({"align": "center", "border": 1 })
        date = data["form"]["date"]
        to_date = data["form"]["to_date"]
        worksheet.merge_range("A1:D1", f"Sales Summary Report - From {date} to {to_date}", bolda)

       

        worksheet.set_column("A:A", 50)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 15)
        worksheet.set_column("H:H", 15)
        worksheet.set_column("I:I", 15)
        worksheet.set_column("J:J", 15)
        worksheet.set_column("K:K", 15)
        worksheet.set_column("L:L", 15)
        worksheet.set_column("M:M", 15)

        worksheet.write('A2','', center)
        worksheet.write('B2', 'Tiger One UK', boldc)
        worksheet.write('C2', 'Tiger One EU', boldc)
        worksheet.write('D2', 'Seedsman UK', boldc)
        worksheet.write('E2', 'Seedsman EU', boldc)
        worksheet.write('F2', 'Seedsman USA', boldc)
        worksheet.write('G2', 'Tiger One USA', boldc)
        worksheet.write('H2', 'THTC', boldc)
        worksheet.write('I2', 'Fastbuds', boldc)
        worksheet.write('J2', 'Barneys Farm', boldc)
        worksheet.write('K2', 'Others', boldc)

        domain = [('sale_id','!=', False),('state','=','posted')]
        if date:
            domain.append(("date", ">=", date))
        if to_date:
            domain.append(('date','<=', to_date))
        records = self.env["account.payment"].search(domain)
        sale_ids = records.mapped('sale_id.id')
        sale_orders = self.env['sale.order'].search([('id','in', sale_ids),('state','=','sale')])

        payment_filter = self.env['sale.order'].read_group(
            [('id','in', sale_ids),('state','=','sale')],
            fields=['magento_payment_method_id'],
            groupby=['magento_payment_method_id'],
            lazy=False
        )
        
        website_dict = {
            'Tiger One UK'  : "B",
            'Tiger One EU'  : "C",
            'Seedsman UK'   : "D",
            'Seedsman EU'   : "E",
            'Seedsman USA'  : "F",
            'Tiger One USA' : "G",
            'THTC'          : "H",
            'Fastbuds'      : "I",
            'Barneys Farm'  : "J",
            'Others'        : "K",
        }

        total_dict = {
            'Tiger One UK'  : 0,
            'Tiger One EU'  : 0,
            'Seedsman UK'   : 0,
            'Seedsman EU'   : 0,
            'Seedsman USA'  : 0,
            'Tiger One USA' : 0,
            'THTC'          : 0,
            'Fastbuds'      : 0,
            'Barneys Farm'  : 0,
            'Others'        : 0,
        }

        az = {i: chr(ord('A') + i - 1) for i in range(1, 27)}
        report_lines = []
        filtered_records = sale_orders
        row = 3
        for payment in payment_filter:
            if isinstance(payment.get('magento_payment_method_id'),tuple):
                payment_methods_id = payment.get('magento_payment_method_id')[0]
                magento_payment_method_id = self.env['magento.payment.method'].browse(payment_methods_id)
                recs = filtered_records.filtered(lambda x: x.magento_payment_method_id.id == payment_methods_id)
                recs_ids = recs.mapped('id')
                website_ids = self.env['sale.order'].read_group(
                    [('id','in', recs_ids)],
                    fields=['magento_website_id'],
                        groupby=['magento_website_id'],
                        lazy=False
                )
                web_records = {}
                for website in website_ids:
                    if isinstance(website.get('magento_website_id'),tuple):
                        website_id = website.get('magento_website_id')[0]
                        magento_website_id = self.env['magento.website'].browse(website_id)
                        w_recs = recs.filtered(lambda x : x.magento_website_id.id == website_id)
                        w_recs_ids = w_recs.mapped('id')
                        payment_ids = records.filtered(lambda x: x.sale_id.id in w_recs_ids)
                        total = round(sum(payment_ids.mapped('amount_signed')),2)
                        symbol = payment_ids[0].currency_id.symbol if payment_ids else ''
                        # total_amount = sum(w_recs.mapped('amount_total'))
                        total_dict[str(magento_website_id.name)] = total_dict.get(str(magento_website_id.name)) + total
                        web_records[str(magento_website_id.name)] = symbol + '' + str(total)


                report_lines.append({str(magento_payment_method_id.display_name):web_records})
                filtered_records = filtered_records.filtered(lambda x: x.id not in recs_ids)
            else:
                if payment.get('__count') == len(filtered_records):
                    # total_amount = sum(filtered_records.mapped('amount_total'))
                    shopfiy_records = filtered_records.filtered(lambda x: x.shopify_instance_id.id == True)
                    if shopfiy_records:
                        shopfiy_records_ids = shopfiy_records.mapped('id')
                        web_records = {}
                        payment_ids = records.filtered(lambda x: x.sale_id.id in shopfiy_records_ids)
                        symbol = payment_ids[0].currency_id.symbol if payment_ids else ''
                        total = round(sum(payment_ids.mapped('amount_signed')),2)
                        web_records["THTC"] = symbol + str(total)
                        total_dict['THTC'] = total_dict.get('THTC') + total
                        report_lines.append({ "Shopify Payments" : web_records})
                        filtered_records = filtered_records.filtered(lambda x: x.id not in shopfiy_records_ids)

                    barney_records = filtered_records.filtered(lambda x: x.is_barneys_dropshipping == True)
                    if barney_records:
                        barney_records_ids = barney_records.mapped('id')
                        print(barney_records_ids)
                        web_records = {}
                        sum_profit = 0
                        for sale in barney_records:
                            sku_count = len(sale.order_line.filtered(lambda pline: pline.product_id.detailed_type == "product"))
                            cogs = 0
                            deduct_cogs = 0
                            deduct_cogs_usd = 0
                            for line in sale.order_line:
                                if line.product_id.detailed_type == "product":
                                    cogs += line.product_id.standard_price * line.product_uom_qty
                                    if line.price_unit == 0.00:
                                        deduct_cogs += line.product_id.standard_price
                                        deduct_cogs_usd += deduct_cogs * 1.09
                                    if deduct_cogs:
                                        cogs -= deduct_cogs
                            picking_packing_cost = sale.company_id.picking_packing_cost if (sku_count > 0) else 0
                            additional_pick_pack = 0
                            if sku_count > sale.company_id.min_pick_pack_cost_upto_sku_count:
                                additional_pick_pack = sku_count - sale.company_id.min_pick_pack_cost_upto_sku_count
                            additional_pick_pack_cost = additional_pick_pack * sale.company_id.additional_picking_packing_cost
                            picking_packing_cost += additional_pick_pack_cost
                            payment_method_code_record = self.env["payment.method.code"].search(
                                [("workflow_id", "=", sale.auto_workflow_process_id.id)], limit=1
                            )
                            shipping_charge = (
                                sale.company_id.barneys_payment_surcharge and sale.company_id.barneys_payment_surcharge or 0.00
                            )
                            payment_surcharge = payment_method_code_record.payment_charge if payment_method_code_record else 0
                            payment_charge_amt = ((sale.amount_total * payment_surcharge) / 100) + 0.29
                            cogs_usd = cogs * 1.09
                            total_profit = sale.amount_total - payment_charge_amt - picking_packing_cost - cogs_usd - shipping_charge
                            sum_profit += total_profit
                        rounded_total = round(sum_profit,2)
                        web_records['Barneys Farm'] = "$" + " " + str(rounded_total)
                        report_lines.append({'Barneys Farm Payments' : web_records})
                        total_dict['Barneys Farm'] = total_dict.get('Barneys Farm') + rounded_total
                        filtered_records = filtered_records.filtered(lambda x: x.id not in barney_records_ids)
                    
                    dropshipping_records = filtered_records.filtered(lambda x: x.is_drop_shipping == True)
                    if dropshipping_records:
                        dropshipping_records_ids = dropshipping_records.mapped('id')
                        partner_id = self.env['res.partner'].browse(29318) #Fastbuds
                        total_sum_profit = 0
                        web_records = {}
                        for sale in dropshipping_records:
                            cogs = 0
                            shipping_cost = sale.company_id.dropshipping_shipping_cost
                            for line in sale.order_line:
                                if line.product_id.detailed_type == "product":
                                    product_price = partner_id.property_product_pricelist.item_ids.filtered(
                                        lambda pl: pl.product_tmpl_id == line.product_id.product_tmpl_id
                                    ).fixed_price
                                    cogs += product_price * line.product_uom_qty
                            sku_count = len(sale.order_line.filtered(lambda line: line.product_id.detailed_type == "product"))
                            picking_packing_cost = sale.company_id.dropshipping_picking_packing_cost if (sku_count > 0) else 0
                            additional_pick_pack = 0
                            if sku_count > sale.company_id.dropshipping_min_pick_pack_cost_upto_sku_count:
                                additional_pick_pack = sku_count - sale.company_id.dropshipping_min_pick_pack_cost_upto_sku_count
                            additional_pick_pack_cost = (
                                additional_pick_pack * sale.company_id.dropshipping_additional_picking_packing_cost
                            )
                            picking_packing_cost += additional_pick_pack_cost
                            dropship_amount = sale.amount_total - cogs - picking_packing_cost - shipping_cost
                            total_sum_profit += dropship_amount
                        rounded_total = round(total_sum_profit,2)
                        web_records['Fastbuds'] = "$" + " " + str(rounded_total)
                        report_lines.append({'Fast Buds Payments' : web_records})
                        total_dict['Fastbuds'] = total_dict.get('Fastbuds') + rounded_total
                        filtered_records = filtered_records.filtered(lambda x: x.id not in dropshipping_records_ids)

                    if filtered_records:
                        filtered_rec_ids = filtered_records.mapped('id')
                        payment_ids = records.filtered(lambda x: x.sale_id.id in filtered_rec_ids)
                        total = round(sum(payment_ids.mapped('amount_signed')),2)
                        web_records = {}
                        web_records['Others'] = total
                        total_dict['Others'] = total_dict.get('Others') + total
                        report_lines.append({'Others': web_records })

        b_cols = ['B','C','D','E','F','G','H','I','J','K']
        for line in report_lines:
            for payment_name, website_wise_list in line.items():
                column = 1
                worksheet.write(f"{az.get(column)}{row}", payment_name, bolda)
                for col in b_cols:
                    worksheet.write(f"{col}{row}",'',boldc)
                for web_name, web_value in website_wise_list.items():
                    cell = website_dict[web_name] + str(row)
                    worksheet.write(cell, web_value, center)
                    column+=1
            column = 1
            row+=1

        worksheet.write('A%s'%row,'Total', boldc)
        for key,total in total_dict.items():
            column = 1
            if total != 0:
                cell = website_dict[key] + str(row)
                worksheet.write(cell, total, boldc)
                column+=1
            else:
                cell = website_dict[key] + str(row)
                worksheet.write(cell, '', boldc)
                column+=1