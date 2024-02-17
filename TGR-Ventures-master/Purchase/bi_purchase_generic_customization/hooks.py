from odoo.addons.purchase_stock.models.purchase import PurchaseOrder


def post_load_hook():
    # This hook add functionality to consider for not creating a picking automatically while confirm the PO
    def button_approve(self, force=False):
        result = super(PurchaseOrder, self).button_approve(force=force)
        return result

    # THIS HOOK IS ADDED TO REMOVE CHECK WHILE CANCELING THE PO
    def button_cancel(self):
        return super(PurchaseOrder, self).button_cancel()

    PurchaseOrder.button_approve = button_approve
    PurchaseOrder.button_cancel = button_cancel
