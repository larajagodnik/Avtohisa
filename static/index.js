'use strict'    

function filtertabela(){
    let izbrano = document.getElementById('barve')
    var barva = izbrano.options[izbrano.selectedIndex].text;
    const response = await fetch('/avto_prijavljen/filtriraj_po_barvah', {
    method: 'POST',
    body: myBody, // string or object
    headers: {
      'Content-Type': 'application/json'
    }
  });
  
}