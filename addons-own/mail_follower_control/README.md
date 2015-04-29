# mail_follower_control

This addon allows better control over follower handling for the chatter view.

## Goals:

- Checkbox "Do not automatically add as follower" for res.partner
- Set this new Checkbox to True by default
- Show the followers and additional recipients that will receive an email (notify always + email)
- Show a warning when adding additional recipients if the new recipient will not receive an email
- Show followers that will not receive Messages in Red

- ToDo: Write the followers that received an email to mail.message in a new field
    - show this field in the message (chatter) view: e-mail send to:

- ToDo: Always show all the followers when writing a message in full message composer
    - ToDo: Allow to remove some followers just for the current mail
- ToDo: BCC Field for all Chatter E-Mails
    - ToDo: Do NOT add BCC Recipients as followers regardless of the checkbox "Do not automatically ad as follower"



## Technische Informationen

Das System besteht aus den drei großen Klassen mail_mail, mail_message und mail_followers.

Wird eine Nachricht über den Schnellversand geschrieben wird passiert im Groben folgendes:


Beim Klick auf **"Sende eine Nachricht"** wird im JS **mail.js** **mail.ThreadComposeMessage = mail.MessageCommon.extend** 
aufgerufen diese bezieht sich auf das QWeb template **mail.compose_message** in **mail.xml**. Die python Klasse von der die
Daten für das Template kommen ist die **mail_compose_message** welche von **mail.message** ableitet.

mail.js mail.ThreadComposeMessage holt sich folgende wichtige Informationen von mail_compose_message:
- this.recipients = []
- this.recipient_ids = []

mail.ThreadComposeMessage leitet bereits von **mail.MessageCommon** = session.web.Widget.extend( ab und hat daher
- this.partner_ids
- ... und fas alle anderen Felder von Python mail_compose_message und daher auch mail_message

Todo: Wir erweitern dies dann später um:
- this.message_follower_ids

### mail.js > mail.ThreadComposeMessage > check_recipient_partners()
Sie überprüft die Angehakten receipients und übergibt diese dann offensichtlich auch der on_compose_fullmail function.
 
Wird durch mehrere Punkte im JS gestartet.

**Wie werden die Receipients ermittelt?**

**Neue Liste / neues Feld 


