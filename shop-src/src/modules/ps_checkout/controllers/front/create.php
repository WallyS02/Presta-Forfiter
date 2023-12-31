<?php

/**
 * Copyright since 2007 PrestaShop SA and Contributors
 * PrestaShop is an International Registered Trademark & Property of PrestaShop SA
 *
 * NOTICE OF LICENSE
 *
 * This source file is subject to the Academic Free License version 3.0
 * that is bundled with this package in the file LICENSE.md.
 * It is also available through the world-wide-web at this URL:
 * https://opensource.org/licenses/AFL-3.0
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@prestashop.com so we can send you a copy immediately.
 *
 * @author    PrestaShop SA and Contributors <contact@prestashop.com>
 * @copyright Since 2007 PrestaShop SA and Contributors
 * @license   https://opensource.org/licenses/AFL-3.0 Academic Free License version 3.0
 */

use PrestaShop\Module\PrestashopCheckout\Controller\AbstractFrontController;
use PrestaShop\Module\PrestashopCheckout\Exception\PsCheckoutException;
use PrestaShop\Module\PrestashopCheckout\Handler\CreatePaypalOrderHandler;
use PrestaShop\Module\PrestashopCheckout\PayPal\PayPalConfiguration;
use PrestaShop\Module\PrestashopCheckout\Repository\PsCheckoutCartRepository;

/**
 * This controller receive ajax call to create a PayPal Order
 */
class Ps_CheckoutCreateModuleFrontController extends AbstractFrontController
{
    /**
     * @var Ps_checkout
     */
    public $module;

    /**
     * @see FrontController::postProcess()
     *
     * @todo Move logic to a Service
     */
    public function postProcess()
    {
        try {
            // BEGIN Express Checkout
            $bodyValues = [];
            $bodyContent = file_get_contents('php://input');

            if (false === empty($bodyContent)) {
                $bodyValues = json_decode($bodyContent, true);
            }

            if (isset($bodyValues['quantity_wanted'], $bodyValues['id_product'], $bodyValues['id_product_attribute'], $bodyValues['id_customization'])) {
                $cart = new Cart();
                $cart->id_currency = $this->context->currency->id;
                $cart->id_lang = $this->context->language->id;
                $cart->add();
                $isQuantityAdded = $cart->updateQty(
                    (int) $bodyValues['quantity_wanted'],
                    (int) $bodyValues['id_product'],
                    empty($bodyValues['id_product_attribute']) ? null : (int) $bodyValues['id_product_attribute'],
                    empty($bodyValues['id_customization']) ? false : (int) $bodyValues['id_customization'],
                    $operator = 'up'
                );

                if (!$isQuantityAdded) {
                    $this->exitWithResponse([
                        'status' => false,
                        'httpCode' => 400,
                        'body' => [
                            'error' => [
                                'message' => 'Failed to update cart quantity.',
                            ],
                        ],
                        'exceptionCode' => null,
                        'exceptionMessage' => null,
                    ]);
                }

                $cart->update();

                $this->module->getLogger()->info(
                    'Express checkout : Create Cart',
                    [
                        'id_cart' => (int) $cart->id,
                    ]
                );

                $this->context->cart = $cart;
                $this->context->cookie->__set('id_cart', (int) $cart->id);
                $this->context->cookie->write();
            }
            // END Express Checkout

            if (false === Validate::isLoadedObject($this->context->cart)) {
                $this->exitWithResponse([
                    'httpCode' => 400,
                    'body' => 'No cart found.',
                ]);
            }

            /** @var PsCheckoutCartRepository $psCheckoutCartRepository */
            $psCheckoutCartRepository = $this->module->getService('ps_checkout.repository.pscheckoutcart');

            /** @var PsCheckoutCart|false $psCheckoutCart */
            $psCheckoutCart = $psCheckoutCartRepository->findOneByCartId((int) $this->context->cart->id);

            $isExpressCheckout = (isset($bodyValues['isExpressCheckout']) && $bodyValues['isExpressCheckout']) || empty($this->context->cart->id_address_delivery);

            if (false !== $psCheckoutCart && $psCheckoutCart->isExpressCheckout() && $psCheckoutCart->isOrderAvailable()) {
                $this->exitWithResponse([
                    'status' => true,
                    'httpCode' => 200,
                    'body' => [
                        'orderID' => $psCheckoutCart->paypal_order,
                    ],
                    'exceptionCode' => null,
                    'exceptionMessage' => null,
                ]);
            }

            // If we have a PayPal Order Id with a status CREATED or APPROVED or PAYER_ACTION_REQUIRED we mark it as CANCELED and create new one
            // This is needed because cart gets updated so we need to update paypal order too
            if (
                false !== $psCheckoutCart && $psCheckoutCart->getPaypalOrderId()
            ) {
                $psCheckoutCart->paypal_status = PsCheckoutCart::STATUS_CANCELED;
                $psCheckoutCartRepository->save($psCheckoutCart);
                $psCheckoutCart = false;
            }

            $paypalOrder = new CreatePaypalOrderHandler($this->context);
            $response = $paypalOrder->handle($isExpressCheckout);

            if (false === $response['status']) {
                throw new PsCheckoutException($response['exceptionMessage'], (int) $response['exceptionCode']);
            }

            if (empty($response['body']['id'])) {
                throw new PsCheckoutException('Paypal order id is missing.', PsCheckoutException::PAYPAL_ORDER_IDENTIFIER_MISSING);
            }

            $paymentSource = isset($response['body']['payment_source']) ? key($response['body']['payment_source']) : 'paypal';
            $fundingSource = isset($bodyValues['fundingSource']) ? $bodyValues['fundingSource'] : $paymentSource;
            $orderId = isset($bodyValues['orderID']) ? $bodyValues['orderID'] : null;
            $isExpressCheckout = isset($bodyValues['isExpressCheckout']) && $bodyValues['isExpressCheckout'];
            $isHostedFields = isset($bodyValues['isHostedFields']) && $bodyValues['isHostedFields'];
            /** @var PayPalConfiguration $configuration */
            $configuration = $this->module->getService('ps_checkout.paypal.configuration');

            $this->module->getLogger()->info(
                'PayPal Order created',
                [
                    'PayPalOrderId' => $orderId,
                    'FundingSource' => $fundingSource,
                    'isExpressCheckout' => $isExpressCheckout,
                    'isHostedFields' => $isHostedFields,
                    'id_cart' => (int) $this->context->cart->id,
                    'amount' => $this->context->cart->getOrderTotal(true, Cart::BOTH),
                    'environment' => $configuration->getPaymentMode(),
                    'intent' => $configuration->getIntent(),
                ]
            );

            if (false === $psCheckoutCart) {
                $psCheckoutCart = new PsCheckoutCart();
                $psCheckoutCart->id_cart = (int) $this->context->cart->id;
            }

            $psCheckoutCart->paypal_funding = $fundingSource;
            $psCheckoutCart->paypal_order = $response['body']['id'];
            $psCheckoutCart->paypal_status = $response['body']['status'];
            $psCheckoutCart->paypal_intent = $configuration->getIntent();
            $psCheckoutCart->paypal_token = $response['body']['client_token'];
            $psCheckoutCart->paypal_token_expire = (new DateTime())->modify('+3550 seconds')->format('Y-m-d H:i:s');
            $psCheckoutCart->environment = $configuration->getPaymentMode();
            $psCheckoutCart->isExpressCheckout = isset($bodyValues['isExpressCheckout']) && $bodyValues['isExpressCheckout'];
            $psCheckoutCart->isHostedFields = isset($bodyValues['isHostedFields']) && $bodyValues['isHostedFields'];
            $psCheckoutCartRepository->save($psCheckoutCart);

            $this->exitWithResponse([
                'status' => true,
                'httpCode' => 200,
                'body' => [
                    'orderID' => $psCheckoutCart->paypal_order,
                ],
                'exceptionCode' => null,
                'exceptionMessage' => null,
            ]);
        } catch (Exception $exception) {
            $this->module->getLogger()->error(
                'CreateController - Exception ' . $exception->getCode(),
                [
                    'exception' => $exception,
                ]
            );

            $this->exitWithExceptionMessage($exception);
        }
    }
}
