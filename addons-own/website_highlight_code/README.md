ckeditor_advanced
=================

All changes, for plugins, extra buttons ... for the integrated ckeditor of odoo belongs here.

Also additional Styles, Fonts, Symbols ... will be integrated here.


Tasks:
------
- Add Syntax highlight plugin to ckeditor and enable corresponding button in webcms
- Add plugin to ckeditor to embedd gists
- Add plugin in ckeditor to show files or part of files from github

Info:
-----
http://stackoverflow.com/questions/12531002/change-ckeditor-toolbar-dynamically
http://cdn.ckeditor.com/
http://docs.ckeditor.com/
http://docs.ckeditor.com/#!/api/CKEDITOR.plugins-method-addExternal
http://pierrebaron.fr/pbckcode/docs/
https://highlightjs.org/download/
http://stackoverflow.com/questions/20900041/how-to-remove-event-listeners-while-destroying-ckeditor
http://docs.ckeditor.com/#!/guide/dev_jquery
http://stackoverflow.com/questions/1794219/ckeditor-instance-already-exists

http://ace.c9.io/#nav=about
https://github.com/ajaxorg/ace-builds
http://www.jsdelivr.com/#!ace
http://cdnjs.com/libraries/ace/

CKEDITOR.instances.content.destroy()
CKEDITOR.replace('content', {uiColor: '#9AB8F3', removeButtons: ""})

CKEditor will be loaded by website addon already for every input with id editor! Becuse of this the editor is already
loaded even if website_forum.js is not.


document.getElementsByTagName("CODE")[0].textContent = document.getElementsByTagName("CODE")[0].textContent;