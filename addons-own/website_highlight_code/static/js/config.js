/**
 * @license Copyright (c) 2003-2014, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.html or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For the complete reference:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

    config.skin = 'bootstrapck,/website_highlight_code/static/lib/ckeditor_skins/bootstrapck/';

    config.extraPlugins = 'pbckcode,maximize';

    // config.toolbar = null;

	//The toolbar groups arrangement, optimized for a single toolbar row.
	config.toolbarGroups = [
		{ name: 'document',	   groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
		{ name: 'forms' },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align', 'bidi' ] },
		{ name: 'links' },
		{ name: 'insert' },
		{ name: 'styles' },
		{ name: 'colors' },
		{ name: 'tools' },
		{ name: 'others' },
		{ name: 'about' },
        { name: 'pbckcode' }
	];

    //config.toolbarGroups = null;

    //config.uiColor = '#9AB8F3';

    config.contentsCss = '/web/css/website.assets_frontend';

	// The default plugins included in the basic setup define some buttons that
	// we don't want too have in a basic editor. We remove them here.
	// config.removeButtons = 'Cut,Copy,Paste,Undo,Redo,Anchor,Underline,Strike,Subscript,Superscript';

	// Let's have it basic on dialogs as well.
	// config.removeDialogTabs = 'link:advanced';

    // These rules do only work in here (for the output), but not for the input (linebreaks etc)

    // allow <script> tags
    //config.protectedSource.push( /<(script)[^>]*>.*<\/script>/ig );

    // allow <?php ?> tags
    //config.protectedSource.push( /<\?[\s\S]*?\?>/ig );

    // allow imageselectorplus mediainsert tag code
    //config.protectedSource.push( /<mediainsert[\s\S]*?\/mediainsert>/img );

    // set placeholder tag cases
    //config.extraAllowedContent = 'mediainsert(*)[*]{*}; script(*)[*]{*} ;pre(*){*}[*]';

     // PBCKCODE CUSTOMIZATION
     config.pbckcode = {
         // An optional class to your pre tag.
         cls : '',

         // The syntax highlighter you will use in the output view
         highlighter : 'PRISM',

         // An array of the available modes for you plugin.
         // The key corresponds to the string shown in the select tag.
         // The value correspond to the loaded file for ACE Editor.
         modes :  [
             ['SH', 'sh'], ['Powershell' , 'powershel1'], ['Markdown' , 'markdown'],
             ['HTML', 'html'], ['CSS', 'css'], ['LESS' , 'less'],
             ['Python' , 'python'], ['JS', 'javascript'], ['XML', 'xml'], ['JSON' , 'json'],
             ['pgSQL', 'pgsql'], ['SQL', 'sql']
         ],

         // The theme of the ACE Editor of the plugin.
         //theme : 'monokai',

         // Tab indentation (in spaces)
         tab_size : '4',

         // load a specific version of ace
         //js : "http://cdn.jsdelivr.net/ace/1.1.9/noconflict/"
         js : "/website_highlight_code/static/lib/ace-builds-master/src-min-noconflict/"
     };

};
