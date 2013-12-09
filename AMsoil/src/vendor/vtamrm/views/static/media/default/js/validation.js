var DATAPATH_RE = /^([0-9a-fA-F]{2}[:-]){7}([0-9a-fA-F]{2})$/;
var MAC_RE = /^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$/;
var NOTBLANK_RE = /^.+$/;
var NUMBER_RE = /^([0-9])+$/;
var RESOURCE_RE = /^([0-9a-zA-Z\-\_\ \.])+$/;
//var RESOURCE_RE = /^([0-9a-zA-Z\-\_])+$/;
var RESOURCE_RESTRICTED_RE = /^([0-9a-zA-Z\-]){1,64}$/;

/* Error list check and generation */
function doErrorlistExists(fieldID) {
    var result = false;
    if ($("#errorlist_" + fieldID).length > 0) {
        result = true;
    }
    return result;
}

function prependErrorlist(fieldID, errorMessage) {
    $("#" + fieldID).parent().prepend("<ul id=\"errorlist_" + fieldID + "\" class=\"error\"><li>" + errorMessage + "</li></ul>");
}

function removeErrorlist(fieldID) {
    $("#errorlist_" + fieldID).remove();
}

/* REGEX wrapper */
function checkWithRegExp(fieldID, regExp, errorMessage) {
    var result = false;
    var reCorrectFormat = new RegExp(regExp);
    var field = $("#" + fieldID);
    if (!reCorrectFormat.test(field.val())) {
        if (!doErrorlistExists(field.attr("id"))) {
            prependErrorlist(field.attr("id"), errorMessage);
        }
    } else {
        if (doErrorlistExists(field.attr("id"))) {
            removeErrorlist(field.attr("id"));
        }
        result = true;
    }
    return result;
}

/* Generic validation */
function checkDatapathID(id, resourceName) {
    return checkWithRegExp(id, DATAPATH_RE, "Check that the " + resourceName + " is properly formed.");
}

function checkNotBlank(id, resourceName) {
    return checkWithRegExp(id, NOTBLANK_RE, "Check that the " + resourceName + " is not empty.");
}

function checkNumber(id, resourceName) {
    return checkWithRegExp(id, NUMBER_RE, "Check that the " + resourceName + " consists only of numbers.");
}

function checkPort(id, resourceName) {
    return checkWithRegExp(id, NUMBER_RE, "Check that the " + resourceName + " is correct.");
}

function checkRestrictedName(id, resourceName) {
    return checkWithRegExp(id, RESOURCE_RESTRICTED_RE, "Check that the " + resourceName + " has ASCII characters only and no whitespaces.");
}

function checkName(id, resourceName) {
    return checkWithRegExp(id, RESOURCE_RE, "Check that the " + resourceName + " has ASCII characters only.");
}

function checkMAC(id, resourceName) {
    return checkWithRegExp(id, MAC_RE, "Check that the " + resourceName + " is properly formed.");
}

function checkAllResultsOK(results) {
    var result = true;
    $.each(results, function(index, value) { result = result && value; });
    return result;
}

function checkDropDownSelected(fieldID) {
    var result = false;
    var field = $("#" + fieldID);
    if ($("#" + fieldID)[0].selectedIndex <= 0) {
        if (!doErrorlistExists(field.attr("id"))) {
            prependErrorlist(field.attr("id"), "Please select one option.");
        }
    } else {
        if (doErrorlistExists(field.attr("id"))) {
            removeErrorlist(field.attr("id"));
        }
        result = true;
    }
    return result;
}

/* Automated validation */
function contains(substring, string) {
    return (string != undefined && substring != undefined && string.toLowerCase().indexOf(substring.toLowerCase()) > -1);
}

function isBlank(id) {
    var reCorrectFormat = new RegExp(NOTBLANK_RE);
    return !reCorrectFormat.test($("#" + id).val());
}

function replaceID(id, oldWord, newWord) {
    return id.replace(new RegExp(oldWord,"g"), newWord);
}

/* Bind validation check to the submit button */
$(":submit[id^=form_create_server]").click(function() {
    // First, submit ID
    var submitID = $(this).attr("id") || "";
    if (contains("form_create_", submitID)) {
        submitID = submitID.split('form_create_').slice(1).join('')
    }

    // Second, all other input IDs
    var id = "";
    var type = "";
    var results = Array();
    $("form table input, form table select, form table textarea").each(function(index) {
        id = $(this).attr("id") || "";
        // Correct by default (ignores fields non stated in the if/else block
        results[index] = true;
        if ($(this).is("input")) {
            // VM names have a special treatment
            if (contains("name",id) && (contains("server", id) || contains("bridge", id))) {
                results[index] = checkName(id,submitID + " name");
            } else if (contains("name",id)) {
                results[index] = ((isBlank(id) && isBlank(replaceID(id, "name", "port")) && isBlank(replaceID(id, "name", "switchID"))) || checkName(id,submitID + " name"));
            } else if (contains("url",id)) {
                results[index] = checkNotBlank(id,submitID + " agent URL");
            } else if (contains("-mac",id)) {
                results[index] = (isBlank(id) || checkMAC(id,submitID + " mac"));
            } else if (contains("switchID",id)) {
                results[index] = ((isBlank(id) && isBlank(replaceID(id, "switchID", "name")) && isBlank(replaceID(id, "switchID", "port"))) || checkDatapathID(id,submitID + " switch"));
            } else if (contains("port",id)) {
                results[index] = ((isBlank(id) && isBlank(replaceID(id, "port", "name")) && isBlank(replaceID(id, "port", "switchID"))) || checkPort(id,submitID + " port"));
            }
        } else if ($(this).is("select")) {
            results[index] = checkDropDownSelected(id);
        }
    });
    return checkAllResultsOK(results);
});
