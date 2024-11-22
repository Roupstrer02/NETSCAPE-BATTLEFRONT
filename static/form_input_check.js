
// denies form submission if instructions are either useless or impossible to run
    




$(document).ready(function() {
    console.log("js is loaded!")

    $("#InvalidFormAlert").hide();

    $("form").submit( function(e) {

        let raw_form_data = new FormData(document.getElementById("controller"));
        let form_data = {};

        for (const [key, value] of raw_form_data) {
            form_data[key] = value
        }

        console.log(form_data["unit_spawn"])
        console.log(form_data["unit_destination"])

        //units must be sent from one control point to another, not to themselves 
        if (form_data["unit_spawn"] == form_data["unit_destination"]) {
            $("#InvalidFormAlert").show();
            $("#InvalidFormMessage").show()
            return false;
        }

        return true;
    
    });
});

