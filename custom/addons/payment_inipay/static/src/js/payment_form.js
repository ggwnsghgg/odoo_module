odoo.define('inipay_payment_ab.payment_form', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var PaymentForm = require('payment.payment_form');

var _t = core._t;

PaymentForm.include({

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    payEvent: function (ev) {
        console.log('[MARO] payEvent');
        ev.preventDefault();
        var checked_radio = this.$('input[type="radio"]:checked');
        var self = this;
        if (ev.type === 'submit') {
            var button = $(ev.target).find('*[type="submit"]')[0]
        } else {
            var button = ev.target;
        }

        if (checked_radio.length === 1 && checked_radio.data('provider') === 'inipay') {
            checked_radio = checked_radio[0];

            // we retrieve all the input inside the acquirer form and 'serialize' them to an indexed array
            var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
            var acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);

            this.disableButton(button);
            var $tx_url = this.$el.find('input[name="prepare_tx_url"]');
            // if there's a prepare tx url set
            if ($tx_url.length === 1) {
                // if the user wants to save his credit card info
                var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
                // then we call the route to prepare the transaction
                return this._rpc({
                    route: $tx_url[0].value,
                    params: {
                        'acquirer_id': parseInt(acquirer_id),
                        'save_token': form_save_token,
                        'access_token': self.options.accessToken,
                        'success_url': self.options.successUrl,
                        'error_url': self.options.errorUrl,
                        'callback_method': self.options.callbackMethod,
                        'order_id': self.options.orderId,
                    },
                }).then(function (result) {
                    if (result) {
                        if (config.device.isMobile) {
                            var newForm = document.createElement('form');
                            newForm.setAttribute("method", "post"); // set it to post
                            newForm.setAttribute("accept-charset","euc-kr");
                            newForm.setAttribute("provider", checked_radio.dataset.provider);
                            newForm.hidden = true; // hide it
                            newForm.innerHTML = result; // put the html sent by the server inside the form
                            var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl');
                            newForm.setAttribute("action", action_url); // set the action url
                            $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                            $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed
                            if(action_url) {
                                newForm.submit(); // and finally submit the form
                                return new Promise(function () {});
                            }
                        } else {
                            // if the server sent us the html form, we create a form element
                            var newForm = document.createElement('form');
                            newForm.setAttribute("id", "SendPayForm_id");
                            newForm.setAttribute("method", "post"); // set it to post
                            newForm.setAttribute("provider", checked_radio.dataset.provider);
                            newForm.hidden = true; // hide it
                            newForm.innerHTML = result; // put the html sent by the server inside the form
                            $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                            $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed
                            return INIStdPay.pay('SendPayForm_id');
                        }
                    } else {
                        self.displayError(
                            _t('Server Error'),
                            _t("We are not able to redirect you to the payment form.")
                        );
                        self.enableButton(button);
                    }
                }).guardedCatch(function (error) {
                    error.event.preventDefault();
                    self.displayError(
                        _t('Server Error'),
                        _t("We are not able to redirect you to the payment form.") + " " +
                        self._parseError(error)
                    );
                });
            }
        } else {
            return this._super.apply(this, arguments);
        }
    },
});
});

