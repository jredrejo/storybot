// State machine
const STATES = {
    IDLE: 'idle',
    PLAYING: 'playing',
    THANKYOU: 'thankyou'
};

let currentState = STATES.IDLE;
let stories = [];
let currentStory = null;
let nfcEventSource = null;
const audioElement = document.getElementById('story-audio');

function transitionTo(newState, story = null) {
    currentState = newState;
    currentStory = story;

    // Hide all screens
    document.querySelectorAll('[data-screen]').forEach(el => el.classList.add('hidden'));

    switch (newState) {
        case STATES.IDLE:
            document.querySelector('[data-screen="idle"]').classList.remove('hidden');
            break;
        case STATES.PLAYING:
            showPlaybackScreen(story);
            document.querySelector('[data-screen="playing"]').classList.remove('hidden');
            playAudio(story);
            break;
        case STATES.THANKYOU:
            document.querySelector('[data-screen="thankyou"]').classList.remove('hidden');
            setTimeout(() => transitionTo(STATES.IDLE), 4000);
            break;
    }
}

// Story grid rendering
async function loadStories() {
    try {
        const response = await fetch('/api/stories');
        const data = await response.json();
        stories = data.stories;
        renderStoryGrid();
    } catch (err) {
        console.error('Failed to load stories:', err);
    }
}

function renderStoryGrid() {
    const grid = document.querySelector('.story-grid');
    grid.innerHTML = '';

    stories.forEach(story => {
        const card = document.createElement('div');
        card.className = 'story-card';
        card.style.backgroundColor = story.led_color + '40'; // 25% opacity
        card.setAttribute('aria-label', story.title);
        card.textContent = story.emoji;
        card.onclick = () => playStory(story);
        grid.appendChild(card);
    });
}

function playStory(story) {
    if (currentState !== STATES.IDLE) return;

    // Ensure audio is unlocked before playing
    unlockAudio();

    // Add a small delay to ensure audio context is ready
    setTimeout(() => {
        transitionTo(STATES.PLAYING, story);
    }, 100);
}

// Playback functions
function showPlaybackScreen(story) {
    const container = document.querySelector('[data-screen="playing"]');
    container.style.setProperty('--story-color', story.led_color);

    const cover = container.querySelector('.cover-image');
    const emoji = container.querySelector('.cover-emoji');

    if (story.cover_image) {
        cover.src = `/static/stories/${story.id}/${story.cover_image}`;
        cover.style.display = 'block';
        emoji.style.display = 'none';
    } else {
        cover.style.display = 'none';
        emoji.style.display = 'block';
        emoji.textContent = story.emoji;
    }
}

function playAudio(story) {
    const audioPath = `/static/stories/${story.id}/${story.audio_file}`;
    console.log('Playing audio:', audioPath);
    console.log('Audio element:', audioElement);
    console.log('Audio src before:', audioElement.src);

    // Reset audio element
    audioElement.currentTime = 0;
    audioElement.src = audioPath;

    console.log('Audio src after:', audioElement.src);
    console.log('Audio readyState:', audioElement.readyState);

    // Try to play with better error handling
    const playPromise = audioElement.play();

    if (playPromise !== undefined) {
        playPromise.then(() => {
            console.log('Audio playback started successfully');
        }).catch(err => {
            console.error('Playback failed:', err);
            console.error('Error name:', err.name);
            console.error('Error message:', err.message);

            // If it's a permission error, the user needs to interact first
            if (err.name === 'NotAllowedError') {
                console.error('Autoplay prevented - user interaction required');
            }

            transitionTo(STATES.IDLE);
        });
    }
}

// Audio ended event handler
function handleAudioEnded() {
    console.log('Audio ended, transitioning to thank you');
    transitionTo(STATES.THANKYOU);
}

audioElement.addEventListener('ended', handleAudioEnded);

// Also handle audio errors
audioElement.addEventListener('error', (e) => {
    console.error('Audio error event:', e);
    console.error('Audio element error code:', audioElement.error);
    console.error('Audio element src:', audioElement.src);
    console.error('Audio element networkState:', audioElement.networkState);

    // Translate error code to message
    const errorMessages = {
        1: 'MEDIA_ERR_ABORTED - User aborted the audio',
        2: 'MEDIA_ERR_NETWORK - Network error occurred',
        3: 'MEDIA_ERR_DECODE - Audio decoding failed',
        4: 'MEDIA_ERR_SRC_NOT_SUPPORTED - Audio format not supported'
    };

    console.error('Error description:', errorMessages[audioElement.error?.code] || 'Unknown error');

    transitionTo(STATES.IDLE);
});

// Log when audio can play through
audioElement.addEventListener('canplaythrough', () => {
    console.log('Audio can play through - fully loaded');
});

// Log when audio starts playing
audioElement.addEventListener('play', () => {
    console.log('Audio play event fired');
});

// NFC listener
function startNFCListener() {
    nfcEventSource = new EventSource('/api/nfc/read');

    nfcEventSource.addEventListener('card', async (event) => {
        if (currentState !== STATES.IDLE) return; // Ignore during playback

        try {
            const { uid } = JSON.parse(event.data);
            const response = await fetch(`/api/stories/nfc/${encodeURIComponent(uid)}`);
            if (response.ok) {
                const story = await response.json();
                playStory(story);
            }
        } catch (err) {
            console.error('NFC lookup failed:', err);
        }
    });

    nfcEventSource.addEventListener('error', () => {
        // Auto-reconnect built into EventSource
    });
}

// Audio unlock mechanism - must be called after user gesture
let audioUnlocked = false;

function unlockAudio() {
    if (audioUnlocked) return;

    console.log('Attempting to unlock audio...');

    // Create a silent audio file to unlock audio context
    const silentAudio = new Audio('data:audio/wav;base64,UklGRjIAAABXQVZFZm10IBIAAAABAAEAQB8AAEAfAAABAAgAAABmYWN0BAAAAAAAAABkYXRhAAAAAA==');

    const playPromise = silentAudio.play();

    if (playPromise !== undefined) {
        playPromise.then(() => {
            console.log('Audio unlocked successfully');
            audioUnlocked = true;
            silentAudio.pause();
            silentAudio.src = '';
        }).catch(err => {
            console.warn('Audio unlock failed:', err);
        });
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    loadStories();
    startNFCListener();

    // Unlock audio on first user interaction (touch/click)
    const unlockEvents = ['click', 'touchstart', 'keydown'];
    unlockEvents.forEach(eventType => {
        document.body.addEventListener(eventType, () => {
            unlockAudio();
        }, { once: true });
    });
});
