/*global AssetManager _config*/
var AssetManager = window.AssetManager || {};
(function AssetManagerScopeWrapper($) {
    var authToken;
    AssetManager.authToken.then(function setAuthToken(token) {
        if (token) {
            authToken = token;
        } else {
            window.location.href = './signin.html';
        }
    }).catch(function handleTokenError(error) {
        alert(error);
        window.location.href = './signin.html';
    });

    $(function onDocReady() {


        AssetManager.authToken.then(function displayToken(token) {
            if (token) {
                $('#token-area').val(token);
            }
        });
    });


}(jQuery));
