(() => {
    const examples = {
        unhappiness: {
            word: 'unhappiness', meaning: 'the state of not being happy',
            category: 'Derivational affixation',
            steps: [
                {parts: [['un-', 'PREFIX'], ['happy', 'ROOT']], result: 'unhappy', label: 'Derivational prefix · changes meaning', note: 'un- attaches before the root happy.'},
                {parts: [['unhappy', 'BASE'], ['-ness', 'SUFFIX']], result: 'unhappiness', label: 'Derivational suffix · changes word class', note: '-ness attaches after unhappy and forms a noun.'}
            ],
            morphemes: [
                {form: 'un-', role: 'derivational prefix', kind: 'derivational'},
                {form: 'happy', role: 'free root', kind: 'root'},
                {form: '-ness', role: 'derivational suffix', kind: 'derivational'}
            ],
            root: 'happy', base: 'unhappy', stem: 'unhappiness', class: 'adjective → noun',
            tree: {label: 'N', children: [{label: 'A', children: [{label: 'un-'}, {label: 'A', children: [{label: 'happy'}]}]}, {label: '-ness'}]}
        },
        cats: {
            word: 'cats', meaning: 'more than one cat',
            category: 'Inflectional affixation',
            steps: [
                {parts: [['cat', 'ROOT'], ['-s', 'PLURAL SUFFIX']], result: 'cats', label: 'Inflection · marks plural number', note: '-s attaches after the noun; it does not create a new word class.'}
            ],
            morphemes: [{form: 'cat', role: 'free root', kind: 'root'}, {form: '-s', role: 'plural inflection', kind: 'inflectional'}],
            root: 'cat', base: 'cat', stem: 'cat', class: 'noun · singular → plural',
            tree: {label: 'N[plural]', children: [{label: 'N', children: [{label: 'cat'}]}, {label: '-s'}]}
        },
        restarted: {
            word: 'restarted', meaning: 'started again; past tense of restart',
            category: 'Derivation + inflection',
            steps: [
                {parts: [['re-', 'PREFIX'], ['start', 'ROOT']], result: 'restart', label: 'Derivational prefix · means “again”', note: 're- attaches before start to form restart.'},
                {parts: [['restart', 'BASE'], ['-ed', 'PAST SUFFIX']], result: 'restarted', label: 'Inflection · marks past tense', note: '-ed attaches to the verb restart.'}
            ],
            morphemes: [{form: 're-', role: 'derivational prefix', kind: 'derivational'}, {form: 'start', role: 'free root', kind: 'root'}, {form: '-ed', role: 'past-tense inflection', kind: 'inflectional'}],
            root: 'start', base: 'start → restart', stem: 'restart', class: 'verb · derivation + past tense',
            tree: {label: 'V[past]', children: [{label: 'V', children: [{label: 're-', kind: 'affix'}, {label: 'V', children: [{label: 'start'}]}]}, {label: '-ed', kind: 'affix'}]}
        },
        blackbird: {
            word: 'blackbird', meaning: 'a bird of a particular type; a lexicalized compound',
            category: 'Compounding · no affix',
            steps: [
                {parts: [['black', 'FREE ROOT'], ['bird', 'FREE ROOT']], result: 'blackbird', label: 'Compound · two free roots', note: 'The two roots combine directly; neither part is an affix.'}
            ],
            morphemes: [{form: 'black', role: 'free root', kind: 'root'}, {form: 'bird', role: 'free root', kind: 'root'}],
            root: 'black + bird', base: 'black + bird', stem: 'blackbird', class: 'compound noun',
            tree: {label: 'N', children: [{label: 'A', children: [{label: 'black'}]}, {label: 'N', children: [{label: 'bird'}]}]}
        },
        toothbrush: {
            word: 'toothbrush', meaning: 'a brush used for cleaning teeth',
            category: 'Compounding · no affix',
            steps: [
                {parts: [['tooth', 'FREE ROOT'], ['brush', 'FREE ROOT']], result: 'toothbrush', label: 'Compound · two free roots', note: 'The two roots combine to name one kind of brush.'}
            ],
            morphemes: [{form: 'tooth', role: 'free root', kind: 'root'}, {form: 'brush', role: 'free root', kind: 'root'}],
            root: 'tooth + brush', base: 'tooth + brush', stem: 'toothbrush', class: 'compound noun',
            tree: {label: 'N', children: [{label: 'N', children: [{label: 'tooth'}]}, {label: 'N', children: [{label: 'brush'}]}]}
        },
        teachers: {
            word: 'teachers', meaning: 'people who teach',
            category: 'Derivation + inflection',
            steps: [
                {parts: [['teach', 'ROOT'], ['-er', 'SUFFIX']], result: 'teacher', label: 'Derivational suffix · forms a person noun', note: '-er attaches to teach to mean “a person who teaches”.'},
                {parts: [['teacher', 'BASE'], ['-s', 'PLURAL SUFFIX']], result: 'teachers', label: 'Inflection · marks plural number', note: '-s attaches outside the derivational suffix.'}
            ],
            morphemes: [{form: 'teach', role: 'free root', kind: 'root'}, {form: '-er', role: 'agent noun derivation', kind: 'derivational'}, {form: '-s', role: 'plural inflection', kind: 'inflectional'}],
            root: 'teach', base: 'teach → teacher', stem: 'teacher', class: 'verb → noun · plural',
            tree: {label: 'N[plural]', children: [{label: 'N', children: [{label: 'V', children: [{label: 'teach'}]}, {label: '-er', kind: 'affix'}]}, {label: '-s', kind: 'affix'}]}
        }
    };

    const processes = [
        {id:'derivation',name:'Derivation',example:'teach + -er → teacher',description:'An affix creates a new lexeme or changes meaning or word class. The suffix -er derives an agent noun from a verb.'},
        {id:'inflection',name:'Inflection',example:'walk + -ed → walked',description:'A grammatical form of the same lexeme. English -ed marks past tense; it does not create a new dictionary word.'},
        {id:'compounding',name:'Compounding',example:'tooth + brush → toothbrush',description:'Two or more lexical bases combine to form one lexeme. Compounds may be written closed, open, or hyphenated.'},
        {id:'blending',name:'Blending',example:'breakfast + lunch → brunch',description:'Parts of two words are fused, often with overlapping sounds or letters, to create a blend.'},
        {id:'clipping',name:'Clipping',example:'advertisement → ad',description:'A longer word is shortened while its core meaning and word class are usually retained.'},
        {id:'backformation',name:'Back-formation',example:'editor → edit',description:'A shorter word is created by removing a segment that speakers reinterpret as an affix.'},
        {id:'conversion',name:'Conversion',example:'email (noun) → to email (verb)',description:'A word changes its grammatical category without an overt affix. Also called zero-derivation.'},
        {id:'borrowing',name:'Borrowing',example:'algebra (Arabic) · piano (Italian)',description:'A language adopts a word from another language. Borrowed forms may later adapt to the recipient language.'},
        {id:'acronym',name:'Acronym and initialism',example:'NASA (spoken as a word) · FBI (letter names)',description:'An acronym is formed from initial letters and pronounced as a word; an initialism is pronounced letter by letter.'},
        {id:'reduplication',name:'Reduplication',example:'bye-bye · teeny-weeny',description:'A whole word or part of it is repeated. English uses reduplication in informal and expressive forms.'},
        {id:'coinage',name:'Coinage and eponyms',example:'Kodak · sandwich',description:'Coinage introduces a new lexical form; an eponym derives from a person or name. Brand histories should be checked individually.'},
        {id:'onomatopoeia',name:'Onomatopoeia',example:'buzz · hiss',description:'A word imitates or evokes a sound. The conventional form differs across languages.'},
        {id:'calque',name:'Calque (loan translation)',example:'loan translation of a model word or phrase',description:'A compound or phrase is translated part by part from another language rather than borrowed as a whole.'}
    ];

    const selector = document.getElementById('exampleSelector');
    const processList = document.getElementById('processList');
    if (!selector || !processList) return;

    function renderTreeNode(node, parent) {
        const wrapper = document.createElement('div');
        wrapper.className = 'tree-node';
        const label = document.createElement('span');
        label.className = `tree-label${node.kind === 'affix' ? '' : ' is-head'}`;
        label.textContent = node.label;
        wrapper.append(label);
        if (node.children?.length) {
            const children = document.createElement('div');
            children.className = 'tree-children';
            node.children.forEach(child => {
                const branch = document.createElement('div');
                branch.className = 'tree-branch';
                renderTreeNode(child, branch);
                children.append(branch);
            });
            wrapper.append(children);
        }
        parent.append(wrapper);
    }

    function selectExample(id) {
        const data = examples[id];
        document.querySelectorAll('.example-selector button').forEach(button => {
            const active = button.dataset.example === id;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
        });
        document.getElementById('analysisWord').textContent = data.word;
        document.getElementById('analysisDefinition').textContent = data.meaning;
        document.getElementById('affixationCategory').textContent = data.category;
        const affixationSteps = document.getElementById('affixationSteps');
        affixationSteps.replaceChildren(...data.steps.map((step, index) => {
            const item = document.createElement('li');
            item.className = 'affixation-step';
            item.style.animationDelay = `${index * 140}ms`;
            const label = document.createElement('strong');
            label.className = 'affixation-step-label';
            label.textContent = step.label;
            const equation = document.createElement('div');
            equation.className = 'affixation-equation';
            step.parts.forEach(([part, role], partIndex) => {
                if (partIndex) {
                    const plus = document.createElement('span');
                    plus.className = 'equation-operator';
                    plus.textContent = '+';
                    equation.append(plus);
                }
                const piece = document.createElement('span');
                piece.className = 'equation-piece';
                piece.dataset.role = role.toLowerCase().replaceAll(' ', '-');
                const form = document.createElement('strong');
                form.textContent = part;
                const name = document.createElement('small');
                name.textContent = role;
                piece.append(form, name);
                equation.append(piece);
            });
            const arrow = document.createElement('span');
            arrow.className = 'equation-operator';
            arrow.textContent = '→';
            equation.append(arrow);
            const result = document.createElement('strong');
            result.className = 'equation-result';
            result.textContent = step.result;
            equation.append(result);
            const note = document.createElement('p');
            note.textContent = step.note;
            item.append(label, equation, note);
            return item;
        }));
        const segmentation = document.getElementById('segmentation');
        segmentation.replaceChildren(...data.morphemes.map(morpheme => {
            const chip = document.createElement('span');
            chip.className = 'morpheme-chip';
            chip.dataset.kind = morpheme.kind;
            const form = document.createElement('strong');
            form.textContent = morpheme.form;
            const role = document.createElement('small');
            role.textContent = morpheme.role;
            chip.append(form, role);
            return chip;
        }));
        const factRows = [
            ['Root', data.root], ['Base', data.base], ['Stem', data.stem], ['Word class / change', data.class]
        ];
        document.getElementById('analysisFacts').replaceChildren(...factRows.flatMap(([label, value]) => {
            const term = document.createElement('dt');
            term.textContent = label;
            const detail = document.createElement('dd');
            detail.textContent = value;
            return [term, detail];
        }));
        const tree = document.getElementById('morphTree');
        tree.replaceChildren();
        renderTreeNode(data.tree, tree);
    }

    Object.entries(examples).forEach(([id, data]) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.example = id;
        button.setAttribute('aria-pressed', 'false');
        button.textContent = data.word;
        button.addEventListener('click', () => selectExample(id));
        selector.append(button);
    });

    function selectProcess(process) {
        document.querySelectorAll('.process-list button').forEach(button => {
            const active = button.dataset.process === process.id;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
        });
        document.getElementById('processTitle').textContent = process.name;
        document.getElementById('processDescription').textContent = process.description;
        document.getElementById('processExample').textContent = process.example;
    }

    processes.forEach(process => {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.process = process.id;
        button.setAttribute('aria-pressed', 'false');
        const title = document.createElement('strong');
        title.textContent = process.name;
        const example = document.createElement('span');
        example.textContent = process.example;
        button.append(title, example);
        button.addEventListener('click', () => selectProcess(process));
        processList.append(button);
    });

    selectExample('unhappiness');
    selectProcess(processes[0]);
})();