# Iyzipay API python client
# API docs at https://iyzico.com
# Authors:
# Yalcin Yenigun <yalcin.yenigun@iyzico.com>
# Nurettin Bakkal <nurettin.bakkal@iyzico.com>

# Configuration variables

# Test variables
# api_key = 'sandbox-YMs6UcqbxBdJJQgqdjRpMuiactLcbZZ2'
# secret_key = 'sandbox-HMEFOB0WeCvJd099aPvmbxlVqSscTAkD'
# base_url = 'sandbox-api.iyzipay.com'

# Prod variables
api_key = 'yhty8FzISwCi4d9sCEr3GnYMyAv4kIsx'
secret_key = '8GNjt6HElrqff5Or3gYzHCl5vmlZZlVz'
base_url = 'api.iyzipay.com'

# Resource
from iyzipay.iyzipay_resource import (  # noqa
    ApiTest,
    BinNumber,
    InstallmentInfo,
    Approval,
    Disapproval,
    CheckoutFormInitialize,
    CheckoutForm,
    Payment,
    ThreedsInitialize,
    ThreedsPayment,
    Cancel,
    Refund,
    Card,
    CardList,
    Bkm,
    BkmInitialize,
    PeccoInitialize,
    PeccoPayment,
    CheckoutFormInitializePreAuth,
    PaymentPreAuth,
    PaymentPostAuth,
    ThreedsInitializePreAuth,
    RefundChargedFromMerchant,
    PayoutCompletedTransactionList,
    BouncedBankTransferList,
    SubMerchant,
    CrossBookingToSubMerchant,
    CrossBookingFromSubMerchant,
    BasicPayment,
    BasicPaymentPreAuth,
    BasicPaymentPostAuth,
    BasicThreedsInitialize,
    BasicThreedsInitializePreAuth,
    BasicThreedsPayment,
    BasicBkm,
    BasicBkmInitialize,
    RetrievePaymentDetails,
    RetrieveTransactions,
    IyziLinkProduct,
    IyziFileBase64Encoder,
    SubscriptionCheckoutFormInitialize,
    SubscriptionCheckoutForm
)

from iyzipay.pki_builder import (  # noqa
    PKIBuilder)

