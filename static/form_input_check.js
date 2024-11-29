
// denies form submission if instructions are either useless or impossible to run
    
$(document).ready(function() {
    console.log("js is loaded!")

    $("#InvalidFormAlert").hide();

    $("form").submit( function(e) {

        let raw_form_data = new FormData(document.getElementById("controller"));
        let form_data = {};

        let invader_cPoints;

        fetch("file:\\\C:\Users\Roups\Documents\VSCodeProjects\PythonProjects\ArmRoup-PyGame\invader_control_points.txt")
        .then((res) => res.text())
        .then((text) => {
          invader_cPoints = text
         })
        .catch((e) => console.error(e));

        for (const [key, value] of raw_form_data) {
            form_data[key] = value
        }

        console.log(form_data["unit_spawn"])
        console.log(form_data["unit_destination"])
        console.log(invader_cPoints)

        //units must be sent from one control point to another, not to themselves 
        if (form_data["unit_spawn"] == form_data["unit_destination"]) {
            $("#InvalidFormAlert").show();
            $("#InvalidFormMessage").show();
            $("#InvalidFormMessage2").hide();
            return false;
        }
        else if (invader_cPoints.includes(form_data["unit_spawn"])) {
            $("#InvalidFormAlert").show();
            $("#InvalidFormMessage").hide();
            $("#InvalidFormMessage2").show();
            return false;  
        }


        return true;
    
    });
});

