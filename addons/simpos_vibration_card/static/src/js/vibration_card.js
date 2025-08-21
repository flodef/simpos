/** @odoo-module **/

import { Order } from "@point_of_sale/app/models/order";
import { ActionButtonWidget } from "@point_of_sale/app/screens/product_screen/action_button/action_button";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AbstractAwaitablePopup } from "@web/core/popups/popup";
import { Component } from "@odoo/owl";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.vibration_card = this.vibration_card || "";
        this.table_no = this.table_no || "";
    },
    set_vibration_card(vibration_card) {
        this.vibration_card = vibration_card;
        this.trigger('change', this);
    },
    get_vibration_card() {
        return this.vibration_card;
    },
    set_table_no(table_no) {
        this.table_no = table_no;
        this.trigger('change', this);
    },
    get_table_no() {
        return this.table_no;
    },
    export_as_JSON() {
        const json = super.export_as_JSON();
        json.vibration_card = this.vibration_card;
        json.table_no = this.table_no;
        return json;
    },
    export_for_printing() {
        const receipt = super.export_for_printing(...arguments);
        receipt.vibration_card = this.get_vibration_card();
        receipt.table_no = this.get_table_no();
        return receipt;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.vibration_card = json.vibration_card;
        this.table_no = json.table_no;
    },
});

export class OrderlineVibrationCardButton extends ActionButtonWidget {
    static template = 'OrderlineVibrationCardButton';
    
    get vibrationCardNumber() {
        if (this.pos.get_order()) {
            return this.pos.get_order().vibration_card;
        }
    }
    
    async onClick() {
        const order = this.pos.get_order();
        if (order) {
            const { confirmed, payload } = await this.popup.add(SelectVibrationCardPopup, {
                title: _t('Set Vibration Card Number'),
                value: order.get_vibration_card(),
                list: [1,2,3,4,5,6,7,8,9,10],
            });
            
            if (confirmed) {
                order.set_vibration_card(payload);
                this.render();
            }
        }
    }
}

// Register the action button component
OrderlineVibrationCardButton.props = {};


export class OrderlineTableNoButton extends ActionButtonWidget {
    static template = 'OrderlineTableNoButton';
    
    get tableNo() {
        if (this.pos.get_order()) {
            return this.pos.get_order().table_no;
        }
    }
    
    async onClick() {
        const order = this.pos.get_order();
        if (order) {
            const { confirmed, payload } = await this.popup.add(SelectVibrationCardPopup, {
                title: _t('Set Table'),
                value: order.get_table_no(),
                list: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
            });
            
            if (confirmed) {
                order.set_table_no(payload);
                this.render();
            }
        }
    }
}

// Register the action button component
OrderlineTableNoButton.props = {};
export class SelectVibrationCardPopup extends AbstractAwaitablePopup {
    static template = "SelectVibrationCardPopupWidget";
    static props = {
        title: String,
        value: { type: [String, Number], optional: true },
        list: { type: Array, optional: true },
    };
    
    setup() {
        super.setup();
        this.list = this.props.list || [];
        this.selectedValue = this.props.value;
    }
    
    clickItem(event) {
        const value = parseInt(event.target.dataset.itemIndex);
        this.confirm({ confirmed: true, payload: value });
    }
    
    clickConfirm() {
        this.confirm({ confirmed: true, payload: undefined });
    }
    
    clickCancel() {
        this.confirm({ confirmed: false, payload: null });
    }
}

// Register popup
SelectVibrationCardPopup.defaultProps = {
    confirmText: _t('Confirm'),
    cancelText: _t('Cancel'),
    title: _t('Select'),
};
