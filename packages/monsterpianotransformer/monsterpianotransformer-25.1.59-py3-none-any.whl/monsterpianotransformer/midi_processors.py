#===================================================================================================
# Monster Piano Transformer midi_processors Python module
#===================================================================================================
# Project Los Angeles
# Tegridy Code 2025
#===================================================================================================
# License: Apache 2.0
#===================================================================================================

from . import TMIDIX

#===================================================================================================

def midi_to_tokens(input_midi,
                   encode_velocity=False
                   ):

    raw_score = TMIDIX.midi2single_track_ms_score(input_midi)
    
    escore_notes = TMIDIX.advanced_score_processor(raw_score, return_enhanced_score_notes=True)[0]
    escore_notes = TMIDIX.augment_enhanced_score_notes(escore_notes, timings_divider=32)
    
    sp_escore_notes = TMIDIX.solo_piano_escore_notes(escore_notes, keep_drums=False)
    zscore = TMIDIX.recalculate_score_timings(sp_escore_notes)
    
    cscore = TMIDIX.chordify_score([1000, zscore])
    
    score = []
    
    pc = cscore[0]
    
    for c in cscore:
        score.append(max(0, min(127, c[0][1]-pc[0][1])))
    
        for n in c:
            if encode_velocity:
                score.extend([max(1, min(127, n[2]))+128, max(1, min(127, n[4]))+256, max(1, min(127, n[5]))+384])

            else:
                score.extend([max(1, min(127, n[2]))+128, max(1, min(127, n[4]))+256])
    
        pc = c

    return score

#===================================================================================================

def tokens_to_midi(tokens,
                   output_midi_name='Monster-Piano-Transformer-Composition',
                   return_score=False,
                   ):
    
    if [t for t in tokens 384 < t < 512]:
        model_with_velocity = True
        
    else:
        model_with_velocity = False
    
    song = tokens
    song_f = []

    time = 0
    dur = 0
    vel = 90
    pitch = 0
    channel = 0
    patch = 0

    patches = [0] * 16

    for m in song:

        if 0 <= m < 128:
            time += m * 32

        elif 128 < m < 256:
            dur = (m-128) * 32

        elif 256 < m < 384:
            pitch = (m-256)

            if not model_with_velocity:
                song_f.append(['note', time, dur, 0, pitch, max(40, pitch), 0])

        elif 384 < m < 512:
            vel = (m-384)

            if model_with_velocity:
                song_f.append(['note', time, dur, 0, pitch, vel, 0])
                
    detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                                output_signature = 'Monster Piano Transformer',
                                                                output_file_name = output_midi_name,
                                                                track_name='Project Los Angeles',
                                                                list_of_MIDI_patches=patches,
                                                                verbose=False
                                                            )
    
    if return_score:
        return song_f

    else:
        return detailed_stats
    
#===================================================================================================
    
def midi_to_chords(input_midi,
                   return_times=True,
                   return_durs=True,
                   return_vels=True,
                   return_only_chords=False
                  ):

    raw_score = TMIDIX.midi2single_track_ms_score(input_midi)
    escore_notes = TMIDIX.advanced_score_processor(raw_score, return_enhanced_score_notes=True)[0]
    escore_notes = TMIDIX.augment_enhanced_score_notes(escore_notes, timings_divider=32)
    
    sp_escore_notes = TMIDIX.solo_piano_escore_notes(escore_notes, keep_drums=False)
    zscore = TMIDIX.recalculate_score_timings(sp_escore_notes)
    
    cscore = TMIDIX.chordify_score([1000, zscore])
    
    times_durs = []
    tones_chords = []
    chords_lens = []

    output = []
    
    for c in cscore:
        
        pitches = [e[4] for e in c]
            
        tones_chord = sorted(set([p % 12 for p in pitches]))
             
        if tones_chord in TMIDIX.ALL_CHORDS_SORTED:
            chord_token = TMIDIX.ALL_CHORDS_SORTED.index(tones_chord)
            
        else:
            tones_chord = TMIDIX.check_and_fix_tones_chord(tones_chord)
            chord_token = TMIDIX.ALL_CHORDS_SORTED.index(tones_chord)

        out = [[chord_token] + pitches]

        if return_times:
            out.append([c[0][1]])

        if return_durs:
            durs = [e[2] for e in c]
            out.append([int(sum(durs) / len(durs))])

        if return_vels:
            vels = [e[5] for e in c]
            out.append([int(sum(vels) / len(vels))])

        output.append(out)

    if return_only_chords:
        return [c[0][0] for c in output]

    else:
        return output

#===================================================================================================

def chords_pitches_to_midi(chords_pitches,
                           midi_chords_list=[[]],
                           chords_dtimes=-1,
                           chords_durs=-1,
                           chords_vels=-1,
                           output_midi_name='Monster-Piano-Transformer-Composition',
                           return_score=False
                          ):

    cpitches = []

    for cp in chords_pitches:
        cpitches.append([c for c in cp if 0 < c < 128])

    if len(midi_chords_list[0]) == 4:
        song_len = min(len(chords_pitches), len(midi_chords_list))

    else:
        song_len = len(chords_pitches)

    time = 0
    dtime = 8
    dur = 8

    song = []

    patches = [0] * 16

    for i in range(song_len):

        if chords_dtimes < 1 and len(midi_chords_list[0]) == 4:
            time = midi_chords_list[i][1][0]

        if chords_durs < 1 and len(midi_chords_list[0]) == 4:
            dur = midi_chords_list[i][2][0]

        elif chords_durs > 0:
            dur = chords_durs

        if chords_vels == -1 and len(midi_chords_list[0]) == 4:
            vel = midi_chords_list[i][3][0]

        elif chords_vels > 0:
            vel = chords_vels

        for p in chords_pitches[i]:

            if chords_vels == -1 and len(midi_chords_list[0]) != 4:
                vel = max(40, p)
            
            song.append(['note', time, dur, 0, p, vel, 0])

        if chords_dtimes > 0:
            time += chords_dtimes

        elif chords_dtimes < 1 and len(midi_chords_list[0]) != 4:
            time += dtime
        
    detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song,
                                                              output_signature = 'Monster Piano Transformer',
                                                              output_file_name = output_midi_name,
                                                              track_name='Project Los Angeles',
                                                              list_of_MIDI_patches=patches,
                                                              timings_multiplier=32,
                                                              verbose=False
                                                             )
    
    if return_score:
        return song_f

    else:
        return detailed_stats
    
#===================================================================================================
# This is the end of midi_processors Python module
#===================================================================================================