$(document).ready(function() {
    if (!is_https_or_localhost()){
        $('#container').html('<div class="alsert alert-danger" role="alert">Cowardly refusing to proceed since this is not a secure connection!</div>');
    }

    $( "#garmin-form" ).submit(function(event) {
        event.preventDefault();
        save_login($("#garmin-email").val(), $("#garmin-password").val());
        $("#garmin-form-container").slideUp();
        $("#runkeeper-form-container").slideDown();
    });

    $("#runkeeper-form").submit(function(event){
        event.preventDefault();

        var here = window.location['href'];
        url = "https://runkeeper.com/apps/authorize?client_id=" + RUNKEEPER_CLIENT_ID + "&response_type=code&redirect_uri=" + here;
        window.location.href = url;
    });

});