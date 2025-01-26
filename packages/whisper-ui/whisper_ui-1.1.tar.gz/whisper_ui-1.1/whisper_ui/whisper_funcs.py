import os
import json

import whisper
from whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE

from whisper_ui.handle_prefs import USER_PREFS, check_model

SUPPORTED_FILETYPES = ('flac', 'm4a', 'mp3', 'wav')
AVAILABLE_MODELS = whisper.available_models()
VALID_LANGUAGES = sorted(
    LANGUAGES.keys()
) + sorted(
    [k.title() for k in TO_LANGUAGE_CODE.keys()]
)
LANGUAGES_FLIPPED = {v: k for k, v in LANGUAGES.items()}
TO_LANGUAGE_CODE_FLIPPED = {v: k for k, v in TO_LANGUAGE_CODE.items()}

if USER_PREFS['DEBUG']:
    model = 'abc'
else:
    model = None
    
def map_available_language_to_valid_language(available_language):
    al = available_language.lower()
    if al not in VALID_LANGUAGES:
        if al in LANGUAGES_FLIPPED and LANGUAGES_FLIPPED[al] in VALID_LANGUAGES:
            return LANGUAGES_FLIPPED[al]
        elif al in TO_LANGUAGE_CODE_FLIPPED and TO_LANGUAGE_CODE_FLIPPED[al] in VALID_LANGUAGES:
            return TO_LANGUAGE_CODE_FLIPPED[al]
    else:
        return al

def get_model():
    global model
    
    model_name = USER_PREFS["model"]
    
    if not check_model(model_name):
        print(f'\tWarning: model {model_name} not found in cache. Please download it.')
        return
    
    if model is None:
        print(f'\tLoading model {model_name}. This may take a while if you have never used this model.')
        print(f'\t\tChecking for GPU...')
        from torch.cuda import is_available
        device = 'cuda' if is_available() else 'cpu'
        if device == 'cuda':
            print('\t\tGPU found.')
        else:
            print('\t\tNo GPU found. Using CPU.')
        try:
            model = whisper.load_model(name=USER_PREFS['model'], device=device, in_memory=True)
        except:
            try:
                model = whisper.load_model(name=USER_PREFS['model'], device=device)
            except:
                print('\t\tWarning: issue loading model onto GPU. Using CPU.')
                model = whisper.load_model(name=USER_PREFS['model'], device='cpu')
        print(f'\tLoaded model {model_name} successfully.')
    else:
        print(f'\tUsing currently loaded model ({model_name}).')

def format_outputs(outputs):
    
    text_template = USER_PREFS['text_template']
    segmentation_template = USER_PREFS['segmentation_template']
    
    text_template_filled = None
    segmentation_lines = None
    
    if USER_PREFS['do_text']:
        text_is = USER_PREFS['text_insertion_symbol']
        text_template_filled = text_template.replace(
            text_is, outputs['text']
        )
    
    if USER_PREFS['do_segmentation']:
        text_is = USER_PREFS['segment_insertion_symbol']
        start_is = USER_PREFS['start_time_insertion_symbol']
        end_is = USER_PREFS['end_time_insertion_symbol']
        
        segmentation_lines = []
        for segment in outputs['segments']:
            text = segment['text']
            start = str(segment['start'])
            end = str(segment['end'])
            seg_template_filled = segmentation_template.replace(
                text_is, text
            ).replace(
                start_is, start
            ).replace(
                end_is, end
            )
            segmentation_lines.append(seg_template_filled)
            
    return {
        'text': text_template_filled,
        'segmentation_lines': segmentation_lines
    }
    
def write_outputs(outputs: dict, formatted_outputs: dict, fname: str):
    text = formatted_outputs['text']
    segmentation_lines = formatted_outputs['segmentation_lines']
    
    output_dir = USER_PREFS['output_dir']
    os.makedirs(output_dir, exist_ok=True)
    
    if USER_PREFS['do_text']:
        loc = os.path.join(output_dir, fname + '.txt')
        with open(loc, 'w+', encoding='utf-8') as f:
            f.write(text.strip())
        print(f'\t\tWrote transcription to "{loc}".')
    if USER_PREFS['do_segmentation']:
        loc = os.path.join(output_dir, fname + '.seg')
        with open(loc, 'w+', encoding='utf-8') as g:
            for line in segmentation_lines:
                g.write(line.strip() + '\n')
        print(f'\t\tWrote segmentation to "{loc}".')
    if USER_PREFS['do_json']:
        loc = os.path.join(output_dir, fname + '.json')
        with open(loc, 'w+', encoding='utf-8') as h:
            json.dump(outputs, h, indent=4)
        print(f'\t\tWrote JSON data to "{loc}".')

def transcribe(paths):
    
    global model
    
    if not paths:
        print('No matching files found.\n')
        return
    
    print(f'Beginning transcription of {len(paths)} audio file(s).')

    get_model()
    
    for i, path in enumerate(paths):
        
        print(f'\tTranscribing "{path}" (file {i+1}/{len(paths)})...')
        
        path = os.path.normpath(path)
        assert os.path.exists(path)
        
        basename = os.path.basename(path)
        fname, ext = os.path.splitext(basename)
        
        if ext[1:] not in SUPPORTED_FILETYPES:
            msg = f'\tWarning: file "{path}" may not be supported. '
            msg += '\tSupported filetypes are: ' + ', '.join(SUPPORTED_FILETYPES)
            print(msg)
        
        if USER_PREFS['DEBUG']:
            outputs = json.load(
                open(os.path.join('test_outputs', 'example_output.json'), 'r', encoding='utf-8')
            )
        else:
            outputs = model.transcribe(
                whisper.load_audio(path),
                language = map_available_language_to_valid_language(USER_PREFS['language'])
            )
        formatted_outputs = format_outputs(outputs)
        write_outputs(outputs, formatted_outputs, fname)
        print('\tDone.')
    
    print(f'Transcribed {len(paths)} files.\n')
