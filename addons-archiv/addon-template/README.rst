## Customer Website Addon

#### put this module into the addons folder in your customers instance and rename it to cu_aaaa depending on your customers index

- find and replace
    grep -rl cu_herz ./addons/cu_herz/ | xargs sed -i 's/cu_aaaa/cu_herz/g'
    find "cu_aaaa" --> replace with example customer --> "cu_herz"
    find "CUSTOMERDOMAINNAME" Replace it with "http://herzbewegt.demo.datadialog.net/"
    find "CUSTOMERNAME" Replace it with "Herzbewegt"

No you can start editing the scss files to rewrite the color codes and special customer modufications