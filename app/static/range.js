function range(start, stop, step){
    var a = [start], b = start;
    while (b < stop) {
        a.push(b += step || 1);
    }
    return a;
}

function showSpin(){
    $("#reqdata").addClass("smooth spinner");
    $("#tenantData").addClass("spinner-opacity");
}

function removeSpin(){
    $("#reqdata").removeClass("smooth spinner");
    $("#tenantData").removeClass("spinner-opacity");
}