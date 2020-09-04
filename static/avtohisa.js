'use strict'

function odpri_okno() {
    var e = document.getElementById("izberi_starost");
    var select_value = e.options[e.selectedIndex].value;
    if(select_value == "false"){
        document.getElementById("hidden_div").style.display = "inherit";
        //document.getElementById("st_kilometrov").required = true;
    }else{
         document.getElementById("st_kilometrov").value = '';
         var ima_servis = document.getElementsByName("servis");
         for (var i = 0, length = ima_servis.length; i < length; i++) {
            if (ima_servis[i].checked) {
                ima_servis[i].checked = false
                break;

            }
        }
         document.getElementsByName("servis").value = '';
    }

}
function zapri_okno(){
        document.getElementById("hidden_div").style.display = "none";
        var st_kilometrov = document.getElementById("st_kilometrov");
        var ima_servis = document.getElementsByName("servis");
        var status_servisa = null;
        for (var i = 0, length = ima_servis.length; i < length; i++) {
            if (ima_servis[i].checked) {
                status_servisa = ima_servis[i].value;
                break;

            }
        }

        if(!st_kilometrov.value || !status_servisa){
            document.getElementById("Nov").selected = true;
            document.getElementById("napaka_za_rabljen").style.display = "inherit";


        }else{
            document.getElementById("napaka_za_rabljen").style.display = "none";

        }

}

function odpri_okno_brisi(element) {
    let id  = element.dataset.id;
    document.getElementById("hidden_div1"+id).style.display = "inherit";
}
function zapri_okno_brisi(element) {
    let id  = element.dataset.id;
    document.getElementById("hidden_div1"+id).style.display = "none";
}

var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //January is 0!
var yyyy = today.getFullYear();
 if(dd<10){
        dd='0'+dd
    } 
    if(mm<10){
        mm='0'+mm
    } 
today = ""+ yyyy+'-'+mm+'-'+dd + "";
console.log(document.getElementById("datum"))
document.getElementById("datum").max =  today;


// function odpri_okno_brisi() {
//     document.getElementById("hidden_div1").style.display = "inherit";
// }

// function zapri_okno_brisi(e) {
//     document.getElementById("hidden_div1").style.display = "none";
// }