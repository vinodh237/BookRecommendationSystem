function set_access_token(access_token) {
    set_cookie('appAccessToken', access_token, 20 * 365);
}

function set_csrf_token(csrf_token) {
    set_cookie('csrftoken', csrf_token, 20 * 365);
}

function clear_access_token() {
    set_cookie('appAccessToken', '', 0);
}

function clear_csrftoken_token() {
    set_cookie('csrftoken', '', 0);
}

function call_ajax(params, callback) {
    var ajax_obj = {
        type: params['request_type'],
        url: params['url'],
        beforeSend: function (xhr, settings) {
            $.blockUI({message: '<h1><img src="' + S3_URL + '/img/loader.gif" /> Just a moment...</h1>'});
            var access_token = get_cookie('appAccessToken');
            if (access_token != '') {
                xhr.setRequestHeader('Authorization', 'Bearer ' + access_token);
            }
            var csrf_token = get_cookie('csrftoken');
            if (csrf_token != '') {
                xhr.setRequestHeader('X-CSRFToken', csrf_token);
            }
        },

        data: params['data'],
        complete: function (response) {
            $.unblockUI();
        },
        success: function (response) {
            callback(0, response);
        },
        error: function (response) {
            if (response.status == 401 || response.status == 403) {
                clear_access_token();
                clear_csrftoken_token();
                window.location = BASE_URL + 'admin/';
            }
            callback(1, response);
        }
    };

    for (var i in params['extra_fields']) {
        ajax_obj[i] = params['extra_fields'][i];
    }
    $.ajax(ajax_obj);
}

function get_cookie(c_name) {
    if (document.cookie.length > 0) {
        var c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1) {
            c_start = c_start + c_name.length + 1;
            var c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1)
                c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start, c_end));
        }
    }
    return "";
}

function set_cookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
}

//$(document).ready(function(){
//   $('#logout').click(function(e){
//        handleLogout(e)
//    });
//});


function handleLogout(e) {
    e.preventDefault();
    var ajax_data = {
        'url': BASE_URL + 'admin/logout/',
        'data': "",
        'request_type': 'POST',
        'extra_fields': {
            dataType: 'json'
        }
    };
    call_ajax(ajax_data, function (err, response) {
        //$.unblockUI();
        if (!err) {
            window.location = BASE_URL + 'admin/';
        } else {
            response = $.parseJSON(response['responseText']);
            if (typeof(response['detail']) !== 'undefined') {
                alert(response['detail']);
            } else {
                alert('Some error occurred.');
            }
        }
    });
}