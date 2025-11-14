document.addEventListener("DOMContentLoaded", () => {
});

{
    // remove all empty <li>

    let listItems = document.querySelectorAll('li');
    listItems.forEach(item=>{
        if (item.innerHTML == ''){
            item.remove();
        }
    });

}
