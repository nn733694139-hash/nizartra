(() => {
    const root = document.getElementById('chatApp');
    if (!root) return;

    const csrfToken = root.dataset.csrfToken;
    const chatName = root.dataset.chatName;
    const messagesUrl = root.dataset.messagesUrl;
    const sendUrl = root.dataset.sendUrl;
    const uploadUrl = root.dataset.uploadUrl;
    const typingUrl = root.dataset.typingUrl;
    const isAdmin = root.dataset.chatIsAdmin === 'true';
    const textInput = document.getElementById('chatText');
    const fileInput = document.getElementById('chatFile');
    const composer = document.getElementById('chatComposer');
    const messagesEl = document.getElementById('chatMessages');
    const emptyEl = document.getElementById('chatEmpty');
    const errorEl = document.getElementById('chatError');
    const sendButton = document.getElementById('sendButton');
    const replyToInput = document.getElementById('replyTo');
    const replyContext = document.getElementById('replyContext');
    const replyName = document.getElementById('replyName');
    const connectionStatus = document.getElementById('connectionStatus');
    const onlineCount = document.getElementById('chatOnlineCount');
    const typingIndicator = document.getElementById('chatTypingIndicator');
    const knownMessages = new Map();
    let selectedReply = null;
    let busy = false;
    let typingActive = false;
    let typingStopTimer;
    let lastTypingPulse = 0;

    function setConnectionState(isOnline) {
        connectionStatus.classList.toggle('is-online', isOnline);
        connectionStatus.classList.toggle('is-offline', !isOnline);
        connectionStatus.querySelector('strong').textContent = isOnline ? 'Online' : 'Offline';
    }

    function showError(message) {
        errorEl.textContent = message;
        errorEl.hidden = !message;
    }

    function formatTime(value) {
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? '' : date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
    }

    function addMedia(bubble, attachment) {
        const media = document.createElement('div');
        media.className = 'message-media';
        if (attachment.kind === 'image') {
            const image = document.createElement('img');
            image.src = attachment.url;
            image.alt = attachment.name;
            image.loading = 'lazy';
            media.append(image);
        } else if (attachment.kind === 'video') {
            const video = document.createElement('video');
            video.src = attachment.url;
            video.controls = true;
            video.preload = 'metadata';
            video.playsInline = true;
            media.append(video);
        } else if (attachment.kind === 'audio') {
            const audio = document.createElement('audio');
            audio.src = attachment.url;
            audio.controls = true;
            audio.preload = 'metadata';
            media.append(audio);
        } else {
            const fileLink = document.createElement('a');
            fileLink.className = 'message-file-link';
            fileLink.href = attachment.url;
            fileLink.target = '_blank';
            fileLink.rel = 'noopener noreferrer';
            fileLink.textContent = attachment.name;
            media.append(fileLink);
        }
        const actions = document.createElement('div');
        actions.className = 'media-actions';
        const download = document.createElement('a');
        download.className = 'media-download';
        download.href = attachment.download_url;
        download.textContent = 'Download';
        actions.append(download);
        media.append(actions);
        bubble.append(media);
    }

    function renderMessage(message) {
        const row = document.createElement('article');
        row.className = 'message-row';
        if (message.name === chatName) row.classList.add('is-own');
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        const authorLine = document.createElement('div');
        authorLine.className = 'message-author-line';
        const author = document.createElement('strong');
        author.className = 'message-author';
        author.textContent = message.name;
        let presence = null;
        if (!message.is_admin) {
            presence = document.createElement('span');
            presence.className = `presence-dot ${message.online ? 'is-online' : 'is-offline'}`;
            presence.setAttribute('role', 'img');
            presence.setAttribute('aria-label', message.online ? 'Online' : 'Offline');
            presence.title = message.online ? 'Online' : 'Offline';
        }
        const badge = document.createElement('span');
        badge.className = message.is_admin ? 'client-badge is-boss' : 'client-badge';
        badge.textContent = message.badge_label || (message.is_admin ? 'BOSS' : 'HOST');
        authorLine.append(author);
        if (presence) authorLine.append(presence);
        authorLine.append(badge);
        bubble.append(authorLine);

        if (message.reply_to && knownMessages.has(message.reply_to)) {
            const parent = knownMessages.get(message.reply_to);
            const reply = document.createElement('p');
            reply.className = 'message-reply';
            reply.textContent = `Reply to ${parent.name}: ${parent.text || 'Shared media'}`;
            bubble.append(reply);
        }
        if (message.text) {
            const text = document.createElement('p');
            text.className = 'message-text';
            text.textContent = message.text;
            bubble.append(text);
        }
        for (const attachment of message.attachments || []) addMedia(bubble, attachment);

        const meta = document.createElement('div');
        meta.className = 'message-meta';
        const time = document.createElement('time');
        time.dateTime = message.submitted_at;
        time.textContent = formatTime(message.submitted_at);
        const replyButton = document.createElement('button');
        replyButton.className = 'reply-button';
        replyButton.type = 'button';
        replyButton.textContent = 'Reply';
        replyButton.addEventListener('click', () => beginReply(message));
        meta.append(time, replyButton);
        bubble.append(meta);
        row.append(bubble);
        return row;
    }

    function beginReply(message) {
        selectedReply = message;
        replyToInput.value = message.id;
        replyName.textContent = message.name;
        replyContext.hidden = false;
        textInput.focus();
    }

    function clearReply() {
        selectedReply = null;
        replyToInput.value = '';
        replyContext.hidden = true;
        replyName.textContent = '';
    }

    function sendTypingStatus(typing) {
        if (isAdmin) return;
        fetch(typingUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
            body: JSON.stringify({csrf_token: csrfToken, typing}),
        }).catch(() => {});
    }

    function stopTyping() {
        window.clearTimeout(typingStopTimer);
        if (!typingActive) return;
        typingActive = false;
        lastTypingPulse = 0;
        sendTypingStatus(false);
    }

    function updateTypingStatus() {
        if (isAdmin) return;
        if (!textInput.value.trim()) {
            stopTyping();
            return;
        }
        const now = Date.now();
        if (!typingActive || now - lastTypingPulse >= 2000) {
            typingActive = true;
            lastTypingPulse = now;
            sendTypingStatus(true);
        }
        window.clearTimeout(typingStopTimer);
        typingStopTimer = window.setTimeout(stopTyping, 3000);
    }

    document.getElementById('cancelReply').addEventListener('click', clearReply);

    async function loadMessages() {
        try {
            const response = await fetch(messagesUrl, {headers: {'Accept': 'application/json'}});
            if (response.status === 401) {
                window.location.assign('/chat');
                return;
            }
            if (!response.ok) throw new Error('Unable to connect to the chat.');
            const data = await response.json();
            onlineCount.textContent = `${data.online_count || 0} online`;
            const typingUsers = data.typing_users || [];
            typingIndicator.hidden = typingUsers.length === 0;
            if (typingUsers.length === 1) {
                typingIndicator.textContent = `${typingUsers[0]} is typing...`;
            } else if (typingUsers.length > 1) {
                typingIndicator.textContent = `${typingUsers.join(', ')} are typing...`;
            }
            const nearBottom = messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 70;
            const fragment = document.createDocumentFragment();
            knownMessages.clear();
            for (const message of data.messages || []) knownMessages.set(message.id, message);
            for (const message of data.messages || []) fragment.append(renderMessage(message));
            messagesEl.replaceChildren(fragment);
            if (!data.messages || data.messages.length === 0) messagesEl.append(emptyEl);
            if (nearBottom) messagesEl.scrollTop = messagesEl.scrollHeight;
            setConnectionState(true);
        } catch (error) {
            setConnectionState(false);
        }
    }

    async function sendMessage(event) {
        event.preventDefault();
        stopTyping();
        if (busy) return;
        const text = textInput.value.trim();
        const file = fileInput.files[0];
        if (!text && !file) {
            showError('Write a message or choose a file to share.');
            return;
        }
        if (text.length > 2000) {
            showError('Messages must be 2,000 characters or fewer.');
            return;
        }
        if (file && file.size > 10 * 1024 * 1024) {
            showError('Files must be 10 MB or smaller.');
            return;
        }

        const endpoint = file ? uploadUrl : sendUrl;
        const options = file
            ? {method: 'POST', body: new FormData(composer)}
            : {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({csrf_token: csrfToken, message: text, reply_to: replyToInput.value}),
            };
        if (file) {
            options.body.set('csrf_token', csrfToken);
            options.body.set('message', text);
            options.body.set('reply_to', replyToInput.value);
            options.body.set('file', file);
        }

        busy = true;
        sendButton.disabled = true;
        showError('');
        try {
            const response = await fetch(endpoint, options);
            if (response.status === 401) {
                window.location.assign('/chat');
                return;
            }
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'The message could not be sent.');
            textInput.value = '';
            fileInput.value = '';
            clearReply();
            await loadMessages();
            textInput.focus();
        } catch (error) {
            showError(error.message || 'The message could not be sent.');
        } finally {
            busy = false;
            sendButton.disabled = false;
        }
    }

    function checkVideoDuration(file) {
        if (!file || !file.type.startsWith('video/')) return Promise.resolve(true);
        return new Promise(resolve => {
            const video = document.createElement('video');
            const objectUrl = URL.createObjectURL(file);
            video.preload = 'metadata';
            video.onloadedmetadata = () => {
                URL.revokeObjectURL(objectUrl);
                if (video.duration > 60) {
                    showError('Videos must be 60 seconds or shorter.');
                    fileInput.value = '';
                    resolve(false);
                } else {
                    showError('');
                    resolve(true);
                }
            };
            video.onerror = () => {
                URL.revokeObjectURL(objectUrl);
                showError('This video could not be checked. Try an MP4 or WebM file under 10 MB.');
                fileInput.value = '';
                resolve(false);
            };
            video.src = objectUrl;
        });
    }

    fileInput.addEventListener('change', async () => {
        const file = fileInput.files[0];
        if (!file) return;
        if (file.size > 10 * 1024 * 1024) {
            showError('Files must be 10 MB or smaller.');
            fileInput.value = '';
            return;
        }
        await checkVideoDuration(file);
    });
    textInput.addEventListener('input', updateTypingStatus);
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) stopTyping();
    });
    composer.addEventListener('submit', sendMessage);
    textInput.addEventListener('keydown', event => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            composer.requestSubmit();
        }
    });
    window.addEventListener('online', () => setConnectionState(true));
    window.addEventListener('offline', () => setConnectionState(false));

    loadMessages();
    window.setInterval(loadMessages, 2500);
})();
