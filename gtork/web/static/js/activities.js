function format_distance(distance){
    distance = distance / 1000
    return distance.toFixed(2) + ' km'
}

//https://stackoverflow.com/a/24333274
function dayOfWeekAsString(dayIndex) {
  return ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][dayIndex];
}

function date_only(d){
    return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

function is_same_day(d1, d2){
    var d1 = date_only(d1);
    var d2 = date_only(d2);
    return d1.getTime() - d2.getTime() === 0;
}

function is_yesteday(d1, d2){
    var d1 = date_only(d1);
    var d2 = date_only(d2);
    return d1.getTime() - d2.getTime() === 1000 * 60 * 60 * 24;
}

function pad(n, width, z) {
    //https://stackoverflow.com/a/1007378
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function format_datetime(datetime){
    var d = new Date(datetime);
    var now = new Date();
    var day = d.toDateString();
    if (is_same_day(d, now)) {
        day = "Today"
    }else if(is_yesteday(now, d)){
        day = "Yesterday"
    }
    return day + " at " + pad(d.getHours(), 2) + ":" + pad(d.getMinutes(), 2)
}

function upload(span, index){
    $(span).html('<span>Uploading activity...</span>');
    var activity = activity_data[index];
    console.log("Uploading activity: " + activity['activityId']);

    var post_data = {
        id: activity['activityId'],
        name: activity['activityName'],
        description: activity['description'],
        type: activity['activityType']['typeKey'],
        local_start_time: activity['startTimeLocal'],
        access_token: get_runkeeper_access()
    };

    $.post(SCRIPT_ROOT+"/upload", post_data, function(data) {
        $("#status").html('<div class="alert alert-success" role="alert"> <strong>Done!</strong> Activity uploaded successfully. </div>')
        $(span).html('<span>Uploaded</span>');
    }).fail(function(data){
        var reason = "There was an error. That's all we know.";
        try{
            var response = JSON.parse(data.responseText);
            reason = response['error'];
        } catch(e){
            console.log("malformed response");
        }

        $("#status").html('<div class="alert alert-danger" role="alert"> <strong>Oops!</strong> Couldn\'t upload that activity right now. ' + reason + '</div>');
        $(span).html('<span>Upload Failed</span>');
    });

}

$(document).ready(function() {

    if(!is_logged_in()){
        var url = SCRIPT_ROOT + '/auth';
        window.location.replace(url);
        return;
    }

    $('#garmin-name').html(get_garmin_user());
    $('#runkeeper-name').html(get_real_name());

    console.log("Loading activities");
    $.get(MUSTACHE_ROOT + '/activity.html', function(data){
        MUSTACHE_TEMPLATES['activity'] = data ;
    });
    $.get(SCRIPT_ROOT + "/activities", { user: get_garmin_user(), pass: get_garmin_pass()}, function(data) {
        try {
            $("#status").html('');
            activity_data = data;

            var list_container = $("#list-container");
            list_container.empty();
            activity_data.forEach(function (activity, i) {
                var h =  Mustache.render(MUSTACHE_TEMPLATES['activity'], {
                            index: i,
                            name: activity["activityName"],
                            description: activity["description"],
                            distance: format_distance(activity["distance"]),
                            time: format_datetime(activity["startTimeLocal"])
                        });
                list_container.append(h)
            });
        }catch(e){
            console.log(e);
            $("#status").html('<div class="alert alert-danger" role="alert"> <strong>Oops!</strong> The data we got back doesn\'t look good. </div>');
        }
    })
    .fail(function(data) {
        $("#status").html('<div class="alert alert-danger" role="alert"> <strong>Oops!</strong> Couldn\'t load your activities right now. </div>');
        var reason = "Couldn\'t load your activities right now. ";
        try{
            var response = JSON.parse(data.responseText);
            reason += response['error'];
        } catch(e) {
            console.log("error not given");
        }
        $("#status").html('<div class="alert alert-danger" role="alert"> <strong>Oops!</strong> ' + reason + ' </div>');
    });
});