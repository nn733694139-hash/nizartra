(() => {
    const places = {
        bilabial: {en: 'Bilabial', ar: 'شفوي ثنائي', x: 385, y: 151, action: 'Both lips meet or narrow together.', actionAr: 'تلتقي الشفتان أو تتقاربان معاً.'},
        labiodental: {en: 'Labiodental', ar: 'شفوي أسناني', x: 367, y: 146, action: 'The lower lip approaches the upper front teeth.', actionAr: 'تقترب الشفة السفلى من الأسنان الأمامية العليا.'},
        dental: {en: 'Dental', ar: 'أسناني', x: 350, y: 141, action: 'The tongue tip touches or approaches the teeth.', actionAr: 'يلامس طرف اللسان الأسنان أو يقترب منها.'},
        alveolar: {en: 'Alveolar', ar: 'لثوي', x: 333, y: 137, action: 'The tongue tip or blade approaches the ridge behind the upper teeth.', actionAr: 'يقترب طرف اللسان أو نصله من الحافة خلف الأسنان العليا.'},
        postalveolar: {en: 'Postalveolar', ar: 'خلف لثوي', x: 307, y: 131, action: 'The tongue blade approaches the area just behind the alveolar ridge.', actionAr: 'يقترب نصل اللسان من المنطقة الواقعة خلف الحافة السنخية.'},
        palatal: {en: 'Palatal', ar: 'حنكي', x: 276, y: 120, action: 'The middle of the tongue approaches the hard palate.', actionAr: 'يقترب وسط اللسان من الحنك الصلب.'},
        velar: {en: 'Velar', ar: 'طبقي', x: 241, y: 116, action: 'The back of the tongue approaches the soft palate.', actionAr: 'يقترب مؤخر اللسان من الحنك اللين.'},
        glottal: {en: 'Glottal', ar: 'حنجري', x: 169, y: 199, action: 'The sound is shaped at the vocal folds or open glottis.', actionAr: 'يتشكل الصوت عند الطيتين الصوتيتين أو المزمار المفتوح.'},
        labialVelar: {en: 'Labial-velar', ar: 'شفوي طبقي', x: 242, y: 116, action: 'The lips round as the back of the tongue rises.', actionAr: 'تستدير الشفتان بالتزامن مع ارتفاع مؤخر اللسان.'}
    };
    const manners = {
        stop: {en: 'Stop (plosive)', ar: 'وقفي (انفجاري)', action: 'A complete closure builds air pressure, then releases it.', actionAr: 'يُغلق الممر كلياً فيتجمع ضغط الهواء ثم ينطلق.'},
        fricative: {en: 'Fricative', ar: 'احتكاكي', action: 'A narrow opening makes the outgoing air turbulent.', actionAr: 'يُحدث التضييق اضطراباً واحتكاكاً في الهواء الخارج.'},
        affricate: {en: 'Affricate', ar: 'مركب (وقفي احتكاكي)', action: 'A full closure releases into a narrow fricative opening.', actionAr: 'ينفك الإغلاق التام تدريجياً إلى تضييق احتكاكي.'},
        nasal: {en: 'Nasal', ar: 'أنفي', action: 'The oral passage closes while the lowered velum lets air pass through the nose.', actionAr: 'يُغلق الممر الفموي ويهبط الطبق ليسمح بخروج الهواء عبر الأنف.'},
        lateral: {en: 'Lateral approximant', ar: 'تقريبي جانبي', action: 'The tongue makes a central contact while air flows around one or both sides.', actionAr: 'يلامس اللسان في الوسط ويمر الهواء من أحد جانبيه أو كليهما.'},
        approximant: {en: 'Approximant', ar: 'تقريبي', action: 'The articulators approach without making the turbulent friction of a fricative.', actionAr: 'تقترب أعضاء النطق دون إحداث احتكاك مضطرب كالصوت الاحتكاكي.'}
    };
    const consonants = [
        ['p','pin','bilabial','stop',false], ['b','bin','bilabial','stop',true],
        ['t','ten','alveolar','stop',false], ['d','den','alveolar','stop',true],
        ['k','coat','velar','stop',false], ['ɡ','goat','velar','stop',true],
        ['f','fan','labiodental','fricative',false], ['v','van','labiodental','fricative',true],
        ['θ','thin','dental','fricative',false], ['ð','this','dental','fricative',true],
        ['s','sip','alveolar','fricative',false], ['z','zip','alveolar','fricative',true],
        ['ʃ','ship','postalveolar','fricative',false], ['ʒ','vision','postalveolar','fricative',true],
        ['h','hat','glottal','fricative',false],
        ['tʃ','chip','postalveolar','affricate',false], ['dʒ','jam','postalveolar','affricate',true],
        ['m','map','bilabial','nasal',true], ['n','nap','alveolar','nasal',true], ['ŋ','sing','velar','nasal',true],
        ['l','light','alveolar','lateral',true], ['ɹ','red','postalveolar','approximant',true],
        ['j','yes','palatal','approximant',true], ['w','wet','labialVelar','approximant',true]
    ].map(([ipa, example, place, manner, voiced]) => ({type: 'consonant', ipa, example, place, manner, voiced, nasal: manner === 'nasal'}));

    const vowels = [
        {ipa:'ɪ', example:'bit', height:'nearClose', backness:'front', rounded:false, start:[326,126]},
        {ipa:'e', example:'bed', height:'closeMid', backness:'front', rounded:false, start:[311,143]},
        {ipa:'æ', example:'cat', height:'nearOpen', backness:'front', rounded:false, start:[318,169]},
        {ipa:'ʌ', example:'cup', height:'openMid', backness:'central', rounded:false, start:[260,158]},
        {ipa:'ɒ', example:'hot', height:'open', backness:'back', rounded:true, start:[205,177]},
        {ipa:'ʊ', example:'put', height:'nearClose', backness:'nearBack', rounded:true, start:[220,126]},
        {ipa:'ə', example:'about', height:'mid', backness:'central', rounded:false, start:[260,146]},
        {ipa:'iː', example:'see', height:'close', backness:'front', rounded:false, start:[326,113]},
        {ipa:'ɑː', example:'calm', height:'open', backness:'back', rounded:false, start:[205,177]},
        {ipa:'ɔː', example:'thought', height:'openMid', backness:'back', rounded:true, start:[205,158]},
        {ipa:'uː', example:'food', height:'close', backness:'back', rounded:true, start:[205,113]},
        {ipa:'ɜː', example:'bird', height:'mid', backness:'central', rounded:false, start:[260,146]},
        {ipa:'eɪ', example:'day', height:'closeMid', backness:'front', rounded:false, start:[311,143], end:[326,113]},
        {ipa:'aɪ', example:'my', height:'open', backness:'front', rounded:false, start:[318,177], end:[326,113]},
        {ipa:'ɔɪ', example:'boy', height:'openMid', backness:'back', rounded:true, start:[205,158], end:[326,126]},
        {ipa:'aʊ', example:'now', height:'open', backness:'front', rounded:false, start:[318,177], end:[220,126]},
        {ipa:'əʊ', example:'go', height:'mid', backness:'central', rounded:false, start:[260,146], end:[205,113]},
        {ipa:'ɪə', example:'near', height:'nearClose', backness:'front', rounded:false, start:[326,126], end:[260,146]},
        {ipa:'eə', example:'hair', height:'closeMid', backness:'front', rounded:false, start:[311,143], end:[260,146]},
        {ipa:'ʊə', example:'tour', height:'nearClose', backness:'nearBack', rounded:true, start:[220,126], end:[260,146]}
    ].map(vowel => ({
        ...vowel,
        type: vowel.end ? 'diphthong' : 'monophthong',
        duration: vowel.end ? 'diphthong' : vowel.ipa.includes('ː') ? 'long' : 'short'
    }));

    const heightLabels = {
        close: ['Close (high)', 'مغلقة (عالية)'], nearClose: ['Near-close', 'شبه مغلقة'], closeMid: ['Close-mid', 'نصف مغلقة'],
        mid: ['Mid', 'متوسطة'], openMid: ['Open-mid', 'نصف مفتوحة'], nearOpen: ['Near-open', 'شبه مفتوحة'], open: ['Open (low)', 'مفتوحة (منخفضة)']
    };
    const backnessLabels = {
        front: ['Front', 'أمامية'], nearFront: ['Near-front', 'شبه أمامية'], central: ['Central', 'مركزية'], nearBack: ['Near-back', 'شبه خلفية'], back: ['Back', 'خلفية']
    };
    const mannerLabel = manner => manners[manner][document.documentElement.lang === 'ar' ? 'ar' : 'en'];
    const placeLabel = place => places[place][document.documentElement.lang === 'ar' ? 'ar' : 'en'];
    const isArabic = () => document.documentElement.lang === 'ar';
    const grid = document.getElementById('inventorySoundGrid');
    const title = document.getElementById('inventorySoundTitle');
    const example = document.getElementById('inventorySoundExample');
    const explanation = document.getElementById('inventorySoundExplanation');
    const properties = document.getElementById('inventoryProperties');
    const diagram = document.querySelector('.inventory-diagram');
    const flowPath = document.getElementById('inventoryFlowPath');
    const placeMarker = document.getElementById('inventoryPlaceMarker');
    const tongueMarker = document.getElementById('inventoryTongueMarker');
    const glidePath = document.getElementById('inventoryGlidePath');
    const glideMotion = document.getElementById('inventoryGlideMotion');
    let activeFilter = 'all';
    let selectedSound = null;

    function visibleSounds() {
        return [...consonants, ...vowels].filter(sound => activeFilter === 'all' || sound.type === activeFilter);
    }

    function describeSound(sound) {
        if (sound.type === 'consonant') {
            const place = places[sound.place];
            const manner = manners[sound.manner];
            if (isArabic()) {
                return `الصوت /${sound.ipa}/ في “${sound.example}” ${sound.voiced ? 'مجهور' : 'مهموس'} ${manner.ar}، ${place.ar}. ${place.actionAr} ${manner.actionAr}`;
            }
            return `/${sound.ipa}/ in “${sound.example}” is a ${sound.voiced ? 'voiced' : 'voiceless'} ${manner.en.toLowerCase()} at the ${place.en} place. ${place.action} ${manner.action}`;
        }
        const height = heightLabels[sound.height][isArabic() ? 1 : 0];
        const backness = backnessLabels[sound.backness][isArabic() ? 1 : 0];
        const lips = isArabic() ? (sound.rounded ? 'الشفتان مستديرتان.' : 'الشفتان غير مستديرتين.') : (sound.rounded ? 'The lips are rounded.' : 'The lips are unrounded.');
        if (sound.type === 'diphthong') {
            return isArabic()
                ? `الحركة المزدوجة /${sound.ipa}/ في “${sound.example}” تبدأ من موضع ${height} ${backness} ثم تنزلق إلى موضع آخر. ${lips}`
                : `The diphthong /${sound.ipa}/ in “${sound.example}” starts at a ${height.toLowerCase()} ${backness.toLowerCase()} position and glides to a new tongue target. ${lips}`;
        }
        return isArabic()
            ? `الحركة /${sound.ipa}/ في “${sound.example}” ${height} ${backness} و${sound.duration === 'long' ? 'طويلة' : 'قصيرة'}. ${lips} الحركات مجهورة عادةً، ويمر الهواء من الفم من دون إغلاق كامل.`
            : `The vowel /${sound.ipa}/ in “${sound.example}” is ${height.toLowerCase()} and ${backness.toLowerCase()}, and ${sound.duration} in this reference transcription. Vowels are normally voiced. ${lips} Air passes through the open oral tract.`;
    }

    function featureRows(sound) {
        const rows = sound.type === 'consonant'
            ? [
                [isArabic() ? 'موضع النطق' : 'Place', placeLabel(sound.place)],
                [isArabic() ? 'طريقة النطق' : 'Manner', mannerLabel(sound.manner)],
                [isArabic() ? 'الجهر' : 'Voicing', isArabic() ? (sound.voiced ? 'مجهور · اهتزاز الطيتين' : 'مهموس · دون اهتزاز الطيتين') : (sound.voiced ? 'Voiced · folds vibrate' : 'Voiceless · no fold vibration')],
                [isArabic() ? 'الممر' : 'Air route', isArabic() ? (sound.nasal ? 'أنفي' : 'فموي') : (sound.nasal ? 'Nasal' : 'Oral')]
            ]
            : [
                [isArabic() ? 'ارتفاع اللسان' : 'Tongue height', heightLabels[sound.height][isArabic() ? 1 : 0]],
                [isArabic() ? 'مقدمة اللسان' : 'Tongue position', backnessLabels[sound.backness][isArabic() ? 1 : 0]],
                [isArabic() ? 'استدارة الشفتين' : 'Lip shape', isArabic() ? (sound.rounded ? 'مستديرتان' : 'غير مستديرتين') : (sound.rounded ? 'Rounded' : 'Unrounded')],
                [isArabic() ? 'الجهر' : 'Voicing', isArabic() ? 'مجهورة عادةً · اهتزاز الطيتين' : 'Normally voiced · folds vibrate'],
                [isArabic() ? 'المدة/النوع' : 'Length/type', isArabic() ? ({short:'قصيرة', long:'طويلة', diphthong:'مزدوجة'})[sound.duration] : ({short:'Short', long:'Long', diphthong:'Diphthong'})[sound.duration]],
                [isArabic() ? 'حركة اللسان' : 'Tongue movement', isArabic() ? (sound.end ? 'انزلاق بين موضعين' : 'موضع ثابت تقريباً') : (sound.end ? 'Glide between two targets' : 'Relatively steady target')]
            ];
        return rows;
    }

    function renderSelected(sound) {
        selectedSound = sound;
        title.textContent = `/${sound.ipa}/`;
        example.textContent = isArabic() ? `مثال: ${sound.example}` : `Example: ${sound.example}`;
        explanation.textContent = describeSound(sound);
        properties.replaceChildren(...featureRows(sound).flatMap(([label, value]) => {
            const term = document.createElement('dt');
            term.textContent = label;
            const detail = document.createElement('dd');
            detail.textContent = value;
            return [term, detail];
        }));
        grid.querySelectorAll('.inventory-sound').forEach(button => {
            const active = button.dataset.ipa === sound.ipa;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
        });
        diagram.classList.toggle('is-consonant', sound.type === 'consonant');
        diagram.classList.toggle('is-nasal', Boolean(sound.nasal));
        diagram.classList.toggle('is-voiced', Boolean(sound.voiced));

        if (sound.type === 'consonant') {
            const place = places[sound.place];
            placeMarker.setAttribute('cx', place.x);
            placeMarker.setAttribute('cy', place.y);
            placeMarker.classList.remove('is-hidden');
            tongueMarker.classList.add('is-hidden');
            glidePath.setAttribute('d', `M${place.x} ${place.y} L${place.x} ${place.y}`);
            flowPath.setAttribute('d', sound.nasal
                ? 'M124 217 C143 205 153 187 165 175 C188 151 214 138 241 130 C288 120 334 105 371 106'
                : 'M124 217 C143 205 153 187 165 175 C188 151 222 144 261 145 C309 145 351 150 386 154');
        } else {
            placeMarker.classList.add('is-hidden');
            tongueMarker.classList.remove('is-hidden');
            tongueMarker.setAttribute('cx', sound.start[0]);
            tongueMarker.setAttribute('cy', sound.start[1]);
            if (sound.end) {
                glidePath.setAttribute('d', `M${sound.start[0]} ${sound.start[1]} Q${(sound.start[0] + sound.end[0]) / 2 - 20} ${(sound.start[1] + sound.end[1]) / 2} ${sound.end[0]} ${sound.end[1]}`);
                diagram.classList.add('is-gliding');
                if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) glideMotion.beginElement();
            } else {
                diagram.classList.remove('is-gliding');
                glidePath.setAttribute('d', `M${sound.start[0]} ${sound.start[1]} L${sound.start[0]} ${sound.start[1]}`);
            }
        }
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const flowMotion = document.getElementById('inventoryFlowMotion');
        if (!reducedMotion) flowMotion?.beginElement();
    }

    function renderGrid() {
        const sounds = visibleSounds();
        grid.replaceChildren(...sounds.map(sound => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'inventory-sound';
            button.dataset.ipa = sound.ipa;
            button.setAttribute('aria-pressed', 'false');
            const symbol = document.createElement('strong');
            symbol.textContent = `/${sound.ipa}/`;
            const sample = document.createElement('span');
            sample.textContent = sound.example;
            const category = document.createElement('small');
            category.textContent = sound.type === 'consonant'
                ? mannerLabel(sound.manner)
                : isArabic()
                    ? ({short:'حركة قصيرة', long:'حركة طويلة', diphthong:'مزدوجة'})[sound.duration]
                    : ({short:'SHORT VOWEL', long:'LONG VOWEL', diphthong:'DIPHTHONG'})[sound.duration];
            button.append(symbol, sample, category);
            button.addEventListener('click', () => renderSelected(sound));
            return button;
        }));
        if (!selectedSound || !sounds.some(sound => sound.ipa === selectedSound.ipa)) {
            renderSelected(sounds[0]);
        } else {
            renderSelected(selectedSound);
        }
    }

    document.querySelectorAll('.inventory-filter').forEach(button => {
        button.addEventListener('click', () => {
            activeFilter = button.dataset.inventoryFilter;
            document.querySelectorAll('.inventory-filter').forEach(filter => {
                const active = filter === button;
                filter.classList.toggle('is-active', active);
                filter.setAttribute('aria-pressed', String(active));
            });
            renderGrid();
        });
    });

    document.addEventListener('site-language-changed', renderGrid);
    renderGrid();
})();