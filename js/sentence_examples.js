document.addEventListener("DOMContentLoaded", () => {
});

{
    let currentDate = new Date();
    let today_num = currentDate.getDate();
    let list_examples_html = document.querySelectorAll('.hidden_example');
    
    let list_examples = [];

    for (var i =0;i < list_examples_html.length; i++){
        if (list_examples_html[i].innerHTML !=''){
            list_examples.push(list_examples_html[i].innerHTML);
        }
    }

    let index_example = (today_num-1) % list_examples.length;
    let main_example = '!!! No example. Need to fill it !!!';
    
    if (list_examples.length != 0){
        main_example = list_examples[index_example];
    }
    
    let main_ex_node = document.querySelector('.main_example');
    main_ex_node.innerHTML = main_example;


    // remove all empty <li> and main example

    let list_items = document.querySelectorAll('li');

    list_items.forEach(item=>{

        if (item.innerHTML == ''){
            item.remove();
        }
        else if (item.innerHTML == main_example){
            item.remove();
        }
    });


    // remove hr & ul if list is empty

    list_items = document.querySelectorAll('li');

    let ul_item = document.querySelector('.answer_block ul')
    let hr_item = document.querySelector('.answer_block hr')


    if (list_items.length == 0){
        ul_item.remove();
        hr_item.remove();
    }

}