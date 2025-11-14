document.addEventListener("DOMContentLoaded", () => {
});

{
    let currentDate = new Date();
    let todayNum = currentDate.getDate();
    let listExamplesHtml = document.querySelectorAll('.hidden-example');

    let listExamples = [];

    for (var i =0;i < listExamplesHtml.length; i++){
        if (listExamplesHtml[i].innerHTML !=''){
            listExamples.push(listExamplesHtml[i].innerHTML);
        }
    }

    let indexExample = (todayNum-1) % listExamples.length;
    let mainExample = '!!! No example. Need to fill it !!!';

    if (listExamples.length != 0){
        mainExample = listExamples[indexExample];
    }

    let mainExNode = document.querySelector('.main-example-span');
    mainExNode.innerHTML = mainExample;


    // remove all empty <li> and main example

    let listItems = document.querySelectorAll('li');

    listItems.forEach(item=>{

        if (item.innerHTML == ''){
            item.remove();
        }
        else if (item.innerHTML == mainExample){
            item.remove();
        }
    });


    // remove hr & ul if list is empty

    listItems = document.querySelectorAll('li');

    let ulItem = document.querySelector('ul')
    let hrItem = document.querySelector('hr')


    if (listItems.length == 0){
        ulItem.remove();
        hrItem.remove();
    }

}