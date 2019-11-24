/**
 * @license Copyright (c) 2003-2019, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function (config) {
  // Define changes to default configuration here. For example:
  // config.language = 'fr';
  // config.uiColor = '#AADC6E';
  	config.image_previewText = ' ';
  	config.filebrowserImageUploadUrl = "/upload/";
  	config.uiColor = '#9AB8F3';
 	config.toolbar = [
      	['Smiley'],
      	['Bold', 'Italic', 'Underline', 'RemoveFormat', 'Blockquote'],
      	['TextColor', 'BGColor'],
      	['Image', 'Table', 'Link', 'Unlink'],
      	['NumberedList', 'BulletedList'],
      	['Maximize']
	];
	config.skin = 'moono-lisa';
	config.tabSpaces = 4;
};