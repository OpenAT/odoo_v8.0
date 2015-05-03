# Payment Provider FRST


Dier Payment Provider ist speziel für das FRST gedacht. Er ermöglicht es Spenden (Einmal- oder Dauerspenden) per 
 Bankeinzug (IBAN u. BIC) zu tätigen. Es wurde eine java Script Form Validation eingebaut um die IBAN und BIC Nummer
 zu überprüfen.
 
# Doku: Ablauf des Checkout Prozesses in odoo
 
Die Basis für den Bezahlvorgang auf der Webseite ist das addon website_sale dieser wiederum integrierte alle payment_*
 addon payment provider über das Brückenmodul website_payment welches wiederum das addon payment einbindet.

## Addons:
- sale              = zuständig für sales.order
- payment           = basis modul (framework) für alle payment provider
- payment_*         = payment providers (paypla, adyen, ogone)
- website_payment   = bridge addon zum einbinden der payment provider in die webseite
- website_sale      = odoo shop system

## Ablauf eines Checkoutvorganges (nicht eingeloggt):

Im Folgenden werden wir einen Shop Checkout Vorgang durchgehen. Wobei es hier nicht um Vollständigkeit geht sondern 
 lediglich darum den Forgang im Kern zu verstehen:

### 1.) Produkt auf der Produktseite in den Warenkorb legen

```python
@http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
    ...
    return request.website.render("website_sale.product", values)
```

Das Produkt wird auf seiner Produktseite angezeigt. Suche und Kategorie werden dabei in den GET Variablen 
 berücksichtigt. Die Preisliste wird über ```get_pricelist()``` bestimmt und mitgegeben. das Feld product.price ist
 dabei bereits selbst ein functional field das die derzeitige preisliste berücksichtigt user_id ist dabei in jeder
 web session verfügbar: user_id wird benötigt um festzustellen welche preisliste und währung der aktuelle user hat.
 Ist kein user eingeloggt so gibt es dennoch einen default user der automatisch der website session (bzw. dem request)
 zugeordent wird.

TIP: Alle Qweb Templates für den Shop finden sich unter addons/website_sale/views/templates.xml.

#### Preis eines Produktes
Der Finale Preis eines Produktes wird über die user_id die Preisliste und die Währung der Webpage bestimmt.
 Er kann über product.price ausgelesen werden. Dies funktioniert da dies ein functional Feld ist (siehe Erklärung 
 weiter oben).

Im qweb template für Produkte website_sale.product wird das template product_price aufgerufen. Hier wird angezeigt

- Der aktuelle Listenpreis angezeigt über t-field="product.lst_price" Wenn dieser aufgrund der preisliste größer ist als der product.price (visible discounts)
- Der aktuelle Preis angezeigt über t-field="product.price"

TIP: Es wird anderer HTML Code angezeigt je nachdem ob man im Editor Modus ist oder nicht. Dies geschieht über die CSS
 Klasse css_editable_mode_hidden bzw. css_editable_mode_display

#### Add to Cart
Um das Produkt nun dem Warenkorb zuzuführen gibt es einen Button add_to_cart. Dieser submittet die überliegende Form
 an /shop/cart/update. Die einzige relevante post data information dieser form ist die produktmenge alles andere wird 
 über die user_id, product id usw. berechnet.
``` html
<form t-att-action="keep('/shop/cart/update')" class="js_add_cart_variants" method="POST">
    ...
    <a id="add_to_cart" class="btn btn-primary btn-lg mt8 js_check_product a-submit" href="#">Add to Cart</a>
```

In dem Webcontroller /shop/cart/update (addons/website_sale/controllers/main.py) wird nun das erste mal die zentrale 
 Funktion sale_get_order aufgerufen und eine sales.order erstellt und diese mittels der Funktion _cart_update 
 direkt aktualisiert.
 ```
 request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id), add_qty=float(add_qty), set_qty=float(set_qty))
 ```
 
Die Funktion _cart_update die in der methode sale_get_order aufgerufen wird überprüft ob es bereits sales.order.lines 
 für diese Produkt id gibt und aktualisiert diese sofern die Menge nicht unter 0 gesinken ist. Die values für die 
 Aktualisierung der sales.order.line werden dabei über 
 ```
 values = self._website_product_id_change(cr, uid, ids, so.id, product_id, qty=quantity, line_id=line_id, context=context)
 ```
 geholt. und mit ``values['product_uom_qty'] = quantity``` vor dem write aktualisiert. 
 

TIP vor TIP :): Wahrscheinlich ist es leichter die beiden controller 
```
@http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
```
und
```
@http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
```
zu übernhemen und dort jeweils ._cart_update mit den kw_args aufzurufen - dazu kommt das wir _cart_update so verändern 
müssen das 
A) wert aus kwargs für price_units sale.order.line übernommen wird 
B) WEIN KEIN WERT IN KWARGS dann bestehernder wert für price_unit in sale.order.line WENN unterschied zu price_unit
C) 


 
TIP: um nun später unsere Funktion zu realisieren, den preis frei wählen zu können, erweitern wir in der Funktion 
 _cart_update die values um values['price_unit'] = kwargs['price_donate']  um in die sales.order.line den preis 
 aus den kwargs der post form data (/shop/cart/update) des website kontrollers shop/product/<model("product.template"):product>
 in die sales.order.line zu schreiben
 
 - depend on website_sale
 - inherit sale-order
 - extend _cart_update to include a new value of the **kwargs price_donate as price_unit submited py the add to cart form
 - 

 INFOS:
 
 Use Qweb Variables outside of Loops?
 https://github.com/odoo/odoo/issues/4461
 
 get id by xml id
 http://stackoverflow.com/questions/8666809/how-to-get-the-database-id-from-an-xml-id

