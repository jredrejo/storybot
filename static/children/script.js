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
    transitionTo(STATES.PLAYING, story);
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
    audioElement.src = audioPath;
    audioElement.play().catch(err => {
        console.error('Playback failed:', err);
        transitionTo(STATES.IDLE);
    });
}

audioElement.addEventListener('ended', () => {
    transitionTo(STATES.THANKYOU);
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

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    loadStories();
    startNFCListener();

    // Unlock audio context on first touch (browser requirement)
    document.body.addEventListener('click', () => {
        audioElement.play().then(() => audioElement.pause()).catch(() => {});
    }, { once: true });
});
