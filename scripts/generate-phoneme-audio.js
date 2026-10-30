import { mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import ESpeakNg from 'espeak-ng';

const inventories = {
    'en-GB': {
        voice: 'en-gb',
        phones: {
            'ɪ': 'I', 'e': 'E', 'æ': 'a', 'ʌ': 'V', 'ɒ': 'Q', 'ʊ': 'U',
            'ə': '@', 'iː': 'i:', 'ɑː': 'A:', 'ɔː': 'O:', 'uː': 'u:',
            'ɜː': '3:', 'eɪ': 'eI', 'aɪ': 'aI', 'ɔɪ': 'OI', 'aʊ': 'aU',
            'əʊ': '@U', 'ɪə': 'I@', 'eə': 'e@', 'ʊə': 'U@',
            'p': 'p', 'b': 'b@', 't': 't', 'd': 'd@', 'k': 'k', 'ɡ': 'g@',
            'f': 'f', 'v': 'v', 'θ': 'T', 'ð': 'D', 's': 's', 'z': 'z',
            'ʃ': 'S', 'ʒ': 'Z', 'h': 'h', 'tʃ': 'tS', 'dʒ': 'dZ@', 'm': 'm',
            'n': 'n', 'ŋ': 'N', 'l': 'l', 'ɹ': 'r@', 'j': 'j', 'w': 'w',
        },
    },
    'en-US': {
        voice: 'en-us',
        phones: {
            'ɪ': 'I', 'ɛ': 'E', 'æ': 'a', 'ʌ': 'V', 'ɑ': 'A:', 'ʊ': 'U',
            'ə': '@', 'i': 'i', 'ɔ': 'O', 'u': 'u', 'ɝ': '3', 'eɪ': 'eI',
            'aɪ': 'aI', 'ɔɪ': 'OI', 'aʊ': 'aU', 'oʊ': 'oU',
            'p': 'p', 'b': 'b@', 't': 't', 'd': 'd@', 'k': 'k', 'ɡ': 'g@',
            'f': 'f', 'v': 'v', 'θ': 'T', 'ð': 'D', 's': 's', 'z': 'z',
            'ʃ': 'S', 'ʒ': 'Z', 'h': 'h', 'tʃ': 'tS', 'dʒ': 'dZ@', 'm': 'm',
            'n': 'n', 'ŋ': 'N', 'l': 'l', 'ɹ': 'r@', 'j': 'j', 'w': 'w',
        },
    },
};

function audioKey(ipa) {
    return Array.from(ipa, character => character.codePointAt(0).toString(16)).join('-');
}

for (const [accent, inventory] of Object.entries(inventories)) {
    const outputDirectory = resolve('static/phoneme-audio', accent);
    mkdirSync(outputDirectory, { recursive: true });
    for (const [ipa, espeakPhone] of Object.entries(inventory.phones)) {
        const engine = await ESpeakNg({
            arguments: ['-v', inventory.voice, '-w', 'phoneme.wav', `[[${espeakPhone}]]`],
        });
        const audio = engine.FS.readFile('phoneme.wav');
        if (String.fromCharCode(...audio.subarray(0, 4)) !== 'RIFF') {
            throw new Error(`Invalid WAV generated for ${accent} /${ipa}/`);
        }
        writeFileSync(resolve(outputDirectory, `${audioKey(ipa)}.wav`), audio);
        console.log(`${accent} /${ipa}/`);
    }
}