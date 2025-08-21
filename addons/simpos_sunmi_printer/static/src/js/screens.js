/** @odoo-module **/

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { renderToString } from "@web/core/utils/render";

patch(ReceiptScreen.prototype, {
    handle_auto_print() {
      if (this.should_auto_print() && !this.pos.get_order().is_to_email()) {
        this.print(2);
        if (this.should_close_immediately()) {
          this.click_next();
        }
      } else {
        this.lock_screen(false);
      }
    },
    async print(time) {
      const receipt = await renderToString("OrderReceipt", this.get_receipt_render_env());
      
      const result = await this.htmlToImg(receipt);
      if (typeof simpos === "undefined") {
        this.print_web();
      } else {
        if (time === 2) {
          javascript: simpos.printDoubleReceipt(result);
        } else {
          javascript: simpos.printReceipt(result);
        }
      }

      this.pos.get_order()._printed = true;
      if (this.printOrder) {
        this.printOrder();
      }
    },
    htmlToImg(receipt) {
      $(".pos-receipt-print").html(receipt);
      return new Promise((resolve, reject) => {
        this.receipt = $(".pos-receipt-print .pos-receipt");
        html2canvas(this.receipt[0], {
          onparsed: (queue) => {
            queue.stack.ctx.height = Math.ceil(
              this.receipt.outerHeight() + this.receipt.offset().top
            );
          },
          onrendered: (canvas) => {
            $(".pos-receipt-print").empty();
            resolve(this.process_canvas(canvas));
          },
        });
      });
    },
    process_canvas(canvas) {
      return canvas
        .toDataURL("image/jpeg")
        .replace("data:image/jpeg;base64,", "");
    },
});
