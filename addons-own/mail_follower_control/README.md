# mail_follower_control

This addon allows better control over follower handling for the chatter view.

## Goals:

- Checkbox "Do not automatically add as follower" for res.partner
- Set this new Checkbox to True by default
- Show the followers and additional recipients that will receive an email (notify always + email)
- Show a warning when adding additional recipients if the new recipient will not receive an email
- Show followers that will not receive Messages in Red
- Write the followers that received an email to mail.message in a new field to view them in message thread views

- ToDo: Always show all the followers when writing a message in full message composer
    - ToDo: Allow to remove some followers just for the current mail
- ToDo: BCC Field for all Chatter E-Mails
    - ToDo: Do NOT add BCC Recipients as followers regardless of the checkbox "Do not automatically ad as follower"



