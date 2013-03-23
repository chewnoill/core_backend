var submit_vars={};
$(document).ready(function() {
	$('#submit').click(function(){
		submit();
	});
	$('#loading').addClass('hideLoader');
	$('#loading').removeClass('showLoader');
});

function submit(){
	
	var data = {};
	username=$('#username').val();
	if(username && username.length>0){
		data['username']=username;
	}
	password=$('#password').val();
	if(password && password.length>0){
		data['password']=password;
	}
	data['type']=$('#action_type').val(),
	
	$('#loading').addClass('showLoader');
	$('#loading').removeClass('hideLoader');
	
	$.post('/handler.html',JSON.stringify(data),function(data){
		$('#loading').addClass('hideLoader');
		$('#loading').removeClass('showLoader');
		data = JSON.parse(data);
		data = JSON.stringify(data, undefined, 4);
		$('#output').children().remove();
		var json_stuff = $('<pre>');
		var out = syntaxHighlight(data);
		json_stuff[0].innerHTML = out;
		$('#output').append(json_stuff);

	});
	
}

function syntaxHighlight(json) {
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'number';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'key';
            } else {
                cls = 'string';
            }
        } else if (/true|false/.test(match)) {
            cls = 'boolean';
        } else if (/null/.test(match)) {
            cls = 'null';
        }
        return '<span class="' + cls + '">' + match + '</span>';
    });
}


