$(document).ready(function() {
$('#inputCsv').on('change', function() {
$("#preview").html('');
$("#preview").html('<img src="loader.gif" alt="Uploading...."/>');
$("#upload_form").ajaxForm({
//target: '#preview'
}).submit();
});
});
