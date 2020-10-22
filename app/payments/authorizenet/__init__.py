from authorizenet import apicontractsv1
from authorizenet.apicontrollers import *
from decimal import *


def get_an_accept_payment_page(success_url, cancel_url, amount, login_id, transaction_key):
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = login_id
    merchantAuth.transactionKey = transaction_key

    setting1 = apicontractsv1.settingType()
    setting1.settingName = apicontractsv1.settingNameEnum.hostedPaymentButtonOptions
    setting1.settingValue = """{"text": "Pay"}"""

    setting2 = apicontractsv1.settingType()
    setting2.settingName = apicontractsv1.settingNameEnum.hostedPaymentReturnOptions
    setting2.settingValue = '{' + f'"cancelUrl": "{cancel_url}", "cancelUrlText": "Cancel", "showReceipt": true, "url": "{success_url}", "urlText": "Continue"' + '}'

    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(setting1)
    settings.setting.append(setting2)

    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = amount

    paymentPageRequest = apicontractsv1.getHostedPaymentPageRequest()
    paymentPageRequest.merchantAuthentication = merchantAuth
    paymentPageRequest.transactionRequest = transactionrequest
    paymentPageRequest.hostedPaymentSettings = settings

    paymentPageController = getHostedPaymentPageController(paymentPageRequest)

    paymentPageController.execute()

    paymentPageResponse = paymentPageController.getresponse()

    resp = {}

    if paymentPageResponse is not None:
        if paymentPageResponse.messages.resultCode == apicontractsv1.messageTypeEnum.Ok:
            print('Successfully got hosted payment page!')

            print('Token : %s' % paymentPageResponse.token)
            resp['token'] = str(paymentPageResponse.token)

            if paymentPageResponse.messages is not None:
                resp['message_code'] = paymentPageResponse.messages.message[0]['code'].text
                resp['message_text'] = paymentPageResponse.messages.message[0]['text'].text
                print('Message Code : %s' % paymentPageResponse.messages.message[0]['code'].text)
                print('Message Text : %s' % paymentPageResponse.messages.message[0]['text'].text)
        else:
            if paymentPageResponse.messages is not None:
                print('Failed to get batch statistics.\nCode:%s \nText:%s' % (paymentPageResponse.messages.message[0]['code'].text,paymentPageResponse.messages.message[0]['text'].text))

    return (resp, paymentPageResponse)
