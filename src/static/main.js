console.log('hello world')

const shareBtns = [...document.getElementsByClassName('share-btn')]
console.log(shareBtns)

shareBtns.forEach(btn=> btn.addEventListener('click', ()=>{
    console.log('click')
    const msg = "Hey, I found a book called " + btn.getAttribute("data-title") +", check it out at " + btn.getAttribute("data-url")
    navigator.clipboard.writeText(msg)
    btn.textContent = 'Copied'
    console.log(msg)
}))