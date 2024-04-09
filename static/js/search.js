$('.product_search').on('input',function(){
     let value = this.value;
     if(value == ""){
         let filter = value.toUpperCase();

         let sections = $('section');
         for(let i = 0; i< sections.length; i++){
             sections[i].style.display="block";

         }
     }else{
         let filter = value.toUpperCase();

         let sections = $('section');
         console.log(sections);
         for(let i = 0; i< sections.length; i++){
             sections[i].style.display="block";
             if(!(sections[i].id.toUpperCase().indexOf(filter)>-1 )){

                 sections[i].style.display="none";
             }
         }
     }
//alert ("test");
 });


$('.test').on('change',function(){

    let value = this.value;
        let filter = value.toUpperCase();
        let sections = $('section');
        for(let i = 0; i< sections.length; i++){
            sections[i].style.display="block";
            if(!(sections[i].id.toUpperCase().indexOf(filter)>-1 )){

                sections[i].style.display="none";
            }
        }

 
});


$('.type-mis').on('click',function(){;
     let value = this.innerHTML;
     console.log(this.value);
 

        let sections = $('section');
        console.log(sections);
        for(let i = 0; i< sections.length; i++){
            sections[i].style.display="block";
           
             if(!(sections[i].classList.contains(value)) ){
                 sections[i].style.display="none";
             }
        }
    
//alert ("test");
 });


$('.test').on('change',function(){

    let value = this.value;
        let filter = value.toUpperCase();
        let sections = $('section');
        for(let i = 0; i< sections.length; i++){
            sections[i].style.display="block";
            if(!(sections[i].id.toUpperCase().indexOf(filter)>-1 )){

                sections[i].style.display="none";
            }
        }

 
});



function hiddenDostovka(){
     let samavizov = document.getElementById("samavizov");
     let dastavka = document.getElementById("dastavka");
     dastavka.style.display="none";
     samavizov.style.display ="block";


 }
function hiddenSamavizov(){
     let samavizov = document.getElementById("samavizov");
     let dastavka = document.getElementById("dastavka");
     samavizov.style.display ="none";
     dastavka.style.display="block"; 
 }


