/** @odoo-module **/

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { formatCurrency } from "@web/core/currency";

patch(ReceiptScreen.prototype, {
    print() {
        const order = this.pos.get_order().export_for_printing();
        const data = {
            company: {
                phone: order.company.phone,
                contact_address: order.company.contact_address,
            },
            client: order.client,
            cashier: order.cashier,
            name: order.name,
            change: formatCurrency(order.change, this.pos.currency),
            total_with_tax: formatCurrency(order.total_with_tax, this.pos.currency),
            paymentlines: order.paymentlines.map((line) => {
                return {
                    amount: formatCurrency(line.amount, this.pos.currency),
                    payment_method: line.payment_method,
                }
            })
        }
        
        if (typeof simpos !== "undefined") {
            simpos.printReceipt(JSON.stringify(data));
        }
    },
});