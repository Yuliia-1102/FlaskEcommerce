from intasend import APIService

API_PUBLISHABLE_KEY = 'ISPubKey_test_31387f66-10f3-47e5-aecc-a3313f784300'

API_TOKEN = 'ISSecretKey_test_c8481a22-3e9f-4461-b2c4-7dacade85628'


service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)

create_order = service.collect.mpesa_stk_push(phone_number='254712345678', email='test@gmail.com',
                                              amount=200, narrative='Purchase Order', currency='UAH')

print(create_order)