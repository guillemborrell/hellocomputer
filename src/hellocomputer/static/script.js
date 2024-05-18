function toggleMenuArrow(a) {
    if (a.innerHTML == '▶') {
        a.innerHTML = '◀';
    }
    else {
        a.innerHTML = '▶'
    }
}

$('#menu-toggle').click(function (e) {
    e.preventDefault();
    $('#sidebar').toggleClass('toggled');
    toggleMenuArrow(document.getElementById('menu-toggle'));
});

const textarea = document.getElementById('chatTextarea');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.querySelector('.chat-messages');

textarea.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight <= 150 ? this.scrollHeight : 150) + 'px';
    if (this.scrollHeight > 150) {
        this.style.overflowY = 'scroll';
    } else {
        this.style.overflowY = 'hidden';
    }
});

function addUserMessage() {
    const messageContent = textarea.value.trim();
    if (messageContent) {
        const newMessage = document.createElement('div');
        newMessage.classList.add('message', 'bg-light', 'p-2', 'mb-2', 'rounded');
        newMessage.textContent = messageContent;
        chatMessages.prepend(newMessage); // Add new message at the top
        textarea.value = ''; // Clear the textarea
        textarea.style.height = 'auto'; // Reset the textarea height
        textarea.style.overflowY = 'hidden';
    }
};

sendButton.addEventListener('click', addUserMessage);

textarea.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        addUserMessage();
    }
});