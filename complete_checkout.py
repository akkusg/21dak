# coding=utf-8

import iyzipay
import json

options = {
    'api_key': iyzipay.api_key,
    'secret_key': iyzipay.secret_key,
    'base_url': iyzipay.base_url
}


def complete_checkout_form(token, locale='tr', conversationId=None):
    request = {
        'locale': locale,
        'conversationId': conversationId,
        'token': token,
    }

    checkout_form = iyzipay.CheckoutForm()
    checkout_form_complete_response = checkout_form.retrieve(request, options)

    readable_response = checkout_form_complete_response.read().decode('utf-8')
    print(readable_response)
    response_dict = json.loads(readable_response)
    return response_dict
