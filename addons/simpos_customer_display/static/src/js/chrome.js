/** @odoo-module **/

import { Component } from "@odoo/owl";
import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

    /* User interface for distant control over the Client display on the IoT Box */
    // The boolean posbox_supports_display (in devices.js) will allow interaction to the IoT Box on true, prevents it otherwise
    // We don't want the incompatible IoT Box to be flooded with 404 errors on arrival of our many requests as it triggers losses of connections altogether
export class CustomerDisplayScreenWidget extends Component {
    static template = 'ClientScreenWidget';
    
    change_status_display(status) {
        let msg = '';
        const warningEl = this.el.querySelector('.js_warning');
        const disconnectedEl = this.el.querySelector('.js_disconnected');
        const connectedEl = this.el.querySelector('.js_connected');
        
        if (status === 'success') {
            warningEl?.classList.add('oe_hidden');
            disconnectedEl?.classList.add('oe_hidden');
            connectedEl?.classList.remove('oe_hidden');
        } else if (status === 'warning') {
            disconnectedEl?.classList.add('oe_hidden');
            connectedEl?.classList.add('oe_hidden');
            warningEl?.classList.remove('oe_hidden');
            msg = _t('Connected, Not Owned');
        } else {
            warningEl?.classList.add('oe_hidden');
            connectedEl?.classList.add('oe_hidden');
            disconnectedEl?.classList.remove('oe_hidden');
            msg = _t('Disconnected');
            if (status === 'not_found') {
                msg = _t('Client Screen Unsupported. Please upgrade the IoT Box');
            }
        }
    
        const textEl = this.el.querySelector('.oe_customer_display_text');
        if (textEl) textEl.textContent = msg;
    }
    
    setup() {
        super.setup();
        this.onClick = this.onClick.bind(this);
    }
    
    onClick() {
        this.env.pos.simpos_send_current_order_to_customer_facing_display();
    }
}

patch(Chrome.prototype, {
    setup() {
        super.setup(...arguments);
        // Customer display widget setup would be handled differently in Odoo 18
        // through component registration and template modifications
    },
    
    update_customer_screen(html) {
        return rpc("/simpos_customer_display/update_html", {
            html: html,
        });
    },
});
// Register component
CustomerDisplayScreenWidget.props = {};
    