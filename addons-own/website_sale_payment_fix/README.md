website_sale_payment_fix
========================

This addon fixes the session depended payment process of odoo 8.0 website_sale shop in combination with the 
payment_ogone_dadi payment provider which is a replacement of the odoo ogone payment provider.

The problem of the original odoo payment process is that the update of the payment transaction and the related sales
order is dependent on the data of the current request.session. But it might be that the answer from ogone is received 
later and not related to the current session at all and also send by ogone multible times for the same or different 
states of the particullar payment.transaction.

To solve this we did:
- **clear the session variables** sale_order_id, sale_last_order_id, sale_transaction_id, sale_order_code_pricelist_id
  so a new Sales Order would be generated if the user opens the shop again.
  AND **set the sales order to state bestätigt** so that no changes are possible
  after the button of the PP in shop/payment is pressed (JSON calls method payment_transaction in website_sale main.py)
  
- If we receive an answer from the PP **all the logic for the Sales Order is done at method form_feedback** (website_sale
  did this already partially for setting the SO to state done but did not react to all possible states) so we do no
  longer depend on /shop/payment/validate to set the other states for the SO. This was needed because payment_validate
  did use session variables to find the payment.transaction and the sales.order but since the answer of the PP can be
  defered this is not always correct.
  
- Make a lot of fields of Payment.transaction readonly in the form since they should be only changed by the answer of
  the PP and not by the user expecailly because changing the state of a TX would NOT! change the SO state since this
  is done now and form_validate and before this addon in /shop/payment/validate.
  
- Make the Filed in the sales order for the linke TX read only - should only be set by code not by humans ;)

- All the other stuff is done in the addon payment_ogone_dadi - read its description too!