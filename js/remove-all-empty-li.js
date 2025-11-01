document.addEventListener("DOMContentLoaded", () => {
});

{
    // remove all empty <li>

    let list_items = document.querySelectorAll('li');
    list_items.forEach(item=>{
        if (item.innerHTML == ''){
            item.remove();
        }
    });

}
