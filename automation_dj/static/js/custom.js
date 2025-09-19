// Auto fadeout messages
setTimeout(function(){
    const messages = document.getElementById('messages');
    if(messages) {
        messages.style.transition = "opacity 1s";
        messages.style.opacity = 0;
        setTimeout(()=>messages.remove(), 1000);
    }
}, 8000);

// Close buttons
const closeButtons = document.querySelectorAll('.custom-close-btn');
closeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        btn.parentElement.style.display = 'none';
    });
});
