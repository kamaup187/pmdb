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


function spinOn(){
    $("#result-view").addClass("smooth spinner");
    // $("#dummyData").addClass("spinner-opacity-extreme");
}

function spinOff(){
    $("#result-view").removeClass("smooth spinner");
    // $("#dummyData").removeClass("spinner-opacity-extreme");
}

function spinOnChild(){
    $("#child-view").addClass("smooth spinner");
    // $("#dummyData").addClass("spinner-opacity-extreme");
}

function spinOffChild(){
    $("#child-view").removeClass("smooth spinner");
    // $("#dummyData").removeClass("spinner-opacity-extreme");
}

function spinOnChildView(){
    $("#child-result-view").addClass("smooth spinner");
    // $("#dummyData").addClass("spinner-opacity-extreme");
}

function spinOffChildView(){
    $("#child-result-view").removeClass("smooth spinner");
    // $("#dummyData").removeClass("spinner-opacity-extreme");
}