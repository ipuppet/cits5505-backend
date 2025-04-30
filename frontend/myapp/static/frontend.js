// fetch("../templates/navbar.html")
//     .then((response) => response.text())
//     .then((data) => {   
//         document.getElementById("navbar").innerHTML = data;
//     })
formBlock=document.getElementById("form");
add=document.getElementById("add");
del=document.getElementById("delete");
add.addEventListener("click",function(){ 
    if(formBlock.children.length>6){
        alert("You can only add 7 rows of data by form")
        return;
    }
   blockContent=document.createElement('div');
   blockContent.classList.add('formBlock');
   blockContent.innerHTML=`<input type='text' name='Running' placeholder='Running'> <input type='text' name='Cycling' placeholder='Cycling'> <input type='text' name='Swimming' placeholder='Swimming'> <input type='text' name='Yoga' placeholder='Yoga'> <input type='text' name='Weight' placeholder='Weight'> <button type="button" class="delete btn btn-outline-primary">delete</button>`;
//    <button type='button' class=''>delete row</button>
   formBlock.appendChild(blockContent);
})
formBlock.addEventListener("click",function(event){
   
    if(event.target&&event.target.classList.contains('delete')){
        event.target.closest('.formBlock').remove();
    }
})