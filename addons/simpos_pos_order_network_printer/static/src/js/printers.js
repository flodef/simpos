/** @odoo-module **/

import { PrinterMixin } from "@point_of_sale/app/printer/printer_mixin";

export class NetworkPrinter extends PrinterMixin {
    constructor(ip) {
        super(...arguments);
        this.ip = ip;
    }

    /**
     * @override
     */
    send_printing_job(img) {
        if (typeof simpos !== "undefined") {
            const ip = this.ip;
            javascript: simpos.printRestaurantOrder(ip + "SIMPOS" + img);
        }
    }
    
    _onIoTActionFail() {}
    _onIoTActionResult() {}
}
