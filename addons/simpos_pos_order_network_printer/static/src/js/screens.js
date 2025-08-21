/** @odoo-module **/

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { renderToString } from "@web/core/utils/render";

patch(ReceiptScreen.prototype, {
    async printOrder() {
        const order = this.pos.get_order();
        const printers = this.pos.printers;
        const orderlines = order.get_orderlines();
        const order_print_data = {
            table_no: order.table_no,
            vibration_card: order.vibration_card,
            name: order.name,
            formatted_validation_date: order.formatted_validation_date,
            orderlines: [],
        };
        
        for (let i = 0; i < printers.length; i++) {
            orderlines.forEach((line) => {
                const category_ids = printers[i].config.product_categories_ids;
                if (
                    category_ids.length === 0 ||
                    this.pos.db.is_product_in_category(category_ids, line.product.id)
                ) {
                    order_print_data.orderlines.push({
                        qty: line.quantity,
                        note: line.note,
                        product_name: line.product.display_name,
                        default_code: line.product.default_code,
                    });
                }
            });
            
            if (order_print_data.orderlines.length > 0) {
                const kitchen_ticket = await renderToString("KitchenTicket", order_print_data);
                await printers[i].print_receipt(kitchen_ticket);
            }
        }
    },
});
