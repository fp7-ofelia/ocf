var NUMBER_RE = /^([0-9])+$/;
var RESOURCE_RE = /^([0-9a-zA-Z\-\_])+$/;
var TEXT_RE = /^([0-9a-zA-Z\-\_\ \.])+$/;

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

function checkWithRegExp(fieldID, regExp, errorMessage) {
    var result = false;
    reCorrectFormat = new RegExp(regExp);
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

function checkProjectName() {
    return checkWithRegExp("id_name", TEXT_RE, "Check that the project name has ASCII characters only.");
}

function checkProjectDescription() {
    return checkWithRegExp("id_description", TEXT_RE, "Check that the project description has ASCII characters only.");
}

function checkVirtualMachineName() {
    return checkWithRegExp("id_form-0-name", RESOURCE_RE, "Check that the VM has ASCII characters only and no whitespaces.");
}

function checkVirtualMachineMemory() {
    return checkWithRegExp("id_form-0-memory", NUMBER_RE, "Check that the VM size consists only of numbers.");
}

function checkDropDownSelected(fieldID) {
    var result = false;
    var field = $("#" + fieldID);
    if ($("#" + fieldID).attr("selectedIndex") <= 0) {
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

function checkAllResultsOK(results) {
    var result = true;
    $.each(results, function(index, value) { result = result && value; });
    return result;
}

function checkProjectInfo() {
    var results = Array();
    results[0] = checkProjectName();
    results[1] = checkProjectDescription();
    return checkAllResultsOK(results);
}

function checkVirtualMachineInfo() {
    var results = Array();
    results[0] = checkVirtualMachineName();
    results[1] = checkVirtualMachineMemory();
    results[2] = checkDropDownSelected("id_form-0-disc_image");
    results[3] = checkDropDownSelected("id_form-0-hdSetupType");
    results[4] = checkDropDownSelected("id_form-0-virtualizationSetupType");
    return checkAllResultsOK(results);
}
