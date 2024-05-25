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

// Function to fetch response
async function fetchResponse(message, newMessage) {
    try {
        const response = await fetch('/query?sid=' + sessionStorage.getItem('helloComputerSession') + '&q=' + message);
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const data = await response.text();

        // Hide spinner and display result
        newMessage.innerHTML = '<img src="/img/assistant.webp" width="50px"> <div><pre>' + data + '</pre></div>';
    } catch (error) {
        newMessage.innerHTML = '<img src="/img/assistant.webp" width="50px">' + 'Error: ' + error.message;
    }
}

function addAIMessage(messageContent) {
    const newMessage = document.createElement('div');
    newMessage.classList.add('message', 'bg-white', 'p-2', 'mb-2', 'rounded');
    newMessage.innerHTML = '<img src="/img/assistant.webp" width="50px"> <div id="spinner" class="spinner"></div>';
    chatMessages.prepend(newMessage); // Add new message at the top
    fetchResponse(messageContent, newMessage);
}

function addAIManualMessage(m) {
    const newMessage = document.createElement('div');
    newMessage.classList.add('message', 'bg-white', 'p-2', 'mb-2', 'rounded');
    newMessage.innerHTML = '<img src="/img/assistant.webp" width="50px"> <div>' + m + '</div>';
    chatMessages.prepend(newMessage); // Add new message at the top
}

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
        addAIMessage(messageContent);
    }
};

sendButton.addEventListener('click', addUserMessage);

textarea.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        addUserMessage();
    }
});


document.addEventListener("DOMContentLoaded", function () {
    // Elements
    const spinner = document.getElementById('spinner');
    const resultDiv = document.getElementById('result');

    async function fetchGreeting() {
        try {
            const session_response = await fetch('/new_session');
            sessionStorage.setItem("helloComputerSession", JSON.parse(await session_response.text()));

            const response = await fetch('/greetings?sid=' + sessionStorage.getItem('helloComputerSession'));

            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            const data = await response.text();

            // Hide spinner and display result
            spinner.classList.add('hidden');
            resultDiv.classList.remove('hidden');
            resultDiv.textContent = data;
        } catch (error) {
            spinner.classList.add('hidden');
            resultDiv.classList.remove('hidden');
            resultDiv.textContent = 'Error: ' + error.message;
        }
    }
    // Call the function to fetch greeting
    fetchGreeting();
});

document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById('inputGroupFile01');
    const uploadButton = document.getElementById('uploadButton');
    const uploadResultDiv = document.getElementById('uploadResultDiv');

    uploadButton.addEventListener('click', async function () {
        const file = fileInput.files[0];

        if (!file) {
            uploadResultDiv.textContent = 'Please select a file.';
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload?sid=' + sessionStorage.getItem('helloComputerSession'), {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }

            const data = await response.text();
            uploadResultDiv.textContent = 'Upload successful: ' + JSON.parse(data)['message'];

            addAIManualMessage('File uploaded and processed!');
        } catch (error) {
            uploadResultDiv.textContent = 'Error: ' + error.message;
        }
    });
});
