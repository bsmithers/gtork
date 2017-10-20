function is_logged_in(){
    var settings = ['garmin_user', 'garmin_pass', 'runkeeper_access', 'runkeeper_name'];
    return settings.every(function(s){
       return localStorage.getItem(s) !== null;
    });
}

function clear_credentials(){
    localStorage.clear();
    var redirect_to = SCRIPT_ROOT + '/';
    window.location.replace(redirect_to);
}

function get_garmin_user(){
    return localStorage.getItem('garmin_user')
}

function get_garmin_pass(){
    return localStorage.getItem('garmin_pass')
}

function get_real_name(){
    return localStorage.getItem('runkeeper_name');
}

function get_runkeeper_access(){
    return localStorage.getItem('runkeeper_access');
}

function save_login(username, password){
    localStorage.setItem('garmin_user', username);
    localStorage.setItem('garmin_pass', password);
}

function save_runkeeper(access_token, name){
    localStorage.setItem('runkeeper_access', access_token);
    localStorage.setItem('runkeeper_name', name);
}

function is_https_or_localhost(){
    if (location.protocol === 'https:'){
        return true;
    }
    if (location.hostname === "localhost" || location.hostname === "127.0.0.1"){
        return true;
    }
    return false;
}

