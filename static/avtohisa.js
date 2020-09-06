'use strict'

// odpri okno ko zamnjas iz nov na rabljen
function odpri_okno() {
    var e = document.getElementById("izberi_starost");
    var select_value = e.options[e.selectedIndex].value;
    
    // ce je izbran nov avto, je okno skrito
    if(select_value == "false"){
        document.getElementById("hidden_div").style.display = "inherit";

    }else{
        document.getElementById("st_kilometrov").value = '';
        // preverimo ali so vneseni vsi podatki 
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

function odpri_okno1() {
    var e = document.getElementById("izberi_starost");
    var select_value = e.options[e.selectedIndex].value;
    
    // ce je izbran nov avto, je okno skrito
    if(select_value == "false"){
        document.getElementById("hidden_div").style.display = "inherit";

    }else{
        document.getElementById("st_kilometrov").value = '';
        // preverimo ali so vneseni vsi podatki 
        // var ima_servis = document.getElementsByName("servis");
        // for (var i = 0, length = ima_servis.length; i < length; i++) {
        //     if (ima_servis[i].checked) {
        //         ima_servis[i].checked = false
        //         break;

        //     }
        // }
        document.getElementsByName("servis").value = '';
    }

}


function zapri_okno1(){
        document.getElementById("hidden_div").style.display = "none";
        // dobimo vem kaj pise v okncku stevilo kilometrov in ali ima servis
        var st_kilometrov = document.getElementById("st_kilometrov");
        var ima_servis = document.getElementsByName("servis");

        // status servisa je na zacetku null
        var status_servisa = null;

        // ima servis ima vrednost 0 ali 1
        // for (var i = 0, length = ima_servis.length; i < length; i++) {
        //     if (ima_servis[i].checked) {
        //         status_servisa = ima_servis[i].value;
        //         break;

        //     }
        // }

        // ce ni podatka o stevilu kilometrov ali o servisu (se vedno null), se izbira spremeni nazaj na nov, in izpise se napaka
        // if(!st_kilometrov.value || !status_servisa){
        //     document.getElementById("Nov").selected = true;
        //     document.getElementById("napaka_za_rabljen").style.display = "inherit";

        if(!st_kilometrov.value){
            document.getElementById("Nov").selected = true;
            document.getElementById("napaka_za_rabljen").style.display = "inherit";


        }else{
            document.getElementById("napaka_za_rabljen").style.display = "none";

        }

}

// odpri in zapri okno za pojavno okno o brisanju iz baze (prodaja avtomobila, odstrani zaposlenega, iz priljubljrnih)
function odpri_okno_brisi(element) {
    let id  = element.dataset.id;
    document.getElementById("hidden_div1"+id).style.display = "inherit";
}
function zapri_okno_brisi(element) {
    let id  = element.dataset.id;
    document.getElementById("hidden_div1"+id).style.display = "none";
}

// da dobim današnji datum pri omejevanju izbiranja datuma servisa, priprave, prodaje
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //januar je 0
var yyyy = today.getFullYear();
 if(dd<10){
        dd='0'+dd
    } 
    if(mm<10){
        mm='0'+mm
    } 
today = ""+ yyyy+'-'+mm+'-'+dd + "";
if(document.getElementById("datum")){
    document.getElementById("datum").max = today;
}
if(document.getElementById("datum_zadnjega_servisa")){
    document.getElementById("datum_zadnjega_servisa").max = today;
}


