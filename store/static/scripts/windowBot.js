document.addEventListener("DOMContentLoaded", function () {

    // Button chat bot
    const btnBot = document.querySelector('.button-chat');
    const windowBot = document.querySelector('.windowBot');
    const closeBtn = document.querySelector('.close-img');

    function unfoldWindow() {
        if (windowBot.style.display == 'none' || windowBot.style.display === '') {
            windowBot.style.display = 'flex';
        } else {
            windowBot.style.display = 'none';
        }
    }

    function closeWindow() {
        windowBot.style.display = 'none';
    }

    btnBot.addEventListener('click', function () {
        unfoldWindow();
    });

    closeBtn.addEventListener('click', function () {
        closeWindow();
    });

    // Function to scroll to the bottom
    function scrollToBottom() {
        var chatContent = document.getElementById("chat-content");
        chatContent.scrollTop = chatContent.scrollHeight;
    }

    // Scroll to the bottom initially
    scrollToBottom();

    $(document).ready(function () {
        $('#chat-form').on('submit', function (event) {
            event.preventDefault();

            let userInput = $('#user_input').val();
            if (!userInput.trim()) {
                return; // Prevent empty submissions
            }

            // Add user message to chat
            $('#chat-content').append('<div class="message user">' + userInput + '</div>');

            // Clear input field
            $('#user_input').val('');
            scrollToBottom();

            // Show typing indicator after user message
            $('#chat-content').append('<div class="message bot" id="typing-indicator"><em>PC Guru is typing...</em></div>');
            scrollToBottom();

            $.ajax({
                url: '', // URL of your backend that handles the chat
                type: 'POST',
                data: {
                    'user_input': userInput,
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function (data) {
                    // Remove typing indicator
                    $('#typing-indicator').remove();

                    data.chat_messages.forEach(function (message) {
                        // Add the message with HTML content
                        $('#chat-content').append('<div class="message ' + message.sender + '">' + message.text + '</div>');
                    });
                    scrollToBottom();
                },
                error: function () {
                    // Hide typing indicator if there's an error
                    $('#typing-indicator').hide();
                }
            });
        });

        // Use MutationObserver to detect changes in the chat content
        const chatContent = document.getElementById('chat-content');
        const observer = new MutationObserver(scrollToBottom);
        observer.observe(chatContent, { childList: true });
    });
});
