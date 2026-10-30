const input = document.getElementById('txt');
const result = document.getElementById('result');
const listenButton = document.getElementById('listenButton');
const downloadButton = document.getElementById('downloadButton');
const copyButton = document.getElementById('copyIpa');
const speechNote = document.getElementById('speechNote');
const volumeSlider = document.getElementById('volumeSlider');
const volumeValue = document.getElementById('volumeValue');
const soundGrid = document.getElementById('soundGrid');
const accentDescription = document.getElementById('accentDescription');
const soundLibraryTitle = document.getElementById('soundLibraryTitle');
const soundLegend = document.getElementById('soundLegend');
const soundFilters = document.getElementById('soundFilters');
const articulationTitle = document.getElementById('articulationTitle');
const articulationStatus = document.getElementById('articulationStatus');
const articulationNote = document.getElementById('articulationNote');
const accentNote = document.getElementById('accentNote');
const startCaption = document.getElementById('startCaption');
const tongueStart = document.getElementById('tongueStart');
const tongueEnd = document.getElementById('tongueEnd');
const endDiagram = document.getElementById('endDiagram');

const soundSets = {
    'en-GB': {
        description: 'British English · Standard Southern British reference',
        note: 'British reference vowels use /ɒ/ in “hot” and a non-rhotic /ɑː/ in “car”. Regional accents vary.',
        sounds: [
            {ipa:'ɪ',category:'short',lexical:'KIT',word:'bit',example:'/bɪt/',tip:'Relaxed, near-high front vowel.',position:[224,91]},
            {ipa:'e',category:'short',lexical:'DRESS',word:'bed',example:'/bed/',tip:'Mid-front tongue; lips stay unrounded.',position:[220,103]},
            {ipa:'æ',category:'short',lexical:'TRAP',word:'cat',example:'/kæt/',tip:'Low front tongue with an open jaw.',position:[222,120]},
            {ipa:'ʌ',category:'short',lexical:'STRUT',word:'cup',example:'/kʌp/',tip:'Open-mid central tongue position.',position:[164,112]},
            {ipa:'ɒ',category:'short',lexical:'LOT',word:'hot',example:'/hɒt/',tip:'Low back vowel with rounded lips.',position:[112,121]},
            {ipa:'ʊ',category:'short',lexical:'FOOT',word:'put',example:'/pʊt/',tip:'Near-high back tongue; lightly rounded.',position:[114,91]},
            {ipa:'ə',category:'short',lexical:'COMMA',word:'about',example:'/əˈbaʊt/',tip:'A relaxed mid-central vowel in an unstressed syllable.',position:[163,105]},
            {ipa:'iː',category:'long',lexical:'FLEECE',word:'see',example:'/siː/',tip:'High front tongue; spread lips.',position:[232,73]},
            {ipa:'ɑː',category:'long',lexical:'PALM',word:'calm',example:'/kɑːm/',tip:'Low back tongue; open jaw.',position:[113,126]},
            {ipa:'ɔː',category:'long',lexical:'THOUGHT',word:'thought',example:'/θɔːt/',tip:'Mid-low back tongue with rounded lips.',position:[116,103]},
            {ipa:'uː',category:'long',lexical:'GOOSE',word:'food',example:'/fuːd/',tip:'High back tongue with rounded lips.',position:[109,72]},
            {ipa:'ɜː',category:'long',lexical:'NURSE',word:'bird',example:'/bɜːd/',tip:'Long central vowel; no /r/ after the vowel in this reference accent.',position:[164,93]},
            {ipa:'eɪ',category:'diphthong',lexical:'FACE',word:'day',example:'/deɪ/',tip:'Glide from mid-front to high-front.',position:[218,103],glide:[233,75]},
            {ipa:'aɪ',category:'diphthong',lexical:'PRICE',word:'my',example:'/maɪ/',tip:'Glide from open to high-front.',position:[218,124],glide:[233,75]},
            {ipa:'ɔɪ',category:'diphthong',lexical:'CHOICE',word:'boy',example:'/bɔɪ/',tip:'Glide from rounded back to high-front.',position:[115,103],glide:[233,75]},
            {ipa:'aʊ',category:'diphthong',lexical:'MOUTH',word:'now',example:'/naʊ/',tip:'Glide from open to high-back; lips round at the end.',position:[218,124],glide:[109,74]},
            {ipa:'əʊ',category:'diphthong',lexical:'GOAT',word:'go',example:'/ɡəʊ/',tip:'Glide from central-mid to high-back.',position:[164,105],glide:[109,74]},
            {ipa:'ɪə',category:'diphthong',lexical:'NEAR',word:'near',example:'/nɪə/',tip:'Glide from near-high front to central; often varies by speaker.',position:[231,87],glide:[164,105]},
            {ipa:'eə',category:'diphthong',lexical:'SQUARE',word:'hair',example:'/heə/',tip:'Glide from mid-front toward central.',position:[218,103],glide:[164,105]},
            {ipa:'ʊə',category:'diphthong',lexical:'CURE',word:'tour',example:'/tʊə/',tip:'A variable centring glide; some speakers use a simpler vowel.',position:[109,88],glide:[164,105]}
        ]
    },
    'en-US': {
        description: 'American English · General American reference',
        note: 'American varieties do not use vowel length in the same way as British /ɒ/–/ɑː/. “Long” groups tense vowels for learner comparison; accents vary.',
        sounds: [
            {ipa:'ɪ',category:'short',lexical:'KIT',word:'sit',example:'/sɪt/',tip:'Relaxed, near-high front vowel.',position:[224,91]},
            {ipa:'ɛ',category:'short',lexical:'DRESS',word:'set',example:'/sɛt/',tip:'Mid-front tongue; lips stay unrounded.',position:[220,103]},
            {ipa:'æ',category:'short',lexical:'TRAP',word:'cat',example:'/kæt/',tip:'Low front tongue with an open jaw.',position:[222,120]},
            {ipa:'ʌ',category:'short',lexical:'STRUT',word:'cup',example:'/kʌp/',tip:'Open-mid central tongue position.',position:[164,112]},
            {ipa:'ɑ',category:'short',lexical:'LOT',word:'hot',example:'/hɑt/',tip:'Low back vowel; the LOT vowel may merge with PALM.',position:[112,121]},
            {ipa:'ʊ',category:'short',lexical:'FOOT',word:'put',example:'/pʊt/',tip:'Near-high back tongue; lightly rounded.',position:[114,91]},
            {ipa:'ə',category:'short',lexical:'COMMA',word:'about',example:'/əˈbaʊt/',tip:'A relaxed mid-central vowel in an unstressed syllable.',position:[163,105]},
            {ipa:'i',category:'long',lexical:'FLEECE',word:'see',example:'/si/',tip:'Tense high-front vowel; duration depends on context.',position:[232,73]},
            {ipa:'ɑ',category:'long',lexical:'PALM',word:'father',example:'/ˈfɑðɚ/',tip:'Low back vowel; not a phonemic long/short pair in General American.',position:[113,126]},
            {ipa:'ɔ',category:'long',lexical:'THOUGHT',word:'thought',example:'/θɔt/',tip:'Rounded back vowel; often merged with LOT in some regions.',position:[116,103]},
            {ipa:'u',category:'long',lexical:'GOOSE',word:'food',example:'/fud/',tip:'Tense high-back vowel; duration varies by context.',position:[109,72]},
            {ipa:'ɝ',category:'long',lexical:'NURSE',word:'bird',example:'/bɝd/',tip:'Stressed central rhotic vowel; the tongue bunches or curls back.',position:[164,93]},
            {ipa:'eɪ',category:'diphthong',lexical:'FACE',word:'day',example:'/deɪ/',tip:'Glide from mid-front to high-front.',position:[218,103],glide:[233,75]},
            {ipa:'aɪ',category:'diphthong',lexical:'PRICE',word:'my',example:'/maɪ/',tip:'Glide from open to high-front.',position:[218,124],glide:[233,75]},
            {ipa:'ɔɪ',category:'diphthong',lexical:'CHOICE',word:'boy',example:'/bɔɪ/',tip:'Glide from rounded back to high-front.',position:[115,103],glide:[233,75]},
            {ipa:'aʊ',category:'diphthong',lexical:'MOUTH',word:'now',example:'/naʊ/',tip:'Glide from open to high-back; lips round at the end.',position:[218,124],glide:[109,74]},
            {ipa:'oʊ',category:'diphthong',lexical:'GOAT',word:'go',example:'/ɡoʊ/',tip:'Glide from mid-back to high-back.',position:[115,99],glide:[109,74]}
        ]
    }
};

const consonantSounds = [
    {ipa:'p',voicing:'voiceless',place:'Bilabial · lips',word:'pin',example:'/pɪn/',tip:'Close both lips, then release a small burst of air.',position:[277,130]},
    {ipa:'b',voicing:'voiced',place:'Bilabial · lips',word:'bin',example:'/bɪn/',tip:'Close both lips; let the vocal folds vibrate as you release.',position:[277,130]},
    {ipa:'t',voicing:'voiceless',place:'Alveolar · tongue tip',word:'ten',example:'/tɛn/',tip:'Touch the tongue tip to the ridge just behind the upper teeth, then release.',position:[235,104]},
    {ipa:'d',voicing:'voiced',place:'Alveolar · tongue tip',word:'den',example:'/dɛn/',tip:'Use the same tongue-tip contact as /t/, with vocal-fold vibration.',position:[235,104]},
    {ipa:'k',voicing:'voiceless',place:'Velar · back of tongue',word:'coat',example:'/koʊt/',tip:'Raise the back of the tongue to the soft palate, then release.',position:[116,91]},
    {ipa:'ɡ',voicing:'voiced',place:'Velar · back of tongue',word:'goat',example:'/ɡoʊt/',tip:'Raise the back of the tongue to the soft palate while voicing.',position:[116,91]},
    {ipa:'f',voicing:'voiceless',place:'Labiodental · lip and teeth',word:'fan',example:'/fæn/',tip:'Place the lower lip lightly against the upper front teeth; let air pass.',position:[270,103]},
    {ipa:'v',voicing:'voiced',place:'Labiodental · lip and teeth',word:'van',example:'/væn/',tip:'Use the /f/ lip-and-teeth position and add vocal-fold vibration.',position:[270,103]},
    {ipa:'θ',voicing:'voiceless',place:'Dental · tongue and teeth',word:'thin',example:'/θɪn/',tip:'Place the tongue tip gently between or just behind the teeth and release air.',position:[270,107]},
    {ipa:'ð',voicing:'voiced',place:'Dental · tongue and teeth',word:'this',example:'/ðɪs/',tip:'Use the /θ/ tongue position with vocal-fold vibration.',position:[270,107]},
    {ipa:'s',voicing:'voiceless',place:'Alveolar · tongue tip',word:'sip',example:'/sɪp/',tip:'Bring the tongue close to the alveolar ridge to create a narrow stream of air.',position:[237,101]},
    {ipa:'z',voicing:'voiced',place:'Alveolar · tongue tip',word:'zip',example:'/zɪp/',tip:'Use the /s/ tongue position and add vocal-fold vibration.',position:[237,101]},
    {ipa:'ʃ',voicing:'voiceless',place:'Postalveolar · tongue blade',word:'ship',example:'/ʃɪp/',tip:'Raise the tongue blade slightly behind the alveolar ridge and round the lips a little.',position:[211,99]},
    {ipa:'ʒ',voicing:'voiced',place:'Postalveolar · tongue blade',word:'vision',example:'/ˈvɪʒən/',tip:'Use the /ʃ/ tongue position with vocal-fold vibration.',position:[211,99]},
    {ipa:'h',voicing:'voiceless',place:'Glottal · vocal folds',word:'hat',example:'/hæt/',tip:'Let air pass through the open glottis; the tongue anticipates the following vowel.',position:[164,112]},
    {ipa:'tʃ',voicing:'voiceless',place:'Postalveolar · affricate',word:'chip',example:'/tʃɪp/',tip:'Begin with a tongue closure behind the ridge, then release into /ʃ/.',position:[211,99]},
    {ipa:'dʒ',voicing:'voiced',place:'Postalveolar · affricate',word:'jam',example:'/dʒæm/',tip:'Begin with a voiced closure behind the ridge, then release into /ʒ/.',position:[211,99]},
    {ipa:'m',voicing:'voiced',place:'Bilabial · nasal',word:'map',example:'/mæp/',tip:'Close both lips and let air flow through the nose.',position:[277,130]},
    {ipa:'n',voicing:'voiced',place:'Alveolar · nasal',word:'nap',example:'/næp/',tip:'Touch the tongue tip to the alveolar ridge while air flows through the nose.',position:[235,104]},
    {ipa:'ŋ',voicing:'voiced',place:'Velar · nasal',word:'sing',example:'/sɪŋ/',tip:'Raise the back of the tongue to the soft palate and release air through the nose.',position:[116,91]},
    {ipa:'l',voicing:'voiced',place:'Alveolar · lateral',word:'light',example:'/laɪt/',tip:'Touch the tongue tip to the ridge; let air flow around the sides of the tongue.',position:[235,104]},
    {ipa:'ɹ',voicing:'voiced',place:'Postalveolar · approximant',word:'red',example:'/ɹɛd/',tip:'Raise or bunch the tongue toward the area behind the ridge without making contact.',position:[209,94]},
    {ipa:'j',voicing:'voiced',place:'Palatal · approximant',word:'yes',example:'/jɛs/',tip:'Raise the middle of the tongue toward the hard palate; glide into the vowel.',position:[180,75]},
    {ipa:'w',voicing:'voiced',place:'Labial-velar · approximant',word:'wet',example:'/wɛt/',tip:'Round the lips while raising the back of the tongue toward the soft palate.',position:[116,82]}
];

let currentAccent = localStorage.getItem('nizarphonetics-accent') || 'en-GB';
let currentFilter = 'all';
let soundMode = 'all';
let currentSound = null;
let ipaText = '';
let timer;
let controller;
let activeUtterance = null;

function visibleSounds() {
    const vowels = soundSets[currentAccent].sounds;
    const sounds = soundMode === 'vowels' ? vowels
        : soundMode === 'consonants' ? consonantSounds
            : [...vowels, ...consonantSounds];
    return sounds.filter(sound => {
        if (currentFilter === 'all') return true;
        if (currentFilter === 'vowels') return !sound.voicing;
        if (currentFilter === 'consonants') return Boolean(sound.voicing);
        return (sound.category || sound.voicing) === currentFilter;
    });
}

function tonguePath(position) {
    const [x, y] = position;
    return `M48 130 C78 116 ${x - 55} ${y + 14} ${x} ${y} C${x + 38} ${y + 5} 242 119 278 124 L278 139 C213 146 99 145 48 130Z`;
}

function selectSound(sound) {
    currentSound = sound;
    articulationTitle.textContent = `/${sound.ipa}/ · ${sound.lexical}`;
    articulationNote.textContent = sound.tip;
    articulationStatus.textContent = sound.voicing
        ? `${sound.voicing === 'voiced' ? 'VOICED · vocal folds vibrate' : 'VOICELESS · no vocal-fold vibration'} · ${sound.place}`
        : sound.glide ? 'VOWEL GLIDE · tongue moves between positions' : 'VOWEL · tongue position';
    articulationStatus.classList.toggle('is-voiced', sound.voicing === 'voiced');
    articulationStatus.classList.toggle('is-voiceless', sound.voicing === 'voiceless');
    startCaption.textContent = sound.glide ? 'Starting tongue position' : sound.voicing ? sound.place : 'Tongue position';
    tongueStart.setAttribute('d', tonguePath(sound.position));
    endDiagram.hidden = !sound.glide;
    if (sound.glide) tongueEnd.setAttribute('d', tonguePath(sound.glide));
    soundGrid.querySelectorAll('.sound-card').forEach(card => {
        card.classList.toggle('is-selected', card.dataset.sound === sound.ipa && card.dataset.word === sound.word);
    });
}

function speak(text, accent = currentAccent) {
    if (!('speechSynthesis' in window)) {
        speechNote.textContent = 'Speech playback is not available in this browser.';
        return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = accent;
    utterance.volume = Number(volumeSlider.value) / 100;
    activeUtterance = utterance;
    const voice = window.speechSynthesis.getVoices().find(item => item.lang.toLowerCase() === accent.toLowerCase());
    if (voice) utterance.voice = voice;
    utterance.onend = () => {
        activeUtterance = null;
        speechNote.textContent = '';
    };
    speechNote.textContent = `Speaking in ${accent === 'en-GB' ? 'British' : 'American'} English.`;
    window.speechSynthesis.speak(utterance);
}

function renderSounds() {
    const sounds = visibleSounds();
    const filters = soundMode === 'all'
        ? [['all', 'All sounds'], ['vowels', 'Vowels'], ['consonants', 'Consonants'], ['short', 'Short'], ['long', 'Long'], ['diphthong', 'Diphthongs'], ['voiceless', 'Voiceless'], ['voiced', 'Voiced']]
        : soundMode === 'vowels'
        ? [['all', 'All vowels'], ['short', 'Short'], ['long', 'Long'], ['diphthong', 'Diphthongs']]
        : [['all', 'All consonants'], ['voiceless', 'Voiceless'], ['voiced', 'Voiced']];
    soundFilters.setAttribute('aria-label', soundMode === 'all' ? 'Filter all English sounds' : soundMode === 'vowels' ? 'Filter vowel types' : 'Filter consonant voicing');
    soundFilters.innerHTML = filters.map(([filter, label]) => `<button type="button" class="sound-filter${currentFilter === filter ? ' is-active' : ''}" data-filter="${filter}" aria-pressed="${currentFilter === filter}">${label}</button>`).join('');
    soundFilters.querySelectorAll('.sound-filter').forEach(button => {
        button.addEventListener('click', () => {
            currentFilter = button.dataset.filter;
            renderSounds();
        });
    });
    soundLibraryTitle.textContent = soundMode === 'all' ? 'English sound inventory'
        : soundMode === 'vowels' ? 'Vowel sound map' : 'Consonant sound map';
    const vowelCount = soundSets[currentAccent].sounds.length;
    accentDescription.textContent = `${soundSets[currentAccent].description} · ${vowelCount + consonantSounds.length} sounds (${vowelCount} vowels, ${consonantSounds.length} consonants)`;
    soundLegend.setAttribute('aria-label', soundMode === 'all' ? 'Vowel and consonant categories' : soundMode === 'vowels' ? 'Vowel categories' : 'Voicing categories');
    soundLegend.innerHTML = soundMode === 'all'
        ? '<span class="legend-short">Short vowels</span><span class="legend-long">Long vowels</span><span class="legend-diphthong">Diphthongs</span><span class="legend-voiceless">Voiceless</span><span class="legend-voiced">Voiced</span>'
        : soundMode === 'vowels'
            ? '<span class="legend-short">Short vowels</span><span class="legend-long">Long vowels</span><span class="legend-diphthong">Diphthongs</span>'
            : '<span class="legend-voiceless">Voiceless · no vibration</span><span class="legend-voiced">Voiced · vibration</span>';
    const consonantNote = currentAccent === 'en-GB'
        ? 'Most consonants are shared across accents. British English usually has no /r/ after a vowel; /t/ in “water” is typically not a flap.'
        : 'Most consonants are shared across accents. General American pronounces /r/ in “car”; /t/ in “water” may become a voiced flap /ɾ/.';
    accentNote.textContent = soundMode === 'all'
        ? `${soundSets[currentAccent].note} ${consonantNote}`
        : soundMode === 'vowels' ? soundSets[currentAccent].note : consonantNote;
    soundGrid.replaceChildren();
    sounds.forEach(sound => {
        const card = document.createElement('article');
        card.className = `sound-card sound-${sound.category || 'consonant'}${sound.voicing ? ` sound-${sound.voicing}` : ''}`;
        card.dataset.sound = sound.ipa;
        card.dataset.word = sound.word;
        const categoryLabel = sound.voicing
            ? `${sound.voicing.toUpperCase()} CONSONANT`
            : sound.category === 'diphthong' ? 'DIPHTHONG' : `${sound.category.toUpperCase()} VOWEL`;
        card.innerHTML = `<button type="button" class="sound-select" aria-label="Select ${sound.lexical || sound.place}, ${sound.word}"><span class="sound-kind">${categoryLabel}</span><strong class="sound-ipa">/${sound.ipa}/</strong><span class="sound-lexical">${sound.lexical || sound.place}</span><span class="sound-example">${sound.word}</span><span class="sound-example-ipa">${sound.example}</span></button><button type="button" class="sample-play" aria-label="Listen to ${sound.word}">▶</button>`;
        card.querySelector('.sound-select').addEventListener('click', () => selectSound(sound));
        card.querySelector('.sample-play').addEventListener('click', () => {
            selectSound(sound);
            speak(sound.word);
            speechNote.textContent = `${sound.word} · ${currentAccent === 'en-GB' ? 'British' : 'American'} English`;
        });
        soundGrid.append(card);
    });
    if (currentSound && !sounds.includes(currentSound)) selectSound(sounds[0]);
    else if (!currentSound && sounds[0]) selectSound(sounds[0]);
}

function setAccent(accent) {
    currentAccent = accent;
    localStorage.setItem('nizarphonetics-accent', accent);
    document.querySelectorAll('.accent-tab').forEach(button => {
        const active = button.dataset.accent === accent;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-pressed', String(active));
    });
    accentDescription.textContent = soundSets[accent].description;
    accentNote.textContent = soundSets[accent].note;
    currentSound = null;
    renderSounds();
    if (input.value.trim()) scheduleTranscription();
}

async function processPhonetics() {
    const text = input.value.trim();
    if (!text) {
        result.textContent = 'Your phonetic transcription will appear here.';
        ipaText = '';
        listenButton.disabled = true;
        downloadButton.disabled = true;
        copyButton.disabled = true;
        return;
    }
    if (controller) controller.abort();
    controller = new AbortController();
    const currentController = controller;
    result.textContent = 'Preparing phonetic transcription...';
    try {
        const response = await fetch('/phonetics_process', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, accent: currentAccent}),
            signal: currentController.signal
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Unable to prepare phonetic transcription.');
        if (controller === currentController) {
            ipaText = data.ipa;
            result.textContent = ipaText;
            listenButton.disabled = false;
            downloadButton.disabled = false;
            copyButton.disabled = false;
        }
    } catch (error) {
        if (error.name !== 'AbortError' && controller === currentController) {
            result.textContent = error.message;
            ipaText = '';
            listenButton.disabled = true;
            downloadButton.disabled = true;
            copyButton.disabled = true;
        }
    }
}

function scheduleTranscription() {
    clearTimeout(timer);
    if (controller) controller.abort();
    listenButton.disabled = true;
    downloadButton.disabled = true;
    copyButton.disabled = true;
    timer = setTimeout(processPhonetics, 350);
}

document.querySelectorAll('.accent-tab').forEach(button => {
    button.addEventListener('click', () => setAccent(button.dataset.accent));
});
document.querySelectorAll('.sound-filter').forEach(button => {
    button.addEventListener('click', () => {
        currentFilter = button.dataset.filter;
        document.querySelectorAll('.sound-filter').forEach(filter => {
            const active = filter === button;
            filter.classList.toggle('is-active', active);
            filter.setAttribute('aria-pressed', String(active));
        });
        renderSounds();
    });
});
document.querySelectorAll('.sound-mode').forEach(button => {
    button.addEventListener('click', () => {
        soundMode = button.dataset.soundMode;
        currentFilter = 'all';
        document.querySelectorAll('.sound-mode').forEach(modeButton => {
            const active = modeButton === button;
            modeButton.classList.toggle('is-active', active);
            modeButton.setAttribute('aria-pressed', String(active));
        });
        currentSound = null;
        renderSounds();
    });
});

input.addEventListener('input', scheduleTranscription);
listenButton.addEventListener('click', () => speak(input.value.trim()));
volumeSlider.addEventListener('input', () => {
    volumeValue.value = `${volumeSlider.value}%`;
    volumeValue.textContent = `${volumeSlider.value}%`;
    if (activeUtterance) activeUtterance.volume = Number(volumeSlider.value) / 100;
});
copyButton.addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(ipaText);
        speechNote.textContent = 'IPA copied to clipboard.';
    } catch {
        speechNote.textContent = 'Clipboard access is unavailable in this browser.';
    }
});
downloadButton.addEventListener('click', async () => {
    downloadButton.disabled = true;
    speechNote.textContent = 'Generating your MP3...';
    try {
        const response = await fetch('/speech_download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: input.value.trim(), accent: currentAccent, volume: Number(volumeSlider.value)})
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Unable to generate your audio file.');
        }
        const audioUrl = URL.createObjectURL(await response.blob());
        const link = document.createElement('a');
        link.href = audioUrl;
        link.download = `pronunciation-${currentAccent}.mp3`;
        document.body.append(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(audioUrl), 1000);
        speechNote.textContent = 'MP3 downloaded.';
    } catch (error) {
        speechNote.textContent = error.message;
    } finally {
        downloadButton.disabled = !input.value.trim();
    }
});

setAccent(currentAccent in soundSets ? currentAccent : 'en-GB');