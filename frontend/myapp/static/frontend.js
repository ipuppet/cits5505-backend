// fetch("../templates/navbar.html")
//     .then((response) => response.text())
//     .then((data) => {   
//         document.getElementById("navbar").innerHTML = data;
//     })
// formBlock=document.getElementById("form");
// add=document.getElementById("add");
// del=document.getElementById("delete");
// add.addEventListener("click",function(){ 
//     if(formBlock.children.length>6){
//         alert("You can only add 7 rows of data by form")
//         return;
//     }
//    blockContent=document.createElement('div');
//    blockContent.classList.add('formBlock');
//    blockContent.innerHTML=`<input type='text' name='Running' placeholder='Running'> <input type='text' name='Cycling' placeholder='Cycling'> <input type='text' name='Swimming' placeholder='Swimming'> <input type='text' name='Yoga' placeholder='Yoga'> <input type='text' name='Weight' placeholder='Weight'> <button type="button" class="delete btn btn-outline-primary">delete</button>`;
// //    <button type='button' class=''>delete row</button>
//    formBlock.appendChild(blockContent);
// })
// formBlock.addEventListener("click",function(event){
   
//     if(event.target&&event.target.classList.contains('delete')){
//         event.target.closest('.formBlock').remove();
//     }
// })

//upload file
//>>
let filebtn=document.querySelector('#filebtn');
        let formbtn=document.querySelector('#formbtn');
        let uploadForm=document.querySelector('#uploadForm');
        let uploadFile=document.querySelector('#uploadFile');
        filebtn.addEventListener('click',function(){
            filebtn.classList.remove('outset');
            filebtn.classList.add('inset');
            formbtn.classList.remove('inset');
            formbtn.classList.add('outset');
            uploadFile.style.display="block";
            uploadForm.style.display="none";            
        })
        formbtn.addEventListener('click',function(){
            filebtn.classList.remove('inset');
            filebtn.classList.add('outset');
            formbtn.classList.remove('outset');
            formbtn.classList.add('inset');
            uploadFile.style.display="none";
            uploadForm.style.display="block";
        })
        let select=document.querySelector('#select');
        let submit=document.querySelector('#submit');
        let nextForm=document.querySelector('#nextForm');
        let activities={running:
        `Running:&nbsp;
        <input type="text" placeholder="distance(km)">
        <input type="text" placeholder="duration">
        `, cycling:
        `Cycling:&nbsp
        <input type="text" placeholder="distance(km)">
        <input type="text" placeholder="duration">`
        , swimming:
        `Swimming:&nbsp;
        <input type="text" placeholder="distance(m)">
        <input type="text" placeholder="duration">`
        , yoga:"Yoga:&nbsp<input type='number' placeholder='duration'>"
        , weight:
        `Weight:&nbsp;
        <input type='text' placeholder='weight(kg)'>
        <input type='text' placeholder='set'>
        <input type='text' placeholder='reps'>
        `}
        select.addEventListener('change',function(){
            let activity=select.value;
                if(activities[activity]){
                let activityBlock=document.createElement('div');
                activityBlock.classList.add('my-1');
                activityBlock.innerHTML=activities[activity];
                activityBlock.innerHTML+= '&nbsp;<button type="button" class="delete btn btn-outline-primary">delete</button>'
                nextForm.insertBefore(activityBlock,submit);
            }
        })
        nextForm.addEventListener('click',function(event){
            if(event.target && event.target.classList.contains('delete')){
                event.target.closest('div').remove();
            }
        })
//>>