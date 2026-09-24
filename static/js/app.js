// Silvercare Client-side Script

document.addEventListener('DOMContentLoaded', () => {
    // 1. Chatbot Widget Setup
    const toggler = document.getElementById('chatbotToggler');
    const chatWindow = document.getElementById('chatWindow');
    const closeBtn = document.getElementById('closeChatBtn');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatBody = document.getElementById('chatBody');

    if (toggler && chatWindow) {
        toggler.addEventListener('click', () => {
            chatWindow.style.display = chatWindow.style.display === 'flex' ? 'none' : 'flex';
            if (chatWindow.style.display === 'flex' && chatInput) {
                chatInput.focus();
            }
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                chatWindow.style.display = 'none';
            });
        }

        if (chatForm) {
            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const msg = chatInput.value.trim();
                if (!msg) return;

                // Append user message
                appendMessage('user', msg);
                chatInput.value = '';

                // Typing indicator
                const typingBubble = appendMessage('bot', 'SilverBot is typing...');

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: msg })
                    });
                    const data = await res.json();
                    typingBubble.remove();

                    let replyContent = data.reply || "I'm here to help!";
                    if (data.action_url) {
                        replyContent += `<br><a href="${data.action_url}" class="btn btn-sm btn-primary-custom mt-2">${data.action_label || 'Proceed'}</a>`;
                    }
                    appendMessage('bot', replyContent, true);
                } catch (err) {
                    typingBubble.remove();
                    appendMessage('bot', "Sorry, I am temporarily having trouble connecting. Please try again.");
                }
            });
        }
    }

    function appendMessage(sender, text, isHTML = false) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender}`;
        if (isHTML) {
            bubble.innerHTML = text;
        } else {
            bubble.textContent = text;
        }
        chatBody.appendChild(bubble);
        chatBody.scrollTop = chatBody.scrollHeight;
        return bubble;
    }

    // 2. Preset Destination Clickers in Booking Form
    const presetBadges = document.querySelectorAll('.preset-destination');
    const destinationInput = document.getElementById('destinationInput');
    const destinationTypeSelect = document.getElementById('destinationTypeSelect');

    presetBadges.forEach(badge => {
        badge.addEventListener('click', () => {
            const locName = badge.dataset.location;
            const locType = badge.dataset.type;
            if (destinationInput && locName) destinationInput.value = locName;
            if (destinationTypeSelect && locType) destinationTypeSelect.value = locType;
        });
    });

    // 3. Real-Time Tracking Poller
    const trackingContainer = document.getElementById('trackingContainer');
    if (trackingContainer) {
        const bookingCode = trackingContainer.dataset.code;
        if (bookingCode) {
            setInterval(async () => {
                try {
                    const response = await fetch(`/api/booking-status/${bookingCode}`);
                    if (response.ok) {
                        const data = await response.json();
                        const currentStatusElem = document.getElementById('currentStatusBadge');
                        if (currentStatusElem && currentStatusElem.textContent.trim() !== data.status) {
                            // Status changed! Reload page to update full timeline and actions
                            window.location.reload();
                        }
                    }
                } catch (e) {
                    console.log('Status polling...', e);
                }
            }, 6000);
        }
    }
});
