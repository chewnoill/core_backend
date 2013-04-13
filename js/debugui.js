var submit_vars={};
$(document).ready(function() {
	$('#submit').click(function(){
		submit();
	});
	$('#loading').addClass('hideLoader');
	$('#loading').removeClass('showLoader');
	$('#action_type').change(actionChangeListner)
	loadMenu()
	/*
	//debug menu
	menu = {
		a:{b:{Save:'d',
			  Save:'f'},
		   g:{Save:'i',
			  Save:'k'}},
	    l:{Save:'m'},
	    n:{Save:'p'}};
	*/
});
var menu;
var path = [];
var extra = [];
function actionChangeListner(){
	var type = $('#action_type').val();
	if(type=='set_status'){
		newSelector = $('<select id="lvl0-select"></select>');
		newSelector.append(
                $('<option></option>')
                       .val('select something')
                       .html('select something'));
		$.each(menu, function(i,obj){
			//alert(i+":"+obj)
			if(i!='Note'){
				newSelector.append(
		                 $('<option></option>')
		                        .val(i)
		                        .html(i));
			}

		});
		newSelector.data('lvl',0);
		newSelector.select('select something');
		newSelector.change(function(evt){
			pathChangeListener($('#'+evt.target.id).data('lvl'),
					evt.target.value);
		});
		
		$('#secondary').children().remove();
		lvl0 = $('<tr id="lvl0"></tr>');
		pathLabel = $('<td></td>').html('path:');
		lvl0.append(pathLabel);
		pathLabel = $('<td></td>').html('[');
		lvl0.append(pathLabel);
		pathSelect = $('<td></td>').append(newSelector);
		lvl0.append(pathSelect);
		endbracket = $('<span id="endbracket">]</span>');
		endbracket.data('lvl',0);
		lvl0.append(endbracket);
		$('#secondary').append(lvl0);
		
	} else {
		$('#secondary').children().remove();
		$('#tertiary').children().remove();
		path = [];
		extra = []
		

	}
}
function pathChangeListener(lvl,val){
	//remove subsequent options

	for(var x=lvl+1;x<=path.length;x++){
		$('#lvl'+x).remove();
		$('#lvl'+x+'extra').remove();
		if(extra[x]){
			extra[x].is=false;
		}
		
	}
	path.splice(lvl);
	path = path.concat([val]);
	m = getSubMenu(path);
	if(m['extra']){
		addExtra(m['extra'],lvl);
	}
	if(m['Save']){
		//last level, dont display selector with 'save'
		//endbracket may need to be moved up
		$('#endbracket').remove();
		endbracket = $('<span id="endbracket">]</span>');
		lvlDom = $('#lvl'+lvl);
		$('#lvl'+lvl+'comma').remove();
		
		lvlDom.append(endbracket);
		if(extra[lvl]){
			$('#endbracket').html('],');
		}
		
		return;
	}
	newSelector = $('<select id="lvl'+lvl+1+'-select"></select>');
	newSelector.append(
            $('<option></option>')
                   .val('select something')
                   .html('select something'));
	$.each(m, function(i,obj){
		//alert(i+":"+obj)
		if(i!='Note'){
			newSelector.append(
	                 $('<option></option>')
	                        .val(i)
	                        .html(i));
		}

	});
	newSelector.data('lvl',lvl+1);
	newSelector.select('select something');
	newSelector.change(function(evt){
		pathChangeListener($('#'+evt.target.id).data('lvl'),
				evt.target.value);
	});
	var nextLvl = lvl+1;
	var lvlDom = $('<tr id="lvl'+nextLvl+'"></tr>');
	//no label for non lvl0 levels
	pathLabel = $('<td></td>');
	lvlDom.append(pathLabel);
	//no bracket either
	pathLabel = $('<td></td>');
	lvlDom.append(pathLabel);
	
	//but there is a new selector
	pathSelect = $('<td></td>').append(newSelector);
	
	lvlDom.append(pathSelect);
	//change bracket to a comma
	oldBracket = $('#endbracket');
	oldLvl = oldBracket.data('lvl');
	oldBracket.html(',');
	oldBracket.attr('id','lvl'+oldLvl+'comma');
	//move end bracket down
	endbracket = $('<span id="endbracket">]</span>');
	endbracket.data('lvl',nextLvl);
	lvlDom.append(endbracket);
	$('#secondary').append(lvlDom);
	
}
function addExtra(mextra,lvl){
	extra[lvl]= {};
	extra[lvl].is=true;
	$('#endbracket').html('],');
	$('#tertiary').children().remove();
	
	var extraDom = $('<tr id="lvl'+lvl+'extra"></tr>');
	extraLabel = $('<td></td>').html('extra:{');
	extraDom.append(extraLabel);
	for(e in mextra){
		emptyLabel = $('<td></td>');
		extraDom.append(emptyLabel);
		extraLabel = $('<td></td>').html(e+':');
		extraDom.append(extraLabel);
	
		text = $('<input type="text" id="extraText"></input>');
		extraText = $('<td></td>').append(text);
		extra[lvl].name = e;
		extraText.change(function(lvl){
				return function(evt){
					extra[lvl].value = $('#'+evt.target.id).val();
				}
			
		}(lvl));
		extraDom.append(extraText);
		
		
	}
	extraLabel = $('<td></td>').html('}');
	extraDom.append(extraLabel);
	$('#tertiary').append(extraDom);
}
function getSubMenu(path){
	ret = menu;
	for (x in path){
		ret = ret[path[x]];
	}
	return ret;
}

function loadMenu(){
	/*
	 * you don't actually need a username/password if the
	 * backend server has already built the menu
	 */ 
	$('#loading').addClass('showLoader');
	$('#loading').removeClass('hideLoader');
	data ={'type':'get_menu'}
	$.post('/handler.html',JSON.stringify(data),function(data){
		$('#loading').addClass('hideLoader');
		$('#loading').removeClass('showLoader');
		menu = JSON.parse(data);
	})
	.fail(function(){
		$('#loading').addClass('hideLoader');
		$('#loading').removeClass('showLoader');
		
	});
}

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
	data['type']=$('#action_type').val();
	if(path.length>0){
		data['path']=path;
	}
	var extra_data = {};
	var has_extra = false;
	for(e in extra){
		if(extra[e].is){
			has_extra = true;
			extra_data[extra[e].name]=extra[e].value;
		}
	}
	if(has_extra){
		data['extra']=extra_data
	}
	//show data, hide password
	input_data = JSON.parse(JSON.stringify(data));
	if (input_data.password){
		input_data.password = '***********';
	}
	input_data = JSON.stringify(input_data, undefined, 4);
	$('#input').children().remove();
	var json_stuff = $('<pre>');
	var out = syntaxHighlight(input_data);
	json_stuff[0].innerHTML = out;
	$('#input').append(json_stuff);
	
	$('#loading').addClass('showLoader');
	$('#loading').removeClass('hideLoader');
	
	$.post('/handler.html',
			JSON.stringify(data),
			function(data){
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


