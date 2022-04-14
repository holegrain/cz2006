console.log('hello world')

// return a promise
function copyToClipboard(textToCopy) {

    let textArea = document.createElement("textarea");
    textArea.value = textToCopy;
    // make the textarea out of viewport
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    return new Promise((res, rej) => {
        // here the magic happens
        document.execCommand('copy') ? res() : rej();
        textArea.remove();
    });
}

const shareBtns = [...document.getElementsByClassName('share-btn')]
console.log(shareBtns)

shareBtns.forEach(btn=> btn.addEventListener('click', ()=>{
    console.log('click')
    const msg = "Hey, I found a book called " + btn.getAttribute("data-title") +", check it out at " + btn.getAttribute("data-url")
    copyToClipboard(msg)
    btn.textContent = 'Copied'
    console.log(msg)
}))