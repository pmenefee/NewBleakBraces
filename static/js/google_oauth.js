// Replace with your actual Client ID and Redirect URI
var YOUR_CLIENT_ID = '93771216567-26akanan6n84338vph006jt45gl11h55.apps.googleusercontent.com';
var YOUR_REDIRECT_URI = 'https://0ce603a4-b6ea-410e-8524-2971fa93e1cc-00-2xkptk9hodfh2.janeway.replit.dev/';

function oauth2SignIn() {
    var oauth2Endpoint = 'https://accounts.google.com/o/oauth2/v2/auth';
    var form = document.createElement('form');
    form.setAttribute('method', 'GET');
    form.setAttribute('action', oauth2Endpoint);

    var params = {
        'client_id': YOUR_CLIENT_ID,
        'redirect_uri': YOUR_REDIRECT_URI,
        'scope': 'https://www.googleapis.com/auth/youtube.force-ssl',
        'state': 'try_sample_request',
        'include_granted_scopes': 'true',
        'response_type': 'token'
    };

    for (var p in params) {
        var input = document.createElement('input');
        input.setAttribute('type', 'hidden');
        input.setAttribute('name', p);
        input.setAttribute('value', params[p]);
        form.appendChild(input);
    }

    document.body.appendChild(form);
    form.submit();
}

function parseOAuth2Token() {
    var fragmentString = location.hash.substring(1);
    var params = {};
    var regex = /([^&=]+)=([^&]*)/g, m;
    while (m = regex.exec(fragmentString)) {
        params[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
    }
    if (Object.keys(params).length > 0) {
        localStorage.setItem('oauth2-test-params', JSON.stringify(params));
    }
}

document.addEventListener("DOMContentLoaded", function() {
    parseOAuth2Token();
});
