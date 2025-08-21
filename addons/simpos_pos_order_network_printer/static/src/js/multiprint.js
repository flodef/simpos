/** @odoo-module **/

import { PosModel } from "@point_of_sale/app/models/pos_model";
import { patch } from "@web/core/utils/patch";
import { NetworkPrinter } from "./printers";

// Load additional fields for restaurant.printer model
PosModel.prototype.models.find(model => model.model === "restaurant.printer").fields.push("network_printer_ip");

patch(PosModel.prototype, {
    create_printer(config) {
        if (config.printer_type === "network_printer") {
            return new NetworkPrinter(config.network_printer_ip);
        } else {
            return super.create_printer(...arguments);
        }
    },
});