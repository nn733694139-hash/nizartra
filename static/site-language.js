(() => {
    const translations = {
        en: {
            'language.kicker': 'LANGUAGE / 01',
            'language.title': 'Choose your language',
            'language.description': 'Select the language you want to use on this site.',
            'language.arabic': 'العربية',
            'language.english': 'English',
            'language.switch': 'Change language',
            'language.switchToArabic': 'العربية',
            'language.switchToEnglish': 'EN',
            'nav.home': 'Home',
            'nav.phonetics': 'Phonetics',
            'nav.about': 'Who we are?',
            'nav.contact': 'Contact us',
            'nav.thanks': 'Acknowledgements',
            'home.created': 'Created by',
            'home.badge': 'A focused phonetics and pronunciation studio',
            'home.heading': 'Hear English with clarity.',
            'home.intro': 'Explore English pronunciation, compare British and American speech, and build confidence one sound at a time.',
            'home.startLabel': 'START HERE',
            'home.enter': 'Open phonetics studio',
            'home.speechAccent': 'Speech accent',
            'home.chooseAccent': 'Choose speech accent',
            'home.british': 'British English',
            'home.american': 'American English',
            'home.tools': 'Pronunciation tools',
            'home.phoneticsTitle': 'Phonetics',
            'home.phoneticsText': 'Explore pronunciation with IPA transcription.',
            'home.peopleTitle': 'People',
            'home.peopleText': 'Meet the teachers, colleagues, and contributors.',
            'home.aboutTitle': 'About the Studio',
            'home.aboutText': 'Learn about the people and purpose behind the studio.',
            'feedback.title': 'Suggest an idea',
            'feedback.name': 'Student name (optional)',
            'feedback.yourName': 'Your name',
            'feedback.message': 'Your suggestion',
            'feedback.placeholder': 'Write your feedback',
            'feedback.send': 'Send suggestion',
            'feedback.sending': 'Sending your suggestion...',
            'feedback.received': 'Your feedback has been received. Thank you for sharing.',
            'home.footer': 'English Phonetics Studio',
            'about.title': 'About Us',
            'about.eyebrow': 'nizarphonetics · About',
            'about.lead': 'nizarphonetics is a student-centered space for exploring English sounds, pronunciation, and the details that make spoken language clear.',
            'about.storyTitle': 'Our Story',
            'about.story': 'This platform brings practical phonetics tools into one calm workspace. Its sample story and mission are fully editable from the administration panel.',
            'about.mission': '01 / Mission',
            'about.vision': '02 / Vision',
            'about.values': '03 / Values',
            'about.missionTitle': 'Pronunciation Made Clear',
            'about.missionText': 'Make English sounds easier to hear, understand, and practice through clear phonetic tools.',
            'about.visionTitle': 'Confidence in Every Sound',
            'about.visionText': 'Help learners build a lasting connection between written English and natural spoken language.',
            'about.valuesTitle': 'Practice, Clarity, Progress',
            'about.valuesText': 'We value accessible practice, careful listening, and steady progress at every level.',
            'about.principles': 'Our mission, vision, and values',
            'about.founder': 'Site founder',
            'about.founderBio': 'Founder of nizarphonetics, building thoughtful tools for English pronunciation and phonetic learning.',
            'contact.defaultTitle': 'Contact nizarphonetics',
            'contact.defaultIntro': 'Send a question, suggestion, or note to the nizarphonetics team.',
            'contact.emailHeading': 'Email',
            'contact.hoursHeading': 'Response Hours',
            'contact.defaultHours': 'Sunday to Thursday, 9:00 AM to 5:00 PM.',
            'contact.noteHeading': 'Your Feedback Matters',
            'contact.defaultNote': 'Share an idea or comment with the nizarphonetics team.',
            'contact.eyebrow': 'Get in touch',
            'contact.formTitle': 'Send a Message',
            'contact.name': 'Name (optional)',
            'contact.yourName': 'Your name',
            'contact.email': 'Email (optional)',
            'contact.topic': 'Message topic',
            'contact.question': 'Question',
            'contact.suggestion': 'Suggestion',
            'contact.feedback': 'Feedback',
            'contact.other': 'Other',
            'contact.message': 'Your message',
            'contact.placeholder': 'Write your message here...',
            'contact.send': 'Send Message',
            'contact.phone': 'Phone',
            'contact.social': 'Social Media',
            'contact.information': 'Contact information',
            'contact.sending': 'Submitting your message...',
            'thanks.title': 'Acknowledgements',
            'thanks.intro': 'In recognition of everyone who contributed to our pronunciation learning journey, I thank my professors and colleagues for their knowledge, collaboration, and support.',
            'thanks.faculty': 'Professors and Supervisors',
            'thanks.people': 'Colleagues and Students',
            'phonetics.heading': 'English, sound by sound.',
            'phonetics.intro': 'Explore phonemes, compare accents, and listen to each sound in context.',
            'phonetics.labOne': 'SPEECH LAB / 01',
            'phonetics.labTwo': 'SPEECH LAB / 02',
            'phonetics.transcription': 'IPA transcription',
            'phonetics.accent': 'Choose pronunciation accent',
            'phonetics.british': 'British',
            'phonetics.american': 'American',
            'phonetics.input': 'English text',
            'phonetics.inputPlaceholder': 'Type or paste English text...',
            'phonetics.output': 'PHONETIC TRANSCRIPTION',
            'phonetics.copy': 'Copy IPA transcription',
            'phonetics.listen': 'Listen',
            'phonetics.download': 'Download MP3',
            'phonetics.volume': 'Volume',
            'phonetics.caption': 'The accent setting changes transcription and speech. Audio downloads are generated as MP3.',
            'phonetics.allSounds': 'All sounds',
            'phonetics.vowels': 'Vowels',
            'phonetics.consonants': 'Consonants',
            'phonetics.allVowels': 'All vowels',
            'phonetics.allConsonants': 'All consonants',
            'phonetics.short': 'Short',
            'phonetics.long': 'Long',
            'phonetics.diphthongs': 'Diphthongs',
            'phonetics.voiced': 'Voiced',
            'phonetics.voiceless': 'Voiceless',
            'phonetics.selectSound': 'Select a sound',
            'phonetics.soundHelp': 'Choose a sound card to see where the tongue moves inside the mouth.',
            'phonetics.mouthPosition': 'MOUTH POSITION',
            'phonetics.tonguePosition': 'Tongue position',
            'phonetics.startingPosition': 'Starting tongue position',
            'phonetics.glideTo': 'Glide to',
            'phonetics.diagramKey': 'Tongue body · side view',
            'phonetics.diagramDisclaimer': 'Simplified teaching diagram; positions vary slightly between speakers.',
            'phonetics.vowelMap': 'Vowel sound map',
            'phonetics.consonantMap': 'Consonant sound map',
            'phonetics.inventory': 'English sound inventory',
            'phonetics.vowelCategories': 'Vowel categories',
            'phonetics.voicingCategories': 'Voicing categories',
            'phonetics.filterAll': 'Filter all English sounds',
            'phonetics.filterVowels': 'Filter vowel types',
            'phonetics.filterConsonants': 'Filter consonant voicing',
            'phonetics.select': 'Select',
            'phonetics.shortVowels': 'Short vowels',
            'phonetics.longVowels': 'Long vowels',
            'phonetics.noVibration': 'Voiceless · no vibration',
            'phonetics.vibration': 'Voiced · vibration',
            'phonetics.unavailable': 'Speech playback is not available in this browser.',
            'phonetics.enterText': 'Enter some text first.',
            'phonetics.processing': 'Preparing phonetic transcription...',
            'phonetics.transcriptionError': 'Unable to prepare phonetic transcription.',
            'phonetics.copySuccess': 'IPA copied to clipboard.',
            'phonetics.copyError': 'Clipboard access is unavailable in this browser.',
            'phonetics.generating': 'Generating your MP3...',
            'phonetics.downloaded': 'MP3 downloaded.',
            'phonetics.speechError': 'Unable to generate your audio file.',
            'phonetics.transcriptionPlaceholder': 'Your phonetic transcription will appear here.',
            'phonetics.accentSetting': 'The accent setting changes transcription and speech. Audio downloads are generated as MP3.'
            ,'phonetics.accentGBName': 'British English · Standard Southern British reference'
            ,'phonetics.accentUSName': 'American English · General American reference'
            ,'phonetics.vowelNoteGB': 'British reference vowels use /ɒ/ in “hot” and a non-rhotic /ɑː/ in “car”. Regional accents vary.'
            ,'phonetics.vowelNoteUS': 'American varieties do not use vowel length in the same way as British /ɒ/–/ɑː/. “Long” groups tense vowels for learner comparison; accents vary.'
            ,'phonetics.consonantNoteGB': 'Most consonants are shared across accents. British English usually has no /r/ after a vowel; /t/ in “water” is typically not a flap.'
            ,'phonetics.consonantNoteUS': 'Most consonants are shared across accents. General American pronounces /r/ in “car”; /t/ in “water” may become a voiced flap /ɾ/.'
            ,'phonetics.shortVowel': 'SHORT VOWEL'
            ,'phonetics.longVowel': 'LONG VOWEL'
            ,'phonetics.diphthongLabel': 'DIPHTHONG'
            ,'phonetics.voicedConsonant': 'VOICED CONSONANT'
            ,'phonetics.voicelessConsonant': 'VOICELESS CONSONANT'
            ,'phonetics.vowelLabel': 'VOWEL'
            ,'phonetics.vowelGlide': 'VOWEL GLIDE · tongue moves between positions'
            ,'phonetics.vowelStatus': 'VOWEL · tongue position'
            ,'phonetics.voicedStatus': 'VOICED · vocal folds vibrate'
            ,'phonetics.voicelessStatus': 'VOICELESS · no vocal-fold vibration'
            ,'phonetics.voicingFilter': 'Filter by voicing'
            ,'phonetics.speakingGB': 'Speaking in British English.'
            ,'phonetics.speakingUS': 'Speaking in American English.'
            ,'phonetics.generateError': 'Unable to generate your audio file.'
        },
        ar: {
            'language.kicker': 'اللغة / 01',
            'language.title': 'اختر لغة الموقع',
            'language.description': 'اختر اللغة التي تفضّل استخدامها في الموقع.',
            'language.arabic': 'العربية',
            'language.english': 'الإنجليزية',
            'language.switch': 'تغيير لغة الموقع',
            'language.switchToArabic': 'العربية',
            'language.switchToEnglish': 'EN',
            'nav.home': 'الرئيسية',
            'nav.phonetics': 'الأصوات',
            'nav.about': 'من نحن',
            'nav.contact': 'تواصل معنا',
            'nav.thanks': 'الشكر والتقدير',
            'home.created': 'إعداد',
            'home.badge': 'منصة متخصصة في الصوتيات والنطق',
            'home.heading': 'استمع إلى الإنجليزية بوضوح.',
            'home.intro': 'استكشف النطق الإنجليزي، وقارن بين اللهجتين البريطانية والأمريكية، وابنِ ثقتك صوتاً بعد صوت.',
            'home.startLabel': 'ابدأ من هنا',
            'home.enter': 'ادخل إلى مختبر الأصوات',
            'home.speechAccent': 'اللهجة الصوتية',
            'home.chooseAccent': 'اختر اللهجة الصوتية',
            'home.british': 'الإنجليزية البريطانية',
            'home.american': 'الإنجليزية الأمريكية',
            'home.tools': 'أدوات النطق',
            'home.phoneticsTitle': 'الصوتيات',
            'home.phoneticsText': 'تعرّف على النطق باستخدام رموز IPA الصوتية.',
            'home.peopleTitle': 'فريق العمل',
            'home.peopleText': 'تعرّف على المدرسين والزملاء والمساهمين.',
            'home.aboutTitle': 'عن المنصة',
            'home.aboutText': 'تعرّف على فريق المنصة والهدف منها.',
            'feedback.title': 'اقترح لنا اقتراحك',
            'feedback.name': 'اسم الطالب (اختياري)',
            'feedback.yourName': 'اسمك',
            'feedback.message': 'اقتراحك',
            'feedback.placeholder': 'اكتب اقتراحك هنا',
            'feedback.send': 'إرسال الاقتراح',
            'feedback.sending': 'جارٍ إرسال اقتراحك...',
            'feedback.received': 'وصلنا اقتراحك، شكراً لمشاركته.',
            'home.footer': 'منصة الأصوات الإنجليزية',
            'about.title': 'من نحن',
            'about.eyebrow': 'nizarphonetics · من نحن',
            'about.lead': 'منصة تعليمية لاستكشاف الأصوات الإنجليزية والنطق والتفاصيل التي تجعل اللغة المنطوقة أوضح.',
            'about.storyTitle': 'قصتنا',
            'about.story': 'تجمع المنصة أدوات عملية للصوتيات في مساحة واحدة. ويمكن تعديل نص القصة والرسالة من لوحة الإدارة.',
            'about.mission': '01 / رسالتنا',
            'about.vision': '02 / رؤيتنا',
            'about.values': '03 / قيمنا',
            'about.missionTitle': 'نطق أوضح',
            'about.missionText': 'نجعل أصوات الإنجليزية أسهل في الاستماع والفهم والتدرب باستخدام أدوات صوتية واضحة.',
            'about.visionTitle': 'الثقة في كل صوت',
            'about.visionText': 'نساعد المتعلمين على بناء صلة راسخة بين الإنجليزية المكتوبة والمنطوقة بطبيعتها.',
            'about.valuesTitle': 'تدرب ووضوح وتقدم',
            'about.valuesText': 'نؤمن بتدرب متاح، واستماع متأنٍ، وتقدم ثابت في كل مستوى.',
            'about.principles': 'رسالتنا ورؤيتنا وقيمنا',
            'about.founder': 'مؤسس الموقع',
            'about.founderBio': 'مؤسس nizarphonetics، يعمل على بناء أدوات مفيدة لتعلّم النطق والصوتيات الإنجليزية.',
            'contact.defaultTitle': 'تواصل مع nizarphonetics',
            'contact.defaultIntro': 'أرسل سؤالاً أو اقتراحاً أو ملاحظة إلى فريق nizarphonetics.',
            'contact.emailHeading': 'البريد الإلكتروني',
            'contact.hoursHeading': 'أوقات الرد',
            'contact.defaultHours': 'من الأحد إلى الخميس، من 9 صباحاً حتى 5 مساءً.',
            'contact.noteHeading': 'رأيك يهمنا',
            'contact.defaultNote': 'شارك فكرة أو ملاحظة مع فريق nizarphonetics.',
            'contact.eyebrow': 'تواصل معنا',
            'contact.formTitle': 'أرسل رسالة',
            'contact.name': 'الاسم (اختياري)',
            'contact.yourName': 'اسمك',
            'contact.email': 'البريد الإلكتروني (اختياري)',
            'contact.topic': 'موضوع الرسالة',
            'contact.question': 'استفسار',
            'contact.suggestion': 'اقتراح',
            'contact.feedback': 'ملاحظات',
            'contact.other': 'أخرى',
            'contact.message': 'رسالتك',
            'contact.placeholder': 'اكتب رسالتك هنا...',
            'contact.send': 'إرسال الرسالة',
            'contact.phone': 'الهاتف',
            'contact.social': 'حسابات التواصل الاجتماعي',
            'contact.information': 'معلومات التواصل',
            'contact.sending': 'جارٍ إرسال رسالتك...',
            'thanks.title': 'الشكر والتقدير',
            'thanks.intro': 'تقديراً لكل من ساهم في رحلتنا لتعلّم النطق، أتوجه بالشكر إلى أساتذتي وزملائي على ما قدموه من علم وتعاون ودعم.',
            'thanks.faculty': 'الأساتذة والمشرفون',
            'thanks.people': 'الزملاء والطلاب',
            'phonetics.heading': 'الإنجليزية، صوتاً بعد صوت.',
            'phonetics.intro': 'اكتشف الأصوات وقارن اللهجات واستمع إلى كل صوت في سياقه.',
            'phonetics.labOne': 'مختبر النطق / 01',
            'phonetics.labTwo': 'مختبر النطق / 02',
            'phonetics.transcription': 'التحويل إلى رموز IPA',
            'phonetics.accent': 'اختر لهجة النطق',
            'phonetics.british': 'بريطانية',
            'phonetics.american': 'أمريكية',
            'phonetics.input': 'النص الإنجليزي',
            'phonetics.inputPlaceholder': 'اكتب أو الصق نصاً بالإنجليزية...',
            'phonetics.output': 'التحويل الصوتي',
            'phonetics.copy': 'نسخ رموز IPA',
            'phonetics.listen': 'استمع',
            'phonetics.download': 'تنزيل MP3',
            'phonetics.volume': 'مستوى الصوت',
            'phonetics.caption': 'تغيّر اللهجة المختارة التحويل الصوتي والنطق. يمكن تنزيل الصوت بصيغة MP3.',
            'phonetics.allSounds': 'كل الأصوات',
            'phonetics.vowels': 'الحركات',
            'phonetics.consonants': 'الصوامت',
            'phonetics.allVowels': 'كل الحركات',
            'phonetics.allConsonants': 'كل الصوامت',
            'phonetics.short': 'قصيرة',
            'phonetics.long': 'طويلة',
            'phonetics.diphthongs': 'مزدوجة',
            'phonetics.voiced': 'مجهورة',
            'phonetics.voiceless': 'مهموسة',
            'phonetics.selectSound': 'اختر صوتاً',
            'phonetics.soundHelp': 'اختر بطاقة صوت لمعرفة موضع اللسان داخل الفم.',
            'phonetics.mouthPosition': 'موضع الفم',
            'phonetics.tonguePosition': 'موضع اللسان',
            'phonetics.startingPosition': 'موضع اللسان عند البداية',
            'phonetics.glideTo': 'الانزلاق إلى',
            'phonetics.diagramKey': 'جسم اللسان · منظر جانبي',
            'phonetics.diagramDisclaimer': 'رسم تعليمي مبسّط؛ وقد تختلف المواضع قليلاً بين المتحدثين.',
            'phonetics.vowelMap': 'خريطة الحركات',
            'phonetics.consonantMap': 'خريطة الصوامت',
            'phonetics.inventory': 'مجموعة الأصوات الإنجليزية',
            'phonetics.vowelCategories': 'أنواع الحركات',
            'phonetics.voicingCategories': 'أنواع الجهر',
            'phonetics.filterAll': 'تصفية كل الأصوات الإنجليزية',
            'phonetics.filterVowels': 'تصفية أنواع الحركات',
            'phonetics.filterConsonants': 'تصفية الصوامت حسب الجهر',
            'phonetics.select': 'اختر',
            'phonetics.shortVowels': 'حركات قصيرة',
            'phonetics.longVowels': 'حركات طويلة',
            'phonetics.noVibration': 'مهموس · دون اهتزاز',
            'phonetics.vibration': 'مجهور · مع اهتزاز',
            'phonetics.unavailable': 'تشغيل النطق غير متاح في هذا المتصفح.',
            'phonetics.enterText': 'أدخل نصاً أولاً.',
            'phonetics.processing': 'جارٍ إعداد التحويل الصوتي...',
            'phonetics.transcriptionError': 'تعذّر إعداد التحويل الصوتي.',
            'phonetics.copySuccess': 'تم نسخ رموز IPA.',
            'phonetics.copyError': 'الوصول إلى الحافظة غير متاح في هذا المتصفح.',
            'phonetics.generating': 'جارٍ إنشاء ملف MP3...',
            'phonetics.downloaded': 'تم تنزيل ملف MP3.',
            'phonetics.speechError': 'تعذّر إنشاء الملف الصوتي.',
            'phonetics.transcriptionPlaceholder': 'سيظهر التحويل الصوتي هنا.',
            'phonetics.accentSetting': 'تغيّر اللهجة المختارة التحويل الصوتي والنطق. يمكن تنزيل الصوت بصيغة MP3.'
            ,'phonetics.accentGBName': 'الإنجليزية البريطانية · مرجع جنوب بريطانيا القياسي'
            ,'phonetics.accentUSName': 'الإنجليزية الأمريكية · مرجع الأمريكية العامة'
            ,'phonetics.vowelNoteGB': 'في المرجع البريطاني يُستخدم /ɒ/ في “hot” و/ɑː/ غير المسبوق بصوت /r/ في “car”. وتختلف اللهجات الإقليمية.'
            ,'phonetics.vowelNoteUS': 'لا تستخدم اللهجات الأمريكية طول الحركة بالطريقة نفسها في التقابل البريطاني /ɒ/–/ɑː/. مجموعة «الطويلة» هنا للتعلم، واللهجات تختلف.'
            ,'phonetics.consonantNoteGB': 'معظم الصوامت مشتركة بين اللهجات. غالباً لا يُنطق /r/ بعد حركة في البريطانية، ويُنطق /t/ في “water” دون قلبه إلى صوت رفرفة.'
            ,'phonetics.consonantNoteUS': 'معظم الصوامت مشتركة بين اللهجات. يُنطق /r/ في “car” بالأمريكية العامة، وقد يتحول /t/ في “water” إلى رفرفة /ɾ/ مجهورة.'
            ,'phonetics.shortVowel': 'حركة قصيرة'
            ,'phonetics.longVowel': 'حركة طويلة'
            ,'phonetics.diphthongLabel': 'حركة مزدوجة'
            ,'phonetics.voicedConsonant': 'صامت مجهور'
            ,'phonetics.voicelessConsonant': 'صامت مهموس'
            ,'phonetics.vowelLabel': 'حركة'
            ,'phonetics.vowelGlide': 'انزلاق صوتي · ينتقل اللسان بين موضعين'
            ,'phonetics.vowelStatus': 'حركة · موضع اللسان'
            ,'phonetics.voicedStatus': 'مجهور · تهتز الأوتار الصوتية'
            ,'phonetics.voicelessStatus': 'مهموس · دون اهتزاز الأوتار الصوتية'
            ,'phonetics.voicingFilter': 'تصفية حسب الجهر'
            ,'phonetics.speakingGB': 'النطق باللهجة البريطانية.'
            ,'phonetics.speakingUS': 'النطق باللهجة الأمريكية.'
            ,'phonetics.generateError': 'تعذّر إنشاء الملف الصوتي.'
        }
    };

    const languageKey = 'nizarphonetics-language';
    const prompt = document.getElementById('languagePrompt');
    const switcher = document.getElementById('languageSwitcher');
    let activeLanguage = localStorage.getItem(languageKey) === 'ar' ? 'ar' : 'en';

    function translate(key) {
        return translations[activeLanguage][key] || translations.en[key] || key;
    }

    function applyLanguage(language) {
        activeLanguage = language === 'ar' ? 'ar' : 'en';
        document.documentElement.lang = activeLanguage;
        document.documentElement.dir = activeLanguage === 'ar' ? 'rtl' : 'ltr';
        document.body.classList.toggle('is-arabic', activeLanguage === 'ar');

        document.querySelectorAll('[data-i18n]').forEach(element => {
            element.textContent = translate(element.dataset.i18n);
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            element.placeholder = translate(element.dataset.i18nPlaceholder);
        });
        document.querySelectorAll('[data-i18n-aria]').forEach(element => {
            element.setAttribute('aria-label', translate(element.dataset.i18nAria));
        });
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            element.title = translate(element.dataset.i18nTitle);
        });
        if (switcher) {
            switcher.textContent = translate(activeLanguage === 'ar' ? 'language.switchToEnglish' : 'language.switchToArabic');
        }
        document.dispatchEvent(new CustomEvent('site-language-changed', {detail: {language: activeLanguage}}));
    }

    function chooseLanguage(language) {
        localStorage.setItem(languageKey, language);
        applyLanguage(language);
        if (prompt?.open) prompt.close();
    }

    applyLanguage(activeLanguage);
    if (!localStorage.getItem(languageKey) && window.siteLanguageConfig?.promptEnabled && prompt?.showModal) {
        prompt.showModal();
    }

    prompt?.querySelectorAll('[data-language-choice]').forEach(button => {
        button.addEventListener('click', () => chooseLanguage(button.dataset.languageChoice));
    });
    prompt?.addEventListener('cancel', event => {
        event.preventDefault();
        chooseLanguage('en');
    });
    switcher?.addEventListener('click', () => chooseLanguage(activeLanguage === 'ar' ? 'en' : 'ar'));

    window.siteTranslate = translate;
    window.siteLanguage = () => activeLanguage;
})();