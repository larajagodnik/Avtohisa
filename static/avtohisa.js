'use strict'

function odpri_okno() {
    var e = document.getElementById("izberi_starost");
    var select_value = e.options[e.selectedIndex].value ;
    if(select_value == "false"){
        document.getElementById("hidden_div").style.display = "inherit";
    }

}
function zapri_okno(){
    document.getElementById("hidden_div").style.display = "none";

}