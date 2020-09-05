'use strict'    

function filtertabela(el){
    let count_top = 1;
    let stolpec  = [el.dataset.stolpec];
    var vrednost = el.options[el.selectedIndex].value;
    let tabela = document.getElementById('tabela_avtov');
    [...tabela.rows].forEach(vrstica => {  
        vrstica.style.display = ''
    })
    var leto_el = document.getElementById('leto_izdelave');
    var barva_el = document.getElementById('barve');
    var tip_el = document.getElementById('tipi');
    var znamka_el = document.getElementById('znamka');
    var starost_el = document.getElementById('starost');
    var izbrane_vrednosti = [starost_el.options[starost_el.selectedIndex].value, leto_el.options[leto_el.selectedIndex].value, znamka_el.options[znamka_el.selectedIndex].value,  tip_el.options[tip_el.selectedIndex].value, barva_el.options[barva_el.selectedIndex].value];
    var count = 5;
   
    izbrane_vrednosti.forEach(vrednost => {
      [...tabela.rows].forEach(vrstica => {         
        let vrednost_v_tabeli = vrstica.cells[count].innerText
        
        if(vrednost != 'null' && count_top != 1){
        
          if(vrednost_v_tabeli.toLocaleLowerCase().indexOf(vrednost.toLocaleLowerCase()) >= 0) {
          
            
              
          }else{
          
            vrstica.style.display = 'none'
          }
        }
        count_top++;
      })
      count_top = 1;
      count--
    })
    
}

  function seUjema(vrstica, stolpec, vrednost) {
    let vsebina = vrstica.cells[stolpec].innerText

    return vsebina.toLocaleLowerCase().indexOf(vrednost.toLocaleLowerCase()) >= 0
}

function openNav() {
  document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
  document.getElementById("mySidenav").style.width = "0";

}

