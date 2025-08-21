/** @odoo-module **/

import { OrderWidget } from "@point_of_sale/app/screens/product_screen/order_widget";
import { patch } from "@web/core/utils/patch";

patch(OrderWidget.prototype, {
    set_value(val) {
        const order = this.pos.get_order();
        if (order.get_selected_orderline()) {
            super.set_value(val);
            this.pos.simpos_send_current_order_to_customer_facing_display();
        }
    },
});
