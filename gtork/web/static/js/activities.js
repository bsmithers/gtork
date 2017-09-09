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

function format_datetime(datetime){
    var d = new Date(datetime);
    var now = new Date();
    var day = d.toDateString()
    if (is_same_day(d, now)) {
        day = "Today"
    }else if(is_yesteday(now, d)){
        day = "Yesterday"
    }
    return day + " at " + d.getHours() + ":" + d.getMinutes()
}

function upload(span, activity_id){
    $(span).html('<span>Uploading activitiy...</span>');
    console.log(activity_id);
    var post_data = {"id" : activity_id};
    $.post("/upload", activity_id, function(data) {
        $("#status").html('<div class="alert alert-success" role="alert"> <strong>Done!</strong> Activity uploaded successfully. </div>')
        $(span).html('<span>Uploaded</span>');
    }).fail(function(){
        $("#status").html('<div class="alert alert-danger" role="alert"> <strong>Oops!</strong> Couldn\'t upload that activity right now </div>');
        $(span).html('<span>Upload Failed</span>');
    });

}

function generate_row(activity){
    // Returns HTML for one row corresponding to one activity
    return '<div class="row row-striped activity-row">' +
            '<div class="col-lg-4 col-sm-8">' + activity["activityName"] + '</div>' +
            '<div class="col-lg-2 col-sm-4">' + format_distance(activity["distance"]) + '</div>' +
            '<div class="col-lg-3 col-sm-8">' + format_datetime(activity["startTimeLocal"]) + '</div>' +
            '<div class="col-lg-3 col-sm-4"><span class="upload_link" href="#" onclick="upload(this, ' + activity['activityId'] + ')" ><a href="#">Upload Now</a></span></div>' +
    '</div>';
}


$(document).ready(function() {
    console.log("Loading activities");
    $.get( "/activities", function(data) {
        try {
            $("#list-container").empty()
            data.forEach(function (activity) {
                $("#status").html('')
                $("#list-container").append(generate_row(activity))
            });
        }catch(e){
            console.log(e)
            $("#status").html('<div class="alert alert-danger" role="alert"> <strong>Oops!</strong> The data we got back doesn\'t look good. </div>');
        }
    })
    .fail(function() {
        $("#status").html('<div class="alert alert-danger" role="alert"> <strong>Oops!</strong> Couldn\'t load your activities right now. </div>')
    });
});