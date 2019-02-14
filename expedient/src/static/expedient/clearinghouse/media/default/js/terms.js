var change_event_prevent_hack = false;
var validyOfAcceptanceInDays = 180;

function set_loading(is_loading) {
//    console.log("set_loading("+is_loading+")");
    if (document.getElementById("userurn") != undefined ) {
        if (is_loading) {
            document.getElementById("userurn").innerHTML = "loading...";
        } else {
            document.getElementById("userurn").innerHTML = "{{ user_urn }}";
        }
    }

    if (document.getElementById("testbed-access-denied") != undefined ) {
        document.getElementById("testbed-access-denied").hidden = true;
    }
    if (document.getElementById("testbed-access-allowed") != undefined ) {
        document.getElementById("testbed-access-allowed").hidden = true;
    }

    var loadedonce = document.getElementsByClassName("loadedonce");
    for(var i = 0; i < loadedonce.length; i++) {
        if (is_loading) {
           loadedonce.item(i).hidden = false;
       }
    }

    var loaded = document.getElementsByClassName("loaded");
    for(var i = 0; i < loaded.length; i++) {
       loaded.item(i).hidden = is_loading;
    }

    var loading = document.getElementsByClassName("loading");
    for(var i = 0; i < loading.length; i++) {
       loading.item(i).hidden = !is_loading;
    }
}

function load_info() {
    //console.log("load_info()");
    set_loading(true);
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        set_loading(false);
        //console.log("load_info onload status=" + this.status);
        if (this.status == 200) {
            //console.log("load_info onload SUCCESS xhttp.responseText=" + xhttp.responseText);
            var accepts = JSON.parse(xhttp.responseText);
            //console.log("load_info onload SUCCESS accepts=" + accepts);

            // Filled in by the backend
            //document.getElementById("userurn").innerHTML = accepts.user_urn;

            if (document.getElementById("testbed-access-denied") != undefined ) {
                document.getElementById("testbed-access-denied").hidden = accepts.testbed_access;
            }
            if (document.getElementById("testbed-access-allowed") != undefined ) {
                document.getElementById("testbed-access-allowed").hidden = !accepts.testbed_access;
            }

            // Hide buttons when terms are accepted
            /*
            if (document.getElementById("terms-accept") != undefined ) {
                document.getElementById("terms-accept").hidden = accepts.testbed_access;
            }
            if (document.getElementById("terms-decline") != undefined ) {
                document.getElementById("terms-decline").hidden = accepts.testbed_access;
            }
            */

            // Filled in by the backend
            // document.getElementById("until-date").innerHTML = accepts.until;

            //let jFed know
            if (window.jfed && window.jfed.approveWithDateISO8601 && window.jfed.decline) {
                if (accepts.testbed_access) {
                    window.jfed.approveWithDateISO8601(accepts.until);
                } else {
                    window.jfed.decline();
                }
            }
        } else {
            console.log("load_info onload FAILURE status=" + this.status);
        }
    };
    xhttp.open("GET", "/privacy/{{ user_urn }}", true);
    xhttp.send();
}

function on_accept_decline_action(user_urn, accepts) {
    if (change_event_prevent_hack) { return; }
    set_loading(true);
    accepts ? send_accept_terms(user_urn) : send_decline_terms(user_urn);
}

function send_accept_terms(user_urn) {
    //console.log("send_accept_terms()");
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        console.log("accept_terms onload status=" + this.status);
        if (this.status == 204) {
            //console.log("accept_terms onload SUCCESS status=" + this.status);
            if (window.jfed) {
                console.log("accept_terms onload approveDaysFromNow=" + validyOfAcceptanceInDays);
                window.jfed.approveDaysFromNow(validyOfAcceptanceInDays);
            }
            close_window();
        } else {
            console.log("accept_terms onload FAILURE status=" + this.status);
        }
    };
    xhttp.open("GET", "/privacy/" + user_urn + "/accept/", true);
    xhttp.send();
}

function send_decline_terms(user_urn) {
    //console.log("send_accept_terms()");
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        //console.log("decline_terms onload status=" + this.status);
        if (this.status == 204) {
            //console.log("decline_terms onload SUCCESS status=" + this.status);
            if (window.jfed) {
                window.jfed.decline();
            }
            close_window();
        } else {
            console.log("decline_terms onload FAILURE status=" + this.status);
        }
    };
    xhttp.open("GET", "/privacy/" + user_urn + "/decline/", true);
    xhttp.send();
}

function close_window() {
    //console.log("close_window -> window.jfed=" + window.jfed);
    if (window.jfed && window.jfed.close) {
        window.jfed.close();
    }
}

function initJFed() {
    if (window.jfed && window.jfed.decline) {
        //let jFed know the users hasn't accepted the Terms and Conditions yet.
        window.jfed.decline();
    }
}

window.onload = function() {
    if (window.jfed) {
      initJFed();
    } else {
      // window.jfed is not (yet) available
      // trick to make browser call  initJFed() when window.jfed becomes available.
      Object.defineProperty(window, 'jfed', {
        configurable: true,
        enumerable: true,
        writeable: true,
        get: function() {
          return this._jfed;
        },
        set: function(val) {
          this._jfed = val;
          initJFed();
        }
      });
      if (window.jfed) {
        initJFed();
      }

    }

    load_info();
}