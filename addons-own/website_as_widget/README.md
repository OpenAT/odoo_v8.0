# website_as_widget

Call webpages as widgets (without header or footer).

## Call the page from a subdomain called aswidget
http://aswidget.ahch.datadialog.net/shop

## Call the page with aswidget=True and the page widgeturl=%2Fshop
http://ahch.datadialog.net/?aswidget=True&widgeturl=%2Fshop

## Show the page normally again (with header and footer)
http://ahch.datadialog.net/?aswidget=False
This will remove the aswidget=True from the current session

## Session and Domains:
It is always better to call the i-frame url from a sub-domain URL (ahch.datadialog.net) because this will generate a
different session for the subdomain and so one could still call the website with header and footer (different session)
from the other domain (ahch.datadialog.net)

**HINT:** Keep in mind that session cookies can be shared from parent domains to child (sub) domains but not the
other way around!

## Embed the Page as an iFrame
Please look at the example html file at website_as_widget/test_iframe.html

```html
<iframe id="dadifcom" src="http://aswidget.test.com:8069/shop/category/spenden-100007"
        scrolling="no" frameborder="0" width="100%"
        style="widht:100%; border:none; padding:0; margin:0;">
</iframe>
<script type="text/javascript" src="../website_tools/static/lib/iframe-resizer/js/iframeResizer.min.js"></script>
<script>iFrameResize({log:false, checkOrigin:false, heightCalculationMethod: 'bodyScroll'}, '#dadifcom')</script>
```

https://github.com/davidjbradshaw/iframe-resizer

