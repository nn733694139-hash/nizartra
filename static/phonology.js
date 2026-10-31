(() => {
    const terms = [
        {id: 'diaphragm', group: 'respiratory', organ: 'diaphragm', name: 'Diaphragm', definition: 'The diaphragm contracts during inhalation. During speech, coordinated respiratory muscles help maintain the outward airflow needed for most English sounds.', role: 'Breathing and airflow support', stage: '1 · Airstream'},
        {id: 'lungs', group: 'respiratory', organ: 'lungs', name: 'Lungs', definition: 'The usual power source for English speech. Air pushed outward from the lungs sets the pulmonic egressive airstream in motion.', role: 'Pulmonic egressive airstream', stage: '1 · Airstream'},
        {id: 'ribCage', group: 'respiratory', organ: 'rib-cage', name: 'Rib cage', definition: 'The rib cage surrounds and protects the lungs. Intercostal muscles between the ribs help control breathing and the airflow used for speech.', role: 'Respiratory support and protection', stage: '1 · Airstream'},
        {id: 'bronchi', group: 'respiratory', organ: 'bronchi', name: 'Bronchi', definition: 'The two main branches carry air from the trachea into and out of the lungs.', role: 'Air passages', stage: '1 · Airstream'},
        {id: 'trachea', group: 'respiratory', organ: 'trachea', name: 'Trachea', definition: 'The windpipe carries air between the lungs and the larynx.', role: 'Air passage', stage: '1 · Airstream'},
        {id: 'larynx', group: 'phonatory', organ: 'larynx', name: 'Larynx', definition: 'The larynx houses the vocal folds and glottis. It regulates airflow and is central to voicing and phonation.', role: 'Voice source and airflow control', stage: '2 · Phonation'},
        {id: 'epiglottis', group: 'phonatory', organ: 'epiglottis', name: 'Epiglottis', definition: 'A flexible flap above the larynx that helps protect the airway during swallowing. It is shown here as an anatomical landmark, not as the main sound source.', role: 'Airway protection', stage: '2 · Laryngeal anatomy'},
        {id: 'thyroidCartilage', group: 'phonatory', organ: 'thyroid-cartilage', name: 'Thyroid cartilage', definition: 'The largest laryngeal cartilage. It forms the front wall of the larynx and protects the vocal folds.', role: 'Laryngeal support and protection', stage: '2 · Laryngeal anatomy'},
        {id: 'cricoidCartilage', group: 'phonatory', organ: 'cricoid-cartilage', name: 'Cricoid cartilage', definition: 'A ring-shaped cartilage at the base of the larynx, connecting it to the trachea and supporting the airway.', role: 'Laryngeal support', stage: '2 · Laryngeal anatomy'},
        {id: 'vocalFolds', group: 'phonatory', organ: 'vocal-folds', name: 'Vocal folds', definition: 'Air from the lungs can set the vocal folds into vibration for voiced sounds such as /z/. For /s/, the folds are apart and do not vibrate.', role: 'Voicing', stage: '2 · Phonation'},
        {id: 'glottis', group: 'phonatory', organ: 'vocal-folds', name: 'Glottis', definition: 'The glottis is the space between the vocal folds. Its opening and closure help shape the airflow; /h/ is produced with an open glottis.', role: 'Glottal airflow', stage: '2 · Phonation'},
        {id: 'pharynx', group: 'resonance', organ: 'pharynx', name: 'Pharynx', definition: 'The cavity above the larynx and behind the mouth and nose. Its shape contributes to vocal-tract resonance.', role: 'Resonance', stage: '3 · Resonance'},
        {id: 'oralCavity', group: 'resonance', organ: 'oral', name: 'Oral cavity', definition: 'The mouth cavity is the main shaping space for most speech sounds. The tongue, palate, teeth and lips change its shape.', role: 'Oral resonance', stage: '3 · Resonance'},
        {id: 'nasal', group: 'resonance', organ: 'nasal', name: 'Nasal cavity', definition: 'When the velum is lowered, air resonates through the nose, as in /m/, /n/ and /ŋ/.', role: 'Nasal resonance', stage: '3 · Resonance'},
        {id: 'velum', group: 'resonance', organ: 'velum', name: 'Velum (soft palate)', definition: 'The velum lifts to close off the nasal passage for most oral sounds and lowers to allow nasal airflow for sounds such as /m/ and /n/.', role: 'Oral–nasal airflow control', stage: '3 · Resonance'},
        {id: 'tongueTip', group: 'articulation', organ: 'tongue-tip', name: 'Tongue tip and blade', definition: 'The tip and blade form contacts or narrowings near the teeth and alveolar ridge, as in /t/, /s/, /ʃ/ and /θ/.', role: 'Active articulator', stage: '4 · Articulation'},
        {id: 'tongueBody', group: 'articulation', organ: 'tongue', name: 'Tongue body and root', definition: 'The front, back and root of the tongue shape the oral cavity and pharynx. Their position distinguishes vowels and contributes to consonants such as /k/ and /j/.', role: 'Active articulator', stage: '4 · Articulation'},
        {id: 'alveolar', group: 'articulation', organ: 'alveolar', name: 'Alveolar ridge', definition: 'The ridge just behind the upper front teeth. The tongue tip or blade approaches it for /t/, /d/, /s/, /z/ and /n/.', role: 'Passive place of articulation', stage: '4 · Articulation'},
        {id: 'teeth', group: 'articulation', organ: 'teeth', name: 'Upper teeth', definition: 'The upper teeth provide a contact surface for dental sounds such as /θ/ and /ð/, and work with the lower lip for /f/ and /v/.', role: 'Passive articulator', stage: '4 · Articulation'},
        {id: 'hardPalate', group: 'articulation', organ: 'palate', name: 'Hard palate', definition: 'The bony, arched front part of the roof of the mouth. The tongue approaches it for palatal sounds such as /j/.', role: 'Passive place of articulation', stage: '4 · Articulation'},
        {id: 'uvula', group: 'articulation', organ: 'uvula', name: 'Uvula', definition: 'The small structure hanging from the back of the soft palate. It is a landmark in the vocal tract and can be an articulator in some languages.', role: 'Articulatory landmark', stage: '4 · Articulation'},
        {id: 'lips', group: 'articulation', organ: 'lips', name: 'Lips', definition: 'The upper and lower lips can close, narrow or round the vocal-tract opening. They shape sounds such as /p/, /b/, /m/ and /w/.', role: 'Active articulators', stage: '4 · Articulation'},
        {id: 'jaw', group: 'articulation', organ: 'jaw', name: 'Lower jaw', definition: 'Jaw movement changes mouth opening and works with the tongue and lips during articulation, especially for vowel height.', role: 'Movable support for articulation', stage: '4 · Articulation'}
    ];
    const arabicTerms = {
        diaphragm: ['الحجاب الحاجز', 'ينقبض الحجاب الحاجز أثناء الشهيق. وأثناء الكلام تساعد عضلات التنفس المنسقة في الحفاظ على تيار الهواء الخارج اللازم لمعظم الأصوات الإنجليزية.', 'دعم التنفس وتيار الهواء', '1 · تيار الهواء'],
        lungs: ['الرئتان', 'مصدر الطاقة المعتاد للكلام الإنجليزي. يدفع الهواء الخارج منهما تيار الهواء الرئوي الزفيري إلى الحركة.', 'تيار هوائي رئوي زفيري', '1 · تيار الهواء'],
        ribCage: ['القفص الصدري', 'يحيط القفص الصدري بالرئتين ويحميهما. وتساعد العضلات بين الأضلاع في تنظيم التنفس وتيار الهواء المستخدم في الكلام.', 'دعم التنفس والحماية', '1 · تيار الهواء'],
        bronchi: ['الشعب الهوائية', 'ينقل الفرعان الرئيسيان الهواء من القصبة الهوائية إلى الرئتين ومنها.', 'ممرات الهواء', '1 · تيار الهواء'],
        trachea: ['القصبة الهوائية', 'تنقل القصبة الهوائية الهواء بين الرئتين والحنجرة.', 'ممر الهواء', '1 · تيار الهواء'],
        larynx: ['الحنجرة', 'تضم الحنجرة الطيتين الصوتيتين والمزمار. وتنظم مرور الهواء وتؤدي دوراً أساسياً في الجهر والتصويت.', 'مصدر الصوت وتنظيم الهواء', '2 · التصويت'],
        epiglottis: ['لسان المزمار', 'لسان مزمار مرن فوق الحنجرة يساعد على حماية مجرى التنفس أثناء البلع. يظهر هنا كعلامة تشريحية وليس كمصدر رئيسي للصوت.', 'حماية مجرى التنفس', '2 · تشريح الحنجرة'],
        thyroidCartilage: ['الغضروف الدرقي', 'أكبر غضاريف الحنجرة. يشكل جدارها الأمامي ويحمي الطيتين الصوتيتين.', 'دعم الحنجرة وحمايتها', '2 · تشريح الحنجرة'],
        cricoidCartilage: ['الغضروف الحلقي', 'غضروف حلقي الشكل في قاعدة الحنجرة، يصلها بالقصبة الهوائية ويدعم مجرى الهواء.', 'دعم الحنجرة', '2 · تشريح الحنجرة'],
        vocalFolds: ['الطيتان الصوتيتان', 'قد يهز الهواء الطيتين الصوتيتين لإنتاج الأصوات المجهورة مثل /z/. وفي /s/ تتباعد الطيتان ولا تهتزان.', 'الجهر', '2 · التصويت'],
        glottis: ['المزمار', 'المزمار هو الفراغ بين الطيتين الصوتيتين. ويسهم اتساعه وإغلاقه في تشكيل تيار الهواء؛ وينتج /h/ بمزمار مفتوح.', 'مرور الهواء عبر المزمار', '2 · التصويت'],
        pharynx: ['البلعوم', 'تجويف يقع فوق الحنجرة وخلف الفم والأنف. يسهم شكله في رنين مجرى الصوت.', 'الرنين', '3 · الرنين'],
        oralCavity: ['التجويف الفموي', 'التجويف الفموي هو مساحة التشكيل الأساسية لمعظم الأصوات. ويغيّر اللسان والحنك والأسنان والشفتان شكله.', 'الرنين الفموي', '3 · الرنين'],
        nasal: ['التجويف الأنفي', 'عندما ينخفض الطبق، يمر الهواء ويرن عبر الأنف في أصوات مثل /m/ و/n/ و/ŋ/.', 'الرنين الأنفي', '3 · الرنين'],
        velum: ['الطبق (الحنك اللين)', 'يرتفع الطبق لإغلاق الممر الأنفي في معظم الأصوات الفموية، وينخفض للسماح بمرور الهواء الأنفي في أصوات مثل /m/ و/n/.', 'تنظيم مسار الهواء الفموي والأنفي', '3 · الرنين'],
        tongueTip: ['طرف اللسان ونصله', 'يلامس طرف اللسان ونصله الأسنان أو الحافة السنخية أو يقتربان منها في أصوات مثل /t/ و/s/ و/ʃ/ و/θ/.', 'عضو نطق فعال', '4 · التشكيل'],
        tongueBody: ['جسم اللسان وجذره', 'يشكل مقدّم اللسان ومؤخرته وجذره التجويف الفموي والبلعوم. وتُميّز أوضاعها الحركات وتشارك في أصوات مثل /k/ و/j/.', 'عضو نطق فعال', '4 · التشكيل'],
        alveolar: ['اللثة (الحافة السنخية)', 'تقع الحافة خلف الأسنان الأمامية العليا مباشرة. يقترب منها طرف اللسان أو نصله في /t/ و/d/ و/s/ و/z/ و/n/.', 'موضع نطق سلبي', '4 · التشكيل'],
        teeth: ['الأسنان العليا', 'توفر الأسنان العليا سطح تماس للأصوات الأسنانية مثل /θ/ و/ð/، وتتعاون مع الشفة السفلى في /f/ و/v/.', 'عضو نطق سلبي', '4 · التشكيل'],
        hardPalate: ['الحنك الصلب', 'الجزء الأمامي العظمي المقوس من سقف الفم. يقترب منه اللسان في الأصوات الحنكية مثل /j/.', 'موضع نطق سلبي', '4 · التشكيل'],
        uvula: ['اللهاة', 'الجزء الصغير المتدلي من مؤخرة الحنك اللين. وهي علامة تشريحية وقد تكون عضو نطق في بعض اللغات.', 'علامة تشريحية للنطق', '4 · التشكيل'],
        lips: ['الشفتان', 'يمكن للشفة العليا والسفلى الإغلاق أو التضييق أو الاستدارة. وتشارك الشفتان في أصوات مثل /p/ و/b/ و/m/ و/w/.', 'أعضاء نطق فعالة', '4 · التشكيل'],
        jaw: ['الفك السفلي', 'يغيّر الفك مدى انفتاح الفم ويعمل مع اللسان والشفتين أثناء النطق، ولا سيما في تحديد ارتفاع الحركات.', 'دعم متحرك للنطق', '4 · التشكيل']
    };
    const groups = ['respiratory', 'phonatory', 'resonance', 'articulation'];
    const groupLabels = {
        respiratory: ['phonology.groupRespiratory', 'Respiratory system'],
        phonatory: ['phonology.groupPhonatory', 'Phonation and voice'],
        resonance: ['phonology.groupResonance', 'Resonating cavities'],
        articulation: ['phonology.groupArticulation', 'Articulators']
    };
    const soundDemos = {
        m: {
            ipa: '/m/', word: 'moon', wordAr: 'moon (قمر)', place: 'Bilabial', placeAr: 'شفويّ', manner: 'Nasal', mannerAr: 'أنفي', voicing: 'Voiced', voicingAr: 'مجهور', route: 'nasal', routeName: 'Through the nose', routeNameAr: 'عبر الأنف', voiced: true,
            description: 'For /m/, both lips close and the velum lowers. The vocal folds vibrate, while air from the lungs resonates through the nose because the oral exit is closed.',
            descriptionAr: 'في /m/ تنغلق الشفتان وينخفض الطبق. تهتز الطيتان الصوتيتان، ويرن الهواء القادم من الرئتين عبر الأنف لأن المخرج الفموي مغلق.',
            participants: ['diaphragm', 'lungs', 'bronchi', 'trachea', 'larynx', 'vocalFolds', 'pharynx', 'velum', 'nasal', 'lips'],
            steps: ['The lungs provide outward airflow, supported by breathing muscles.', 'The vocal folds vibrate in the larynx, making the sound voiced.', 'The velum lowers; both lips close and block the oral route.', 'Air resonates in the nasal cavity and exits through the nose.'],
            stepsAr: ['توفر الرئتان تيار الهواء الخارج، وتسانده عضلات التنفس.', 'تهتز الطيتان الصوتيتان في الحنجرة، فيكون الصوت مجهوراً.', 'ينخفض الطبق وتنغلق الشفتان، فيُغلق المسار الفموي.', 'يرن الهواء في التجويف الأنفي ويخرج من الأنف.']
        },
        s: {
            ipa: '/s/', word: 'see', wordAr: 'see (يرى)', place: 'Alveolar', placeAr: 'لثويّ', manner: 'Fricative', mannerAr: 'احتكاكي', voicing: 'Voiceless', voicingAr: 'مهموس', route: 'oral', routeName: 'Through the mouth', routeNameAr: 'عبر الفم', voiced: false,
            description: 'For /s/, the tongue blade approaches the alveolar ridge and leaves a narrow channel. Air becomes turbulent at this constriction; the vocal folds do not vibrate and the velum is raised.',
            descriptionAr: 'في /s/ يقترب نصل اللسان من الحافة السنخية تاركاً ممراً ضيقاً. يضطرب الهواء عند هذا التضييق؛ ولا تهتز الطيتان الصوتيتان ويكون الطبق مرتفعاً.',
            participants: ['diaphragm', 'lungs', 'bronchi', 'trachea', 'larynx', 'glottis', 'pharynx', 'velum', 'oralCavity', 'tongueTip', 'alveolar'],
            steps: ['The lungs push air outward through the trachea.', 'The vocal folds stay apart, so the sound is voiceless.', 'The tongue narrows the space at the alveolar ridge without fully closing it.', 'Air passes through the mouth as a sustained, noisy fricative.'],
            stepsAr: ['يدفع الهواء من الرئتين إلى الخارج عبر القصبة الهوائية.', 'تبقى الطيتان الصوتيتان متباعدتين، لذلك يكون الصوت مهموساً.', 'يضيق اللسان الممر عند الحافة السنخية من دون إغلاقه تماماً.', 'يمر الهواء عبر الفم محدثاً احتكاكاً مستمراً.']
        },
        t: {
            ipa: '/t/', word: 'tea', wordAr: 'tea (شاي)', place: 'Alveolar', placeAr: 'لثويّ', manner: 'Stop (plosive)', mannerAr: 'وقفيّ (انفجاري)', voicing: 'Voiceless', voicingAr: 'مهموس', route: 'oral', routeName: 'Released through the mouth', routeNameAr: 'ينطلق عبر الفم', voiced: false,
            description: 'For /t/, the tongue tip makes a complete closure at the alveolar ridge. Air pressure builds behind it, then a short release burst opens the oral passage; the vocal folds do not vibrate.',
            descriptionAr: 'في /t/ يلامس طرف اللسان الحافة السنخية فيغلق الممر تماماً. يتجمع ضغط الهواء خلف الإغلاق ثم ينطلق فجأة عبر الفم، من دون اهتزاز الطيتين الصوتيتين.',
            participants: ['diaphragm', 'lungs', 'trachea', 'larynx', 'glottis', 'velum', 'oralCavity', 'tongueTip', 'alveolar', 'teeth'],
            steps: ['The lungs build the outward airstream.', 'The vocal folds are apart and the velum is raised.', 'The tongue tip seals the passage against the alveolar ridge.', 'The closure releases as a brief burst of air through the mouth.'],
            stepsAr: ['تولّد الرئتان تيار الهواء الخارج.', 'تكون الطيتان متباعدتين والطبق مرتفعاً.', 'يغلق طرف اللسان الممر عند الحافة السنخية.', 'ينفك الإغلاق بدفقة هواء قصيرة عبر الفم.']
        },
        a: {
            ipa: '/ɑː/', word: 'father', wordAr: 'father (أب)', place: 'Open, back vowel', placeAr: 'حركة خلفية مفتوحة', manner: 'Vowel; open vocal tract', mannerAr: 'حركة؛ مجرى مفتوح', voicing: 'Voiced', voicingAr: 'مجهور', route: 'oral', routeName: 'Through the open mouth', routeNameAr: 'عبر الفم المفتوح', voiced: true,
            description: 'For /ɑː/, the vocal folds vibrate while the mouth remains open. The tongue body is low and toward the back; there is no oral closure or narrow fricative constriction.',
            descriptionAr: 'في /ɑː/ تهتز الطيتان الصوتيتان ويبقى الفم مفتوحاً. يكون جسم اللسان منخفضاً ومتجهاً إلى الخلف، من دون إغلاق فموي أو تضييق احتكاكي.',
            participants: ['diaphragm', 'lungs', 'bronchi', 'trachea', 'larynx', 'vocalFolds', 'pharynx', 'velum', 'oralCavity', 'tongueBody', 'jaw', 'lips'],
            steps: ['The lungs supply a steady outward airstream.', 'The vocal folds vibrate to provide voicing.', 'The jaw lowers and the tongue body stays low and back.', 'Air leaves through the open oral cavity without a closure.'],
            stepsAr: ['توفر الرئتان تياراً ثابتاً من الهواء الخارج.', 'تهتز الطيتان الصوتيتان لتكوين الجهر.', 'ينخفض الفك ويبقى جسم اللسان منخفضاً ومتجهاً إلى الخلف.', 'يخرج الهواء عبر التجويف الفموي المفتوح من دون إغلاق.']
        },
        h: {
            ipa: '/h/', word: 'hat', wordAr: 'hat (قبعة)', place: 'Glottal', placeAr: 'حنجريّ', manner: 'Fricative-like airflow', mannerAr: 'هواء احتكاكي', voicing: 'Voiceless', voicingAr: 'مهموس', route: 'oral', routeName: 'Through the mouth', routeNameAr: 'عبر الفم', voiced: false,
            description: 'For /h/, the glottis is open and the vocal folds do not vibrate. Air passes through the larynx; the vocal tract is shaped much like the vowel that follows.',
            descriptionAr: 'في /h/ يكون المزمار مفتوحاً ولا تهتز الطيتان الصوتيتان. يمر الهواء عبر الحنجرة، ويتشكل مجرى الصوت بما يشبه الحركة التي تليه.',
            participants: ['diaphragm', 'lungs', 'trachea', 'larynx', 'glottis', 'pharynx', 'velum', 'oralCavity', 'tongueBody', 'lips'],
            steps: ['The lungs push air up through the trachea.', 'Air passes through an open glottis without vocal-fold vibration.', 'The pharynx and mouth take a shape close to the following vowel.', 'The breathy sound exits through the mouth.'],
            stepsAr: ['يدفع الهواء من الرئتين صعوداً عبر القصبة الهوائية.', 'يمر الهواء عبر مزمار مفتوح من دون اهتزاز الطيتين الصوتيتين.', 'يتخذ البلعوم والفم شكلاً قريباً من الحركة التي تلي الصوت.', 'يخرج الصوت النفَسي عبر الفم.']
        }
    };
    const localized = (term, field) => document.documentElement.lang === 'ar'
        ? arabicTerms[term.id][{name: 0, definition: 1, role: 2, stage: 3}[field]]
        : term[field];
    const localizedDemo = (demo, field) => document.documentElement.lang === 'ar'
        ? demo[`${field}Ar`]
        : demo[field];
    const list = document.getElementById('termIndex');
    const title = document.getElementById('termTitle');
    const definition = document.getElementById('termDefinition');
    const role = document.getElementById('termRole');
    const stage = document.getElementById('termStage');
    const diagram = document.querySelector('.speech-diagram');
    const motion = document.getElementById('airflowMotion');
    const nasalMotion = document.getElementById('nasalMotion');
    const airflowStatus = document.getElementById('airflowStatus');
    const replayButton = document.getElementById('replayAirflow');
    const demoDescription = document.getElementById('demoDescription');
    const demoParticipants = document.getElementById('demoParticipants');
    const demoSteps = document.getElementById('soundSteps');
    let currentDemo = null;
    const translate = (key, fallback) => window.siteTranslate?.(key) || fallback;

    if (!list || !title || !definition || !role || !stage) return;

    let selectedTerm = terms[0];

    function startAirflow(route = 'oral', voiced = false) {
        diagram.classList.toggle('is-nasal', route === 'nasal');
        diagram.classList.toggle('is-voiced', voiced);
        diagram.classList.remove('is-animating');
        void diagram.getBoundingClientRect();
        diagram.classList.add('is-animating');
        (route === 'nasal' ? nasalMotion : motion)?.beginElement();
        airflowStatus.textContent = translate(route === 'nasal' ? 'phonology.flowActiveNasal' : 'phonology.flowActive',
            route === 'nasal' ? 'Air flows from the lungs and exits through the nose.' : 'Air flows from the lungs and exits through the mouth.');
    }

    function selectTerm(term, {keepDemo = false, animate = true} = {}) {
        selectedTerm = term;
        if (!keepDemo) {
            currentDemo = null;
            document.querySelectorAll('.sound-choice').forEach(button => {
                button.classList.remove('is-active');
                button.setAttribute('aria-pressed', 'false');
            });
        }
        title.textContent = localized(term, 'name');
        definition.textContent = localized(term, 'definition');
        role.textContent = localized(term, 'role');
        stage.textContent = localized(term, 'stage');
        document.querySelectorAll('.diagram-node').forEach(node => {
            node.classList.toggle('is-active', node.dataset.term === term.id);
        });
        document.querySelectorAll('.anatomy-part').forEach(part => {
            part.classList.toggle('is-selected', part.dataset.organ === term.organ);
        });
        list.querySelectorAll('button').forEach(button => {
            const active = button.dataset.term === term.id;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
        });
        if (animate) startAirflow(term.organ === 'nasal' ? 'nasal' : 'oral');
    }

    function selectDemo(demoId) {
        const demo = soundDemos[demoId];
        if (!demo) return;
        currentDemo = demo;
        document.querySelectorAll('.sound-choice').forEach(button => {
            const active = button.dataset.demo === demoId;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
            const buttonDemo = soundDemos[button.dataset.demo];
            if (buttonDemo) button.lastElementChild.textContent = localizedDemo(buttonDemo, 'word');
        });
        document.getElementById('demoSymbol').textContent = `${demo.ipa} · ${localizedDemo(demo, 'word')}`;
        demoDescription.textContent = localizedDemo(demo, 'description');
        document.getElementById('demoPlace').textContent = localizedDemo(demo, 'place');
        document.getElementById('demoManner').textContent = localizedDemo(demo, 'manner');
        document.getElementById('demoVoicing').textContent = localizedDemo(demo, 'voicing');
        document.getElementById('demoAirRoute').textContent = localizedDemo(demo, 'routeName');
        demoSteps.replaceChildren(...localizedDemo(demo, 'steps').map(step => {
            const item = document.createElement('li');
            item.textContent = step;
            return item;
        }));
        demoParticipants.replaceChildren(...demo.participants.map(termId => {
            const term = terms.find(item => item.id === termId);
            if (!term) return null;
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = localized(term, 'name');
            button.addEventListener('click', () => selectTerm(term, {keepDemo: true, animate: false}));
            return button;
        }).filter(Boolean));
        document.querySelectorAll('.anatomy-part').forEach(part => {
            const activeOrgans = demo.participants.map(id => terms.find(term => term.id === id)?.organ);
            part.classList.toggle('is-selected', activeOrgans.includes(part.dataset.organ));
        });
        document.querySelectorAll('.diagram-node').forEach(node => {
            node.classList.toggle('is-active', demo.participants.includes(node.dataset.term));
        });
        startAirflow(demo.route, demo.voiced);
    }

    groups.forEach(group => {
        const section = document.createElement('section');
        section.className = 'term-group';
        const heading = document.createElement('h3');
        const [translationKey, fallback] = groupLabels[group];
        heading.textContent = translate(translationKey, fallback);
        const buttons = document.createElement('div');
        buttons.className = 'term-group-buttons';
        terms.filter(term => term.group === group).forEach((term, index) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.dataset.term = term.id;
            button.setAttribute('aria-pressed', 'false');
            const number = document.createElement('span');
            number.textContent = String(terms.filter(item => item.group === group).indexOf(term) + 1).padStart(2, '0');
            const label = document.createElement('span');
            label.textContent = localized(term, 'name');
            button.append(number, label);
            button.addEventListener('click', () => selectTerm(term));
            buttons.append(button);
        });
        section.append(heading, buttons);
        list.append(section);
    });

    document.querySelectorAll('.diagram-node').forEach(node => {
        const term = terms.find(item => item.id === node.dataset.term);
        if (!term) return;
        node.setAttribute('aria-label', localized(term, 'name'));
        node.addEventListener('click', () => selectTerm(term));
        node.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                selectTerm(term);
            }
        });
    });

    selectTerm(terms[0]);
    document.querySelectorAll('.sound-choice').forEach(button => {
        button.addEventListener('click', () => selectDemo(button.dataset.demo));
    });
    document.getElementById('demoParticipants').addEventListener('click', event => {
        const termButton = event.target.closest('button');
        const demoTerm = terms.find(term => term.name === termButton?.textContent || localized(term, 'name') === termButton?.textContent);
        if (demoTerm) selectTerm(demoTerm, {keepDemo: true, animate: false});
    });
    replayButton?.addEventListener('click', () => currentDemo
        ? selectDemo(Object.keys(soundDemos).find(key => soundDemos[key] === currentDemo))
        : startAirflow(selectedTerm.organ === 'nasal' ? 'nasal' : 'oral'));
    selectDemo('m');
    document.addEventListener('site-language-changed', () => {
        list.querySelectorAll('button').forEach(button => {
            const term = terms.find(item => item.id === button.dataset.term);
            if (term) button.lastElementChild.textContent = localized(term, 'name');
        });
        list.querySelectorAll('.term-group h3').forEach((heading, index) => {
            const [key, fallback] = groupLabels[groups[index]];
            heading.textContent = translate(key, fallback);
        });
        document.querySelectorAll('.diagram-node').forEach(node => {
            const term = terms.find(item => item.id === node.dataset.term);
            if (term) node.setAttribute('aria-label', localized(term, 'name'));
        });
        if (currentDemo) {
            selectDemo(Object.keys(soundDemos).find(key => soundDemos[key] === currentDemo));
        } else {
            selectTerm(selectedTerm, {animate: false});
        }
    });
})();