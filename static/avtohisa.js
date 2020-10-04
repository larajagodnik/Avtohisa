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
    }

}

function zapri_okno(){
        document.getElementById("hidden_div").style.display = "none";
        // dobimo vem kaj pise v okncku stevilo kilometrov
        var st_kilometrov = document.getElementById("st_kilometrov");

        // ce ni podatka o st kilometrov, gre vrednost nazaj na nov
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

function preveriEmso(polje){
    console.log(polje.validity)
    if(polje.validity.valueMissing){
      polje.setCustomValidity('To polje je obvezno!')
    }
    else if(polje.validity.patternMismatch){
      polje.setCustomValidity('Emšo mora biti oblike DDMMLLLŠŠŠŠŠŠ!')
    }
    else{
      polje.setCustomValidity('')
    }
  }

  function preveriTelefon(polje){
    console.log(polje.validity)
    if(polje.validity.valueMissing){
      polje.setCustomValidity('To polje je obvezno!')
    }
    else if(polje.validity.patternMismatch){
      polje.setCustomValidity('Telefonska številka ni pravilne oblike!')
    }
    else{
      polje.setCustomValidity('')
    }
  }

  function preveriDvomestno(polje){
    console.log(polje.validity)
    if(polje.validity.valueMissing){
      polje.setCustomValidity('To polje je obvezno!')
    }
    else if(polje.validity.stepMismatch){
      polje.setCustomValidity('Vpisati morate vrednost na največ 2 decimalni mesti natančno!')
    }
    else{
      polje.setCustomValidity('')
    }
  }

  function preveriStevilo(polje){
    console.log(polje.validity)
    if(polje.validity.valueMissing){
      polje.setCustomValidity('To polje je obvezno!')
    }
    else if(polje.validity.stepMismatch){
      polje.setCustomValidity('Vpisati morate točno letnico!')
    }
    else{
      polje.setCustomValidity('')
    }
  }


