document.addEventListener("DOMContentLoaded", () => {
});

{

    let mainExNode = document.querySelector(".main-example-span");
    let mainExample = "!!! No example. Need to fill it !!!";

    if (mainExNode) {
        console.log("found: .main-example-span");

        let currentDate = new Date();
        let todayNum = currentDate.getDate();
        let listExamplesHtml = document.querySelectorAll(".hidden-example");

        let listExamples = [];

        for (var i =0; i < listExamplesHtml.length; i++){
            if (listExamplesHtml[i].innerHTML !=""){
                listExamples.push(listExamplesHtml[i].innerHTML);
            }
        }

        let indexExample = (todayNum-1) % listExamples.length;

        if (listExamples.length != 0){
            mainExample = listExamples[indexExample];
        }

        if (mainExNode){
            mainExNode.innerHTML = mainExample;
            console.log("added main example");
        }
    }

    // remove all empty <li> and main example

    let listItems = document.querySelectorAll("li");

    listItems.forEach(item=>{

        if (item.innerHTML == ""){
            item.remove();
        }
        else if (item.innerHTML == mainExample){
            item.remove();
        }
        console.log("removed empty li");
    });


    // remove hr & example-block if list is empty

    listItems = document.querySelectorAll("li");

    let exampleBlock = document.querySelector(".example-block");
    let hrBeforeExampleBlock = document.querySelector(".hr-before-example-block");

    if (listItems.length == 0){
        if (exampleBlock){
            exampleBlock.remove();
            console.log("removed example block");
        }
        if (hrBeforeExampleBlock){
            hrBeforeExampleBlock.remove();
            console.log("removed hr before example block");
        }
    }

}