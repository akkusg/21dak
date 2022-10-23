# coding=utf-8

import iyzipay
import json

options = {
    'api_key': iyzipay.api_key,
    'secret_key': iyzipay.secret_key,
    'base_url': iyzipay.base_url
}


# paymentGroup values = PRODUCT, LISTING, SUBSCRIPTION
# def initialize_checkout_form(price, paidPrice, callbackUrl, buyer, shippingAddress, basketItems, billingAddress=None,
#                              conversationId=None, installment=1,
#                              paymentChannel='WEB', paymentGroup='PRODUCT', currency='TRY', locale='tr'):
#     request = {
#         'locale': locale,
#         'conversationId': conversationId,
#         'price': price,
#         'paidPrice': paidPrice,
#         'currency': currency,
#         'installment': installment,
#         'paymentChannel': paymentChannel,
#         'paymentGroup': paymentGroup,
#         'callbackUrl': callbackUrl,
#         'buyer': buyer,
#         'shippingAddress': shippingAddress,
#         'billingAddress': billingAddress if billingAddress is not None else shippingAddress,
#         'basketItems': basketItems
#     }
#
#     checkout_form_initialize = iyzipay.CheckoutFormInitialize()
#     checkout_form_initialize_response = checkout_form_initialize.create(request, options)
#
#     readable_response = checkout_form_initialize_response.read().decode('utf-8')
#     print(readable_response)
#     response_dict = json.loads(readable_response)
#     return response_dict

def initialize_checkout_form(pricingPlanReferenceCode, customer, callbackUrl, conversationId=None,
                             locale='tr', subscriptionInitialStatus='ACTIVE'):
    request = {
        'pricingPlanReferenceCode': pricingPlanReferenceCode,
        'locale': locale,
        'conversationId': conversationId,
        'callbackUrl': callbackUrl,
        'customer': customer,
        'subscriptionInitialStatus': subscriptionInitialStatus
    }

    checkout_form_initialize = iyzipay.SubscriptionCheckoutFormInitialize()
    checkout_form_initialize_response = checkout_form_initialize.create(request, options)

    readable_response = checkout_form_initialize_response.read().decode('utf-8')
    print(readable_response)
    response_dict = json.loads(readable_response)
    return response_dict


def initialize_customer(name, surname, email, gsm, identityNumber, billingAddress, shippingAddress):
    customer = {
        'name': name,
        'surname': surname,
        'gsmNumber': gsm,
        'email': email,
        'identityNumber': identityNumber,
        'billingAddress': billingAddress,
        'shippingAddress': shippingAddress
    }
    return customer


# identityNumber = TCKN
def initialize_buyer(userId, name, surname, email, identityNumber, city, ip, registrationAddress, gsm=None,
                     country='Turkey'):
    buyer = {
        'id': userId,
        'name': name,
        'surname': surname,
        'gsmNumber': gsm,
        'email': email,
        'identityNumber': identityNumber,
        'registrationAddress': registrationAddress,
        'ip': ip,
        'city': city,
        'country': country
    }
    return buyer


def initialize_address(contactName, city, address, country='Turkey'):
    address = {
        'contactName': contactName,
        'city': city,
        'address': address,
        'country': country
    }
    return address


def initialize_basket_item(itemId, name, price, itemType='VIRTUAL', category1='Subscription', category2=None):
    basketItem = {
        'id': itemId,
        'itemType': itemType,
        'name': name,
        'category1': category1,
        'category2': category2,
        'price': price
    }
    return basketItem