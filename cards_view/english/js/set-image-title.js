document.addEventListener("DOMContentLoaded", () => {
});

{
    // set title for images

    let cardWord = document.querySelector('.img-block').getAttribute('data-word');
    let imgBlock = document.querySelector('.img-block');
    let caption = document.querySelector('.img-caption');

    imgBlock.addEventListener('mouseover', e => {
        if (e.target.tagName === 'IMG') {
            caption.textContent = cardWord;

            let rect = e.target.getBoundingClientRect();
            let blockRect = imgBlock.getBoundingClientRect();

            caption.style.left = (rect.left - blockRect.left) + 'px';
            caption.style.top = (rect.bottom - blockRect.top - caption.offsetHeight + 15) + 'px';

            caption.style.opacity = 1;
        }
    });

    imgBlock.addEventListener('mouseout', e => {
        if (e.target.tagName === 'IMG') {
            caption.style.opacity = 0;
        }
    });

}
