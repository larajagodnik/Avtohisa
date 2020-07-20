'use strict'    

function filtertabela(el){

    let stolpec  = [el.dataset.stolpec];

    var vrednost = el.options[el.selectedIndex].value;
    let tabela = document.getElementById('tabela_avtov');
    [...tabela.rows].forEach(vrstica => {         

      if(seUjema(vrstica, stolpec, vrednost) || vrednost == "null") {
          vrstica.style.display = 'inherit'
          
       } else {
         vrstica.style.display = 'none'
       }
    })
}

  function seUjema(vrstica, stolpec, vrednost) {
    let vsebina = vrstica.cells[stolpec].innerText

    return vsebina.toLocaleLowerCase().indexOf(vrednost.toLocaleLowerCase()) >= 0
}
