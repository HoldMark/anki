document.addEventListener("DOMContentLoaded", () => {
});

{
    // hide image block if there is no image

    let imgBlock = document.querySelector('.img-block');
    let basicBlockImage = document.querySelector('.basic-block-image');

    if (imgBlock && basicBlockImage) {
        let images = imgBlock.querySelectorAll('.basic-block-image img');
        if (images.length === 0) {
            basicBlockImage.style.display = 'none';
        }
    }
}
