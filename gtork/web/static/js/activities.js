function generate_row(activity){
    // Returns HTML for one row corresponding to one activity
    return '<div class="row row-striped activity-row">' +
            '<div class="col-sm">' + activity["activityName"] + '</div>' +
            '<div class="col-sm">' + activity["distance"] + '</div>' +
            '<div class="col-sm">' + activity["startTimeLocal"] + '</div>' +
            '<div class="col-sm"><a href="#">Upload Now</a></div>' +
    '</div>'
}


$(document).ready(function() {
    console.log("Loading activities");
    $.get( "/activities", function(data) {
        $("#list-container").empty()
        data.forEach(function(activity){
            $("#list-container").append(generate_row(activity))
        });
    })
    .fail(function() {
        console.log("Fail")
    });
});