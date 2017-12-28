$(document).ready(function () {
    counter = 0;
    initial_reload();
});
var formData = {},
    user_id;
function initial_reload() {
    counter++;
    var access_token = $('#access_token').val();
    console.log(access_token)
    if (access_token == undefined || access_token == null || access_token == '') {
//        initPage();
        return;
    }
    else {
        set_access_token(access_token);
        console.log("asdsassdsad")
        window.location = BASE_URL + 'book/user/recommendations/';
    }
}

function updaterating()
{
console.log("dadadadadadad");
formData = {};
    formData.book_rating = $("#your_rating").val();
    formData.book_title = $("#book_titler").val();

var ajax_data = {
            'url': BASE_URL + 'book/updateRating/',
            'data': formData,
            'request_type': 'POST',
            'extra_fields': {
                dataType: 'json'
            }
        };
        call_ajax(ajax_data, function (err, response) {
            //$.unblockUI();
            if (!err) {
                alert("successfully updated rating");
//                $('#view-user').modal('hide');
                location.reload(true);
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
