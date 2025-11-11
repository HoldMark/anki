document.addEventListener("DOMContentLoaded", () => {
});

{
    // hide image block if there is no image

    let imgBlock = document.querySelector('.img-block');
    let imageContainer = document.querySelector('.image-container');

    if (imgBlock && imageContainer) {
        let images = imgBlock.querySelectorAll('img');
        if (images.length === 0) {
            imageContainer.style.display = 'none';
        }
    }
}
