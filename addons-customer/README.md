# addons-customer

Die Addons in diesem Ordner dienen der Individualissierung von einzelnen Datenbanken. Meist beinhalten sie individuelle 
CSS und Anpassungen an der Übersetzung (*.po Dateien).

## Wichtige Hinweise:

Diese Grundregeln sind unbedingt einzuhalten:

- Die Addons-Ordner werden nur der git-Branch hinzugefügt in der die zugehörige Datenbank läuft. 
 Z.B.: in der branch intdadi oder intdadirl1 also NICHT in der Master Branch!
- Die Addons werden nicht in addons-loaded symblisch verlinkt sondern in den speziellen addons ordner der nur für die
 jeweilige Datenbank geladen wird. Dieser befindet sich im DB-Ordner (z.B.: o8_intdadi_datadialog/addons) - dieser wird
 nicht in git geführt - daher haben Fehler in diesen Addons auf die anderen Branches und Installationen keinen Einfluss!
- Die Ordnernamen der addons sollten so aussehen: customer_pfot (Also customer_ + Kundenkürzel)
