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

// Hide sidebar on mobile devices
document.addEventListener("DOMContentLoaded", function () {
    console.log('Width: ' + window.innerWidth + ' Height: ' + window.innerHeight);
    if ((window.innerWidth <= 800) && (window.innerHeight <= 600)) {
        $('#sidebar').toggleClass('toggled');
        toggleMenuArrow(document.getElementById('menu-toggle'));
        console.log('Mobile device detected. Hiding sidebar.');
    }
}
);

const textarea = document.getElementById('chatTextarea');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.querySelector('.chat-messages');

// Auto resize textarea
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
        newMessage.innerHTML = '<img src="/app/img/assistant.webp" width="50px"> <div><pre>' + data + '</pre></div>';
    } catch (error) {
        newMessage.innerHTML = '<img src="/app/img/assistant.webp" width="50px">' + 'Error: ' + error.message;
    }
}

// Function to add AI message
function addAIMessage(messageContent) {
    const newMessage = document.createElement('div');
    newMessage.classList.add('message', 'bg-white', 'p-2', 'mb-2', 'rounded');
    newMessage.innerHTML = '<img src="/app/img/assistant.webp" width="50px"> <div id="spinner" class="spinner"></div>';
    chatMessages.prepend(newMessage); // Add new message at the top
    fetchResponse(messageContent, newMessage);
}

function addAIManualMessage(m) {
    const newMessage = document.createElement('div');
    newMessage.classList.add('message', 'bg-white', 'p-2', 'mb-2', 'rounded');
    newMessage.innerHTML = '<img src="/app/img/assistant.webp" width="50px"> <div>' + m + '</div>';
    chatMessages.prepend(newMessage); // Add new message at the top
}

function addUserMessageBlock(messageContent) {
    const newMessage = document.createElement('div');
    newMessage.classList.add('message', 'bg-light', 'p-2', 'mb-2', 'rounded');
    newMessage.textContent = messageContent;
    chatMessages.prepend(newMessage); // Add new message at the top
    textarea.value = ''; // Clear the textarea
    textarea.style.height = 'auto'; // Reset the textarea height
    textarea.style.overflowY = 'hidden';
};

function addUserMessage() {
    const messageContent = textarea.value.trim();
    if (sessionStorage.getItem("helloComputerSessionLoaded") == 'false') {
        textarea.value = '';
        addAIManualMessage('Please upload a data file or select a session first!');
    }
    else {
        if (messageContent) {
            addUserMessageBlock(messageContent);
            addAIMessage(messageContent);
        }
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
            sessionStorage.setItem("helloComputerSessionLoaded", false);

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

// Function upload the data file
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
            const sid = sessionStorage.getItem('helloComputerSession');
            const session_name = document.getElementById('datasetLabel').value;
            const response = await fetch(`/upload?sid=${sid}&session_name=${session_name}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }

            const data = await response.text();
            uploadResultDiv.textContent = 'Upload successful: ' + JSON.parse(data)['message'];
            sessionStorage.setItem("helloComputerSessionLoaded", true);

            addAIManualMessage('File uploaded and processed!');
        } catch (error) {
            uploadResultDiv.textContent = 'Error: ' + error.message;
        }
    });
});

// Function to get the user sessions
document.addEventListener("DOMContentLoaded", function () {
    const sessionsButton = document.getElementById('loadSessionsButton');
    const sessions = document.getElementById('userSessions');
    const loadResultDiv = document.getElementById('loadResultDiv');

    sessionsButton.addEventListener('click', async function fetchSessions() {
        try {
            const response = await fetch('/sessions');
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            const data = JSON.parse(await response.text());
            sessions.innerHTML = '';
            data.forEach(item => {
                const listItem = document.createElement('li');
                const button = document.createElement('button');
                button.textContent = item.session_name;
                button.addEventListener("click", function () {
                    sessionStorage.setItem("helloComputerSession", item.sid);
                    sessionStorage.setItem("helloComputerSessionLoaded", true);
                    loadResultDiv.textContent = 'Session loaded';
                });
                listItem.appendChild(button);
                sessions.appendChild(listItem);
            });
        } catch (error) {
            sessions.innerHTML = 'Error: ' + error.message;
        }
    }
    );
}
);