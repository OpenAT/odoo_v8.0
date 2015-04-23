mail_follower_control
=====================

This addon allows better control over follower handling for the chatter view.

Goals:
------

- Checkbox "Do not automatically add as follower" for res.partner
- Set this new Checkbox to True by default
- Always show all the followers when sending an E-Mail AND allow to remove them
- CC and BCC Field for all Chatter E-Mails
    - Do NOT add BCC and CC Recipients as followers regardless of the checkbox "Do not automatically ad as follower"
- Show followers that will not receive Messages in Red
- Show followers that will seldom receive Messages in Orange
- Show a Warning when Sending an E-Mail if there are any Followers that will not receive the mail by config
