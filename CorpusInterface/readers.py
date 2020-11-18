import pandas as pd
from CorpusInterface.datatypes import Event, LinearTime, LinearTimeDuration
from CorpusInterface.midi import MIDINote, MIDITempo, MIDITimeSignature, EnharmonicPitch
from fractions import Fraction
import music21
import mido

# Readers for corpus files - each file 

def read_txt(path, *args, **kwargs):
    return open(path, *args, **kwargs).read()


def read_csv(path, *args, **kwargs):
    return pd.read_csv(path, *args, **kwargs)


def read_tsv(path, *args, **kwargs):
    time_col = None 
    duration_col = None
    events = []

    stdata = pd.read_csv(path, sep='\t')
    if kwargs.get('tsv_time') is not None:
      time_col = kwargs['tsv_time']
    if kwargs.get('tsv_duration') is not None:
      duration_col = kwargs['tsv_duration']
    for row in stdata.iterrows():
      [index, data] = row
      time = index
      if time_col != None:
        time = data[time_col]
      duration = None
      if duration_col != None:
        duration = data[duration_col]
      events.append(Event(data=data,time=LinearTime(time),duration=LinearTimeDuration(duration)))
    
    return list(events)


def read_humdrum_music21(path, *args, **kwargs):
    events = []
    piece = music21.converter.parse(path)
    for part_id, part in enumerate(piece.parts):
        for note in part.flat.notes:
            if isinstance(note, (music21.note.Note, music21.chord.Chord)):
                for pitch in note.pitches:
                    events.append(Event(data=EnharmonicPitch(value=pitch.ps),
                                        time=LinearTime(note.offset),
                                        duration=LinearTimeDuration(note.duration.quarterLength)))
            else:
                raise Warning(f"Encountered unknown Humdrum stream object {note} (type: {type(note)}) "
                              f"while reading file '{path}'")
    return list(sorted(events, key=lambda e: e.time))

read_humdrum = read_humdrum_music21

def read_midi_mido(path, raw=False, quantise=None, time_sig=False, tempo=False, as_enharmonic=False, *args, **kwargs):
    mid = mido.MidiFile(path)
    piece = []
    ticks_per_beat = mid.ticks_per_beat
    for track_id, t in enumerate(mid.tracks):
        time = 0
        track = []
        end_of_track = False
        active_notes = {}
        for msg in t:
            time += Fraction(msg.time, ticks_per_beat)
            if raw:
                track.append(Event(time=time, duration=None, data=msg))
            else:
                if msg.type == 'end_of_track':
                    # check for end of track
                    end_of_track = True
                else:
                    if end_of_track:
                        # raise if events occur after the end of track
                        raise ValueError("Received message after end of track")
                    elif msg.type == 'time_signature' and time_sig:
                        track.append(Event(time=LinearTime(time),
                                           duration=LinearTimeDuration(0),
                                           data=MIDITimeSignature(numerator=msg.numerator,
                                                                  denominator=msg.denominator)))
                    elif msg.type == 'set_tempo' and tempo:
                        track.append(Event(time=LinearTime(time),
                                           duration=LinearTimeDuration(0),
                                           data=MIDITempo(tempo=msg.tempo)))
                    elif msg.type == 'note_on' or msg.type == 'note_off':
                        note = (msg.note, msg.channel)
                        if msg.type == 'note_on' and msg.velocity > 0:
                            # note onset
                            if note in active_notes:
                                raise ValueError(f"{note} already active")
                            else:
                                active_notes[note] = (time, msg.velocity)
                        else: # (msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0)
                            # note offset
                            if note in active_notes:
                                onset_time = active_notes[note][0]
                                note_duration = time - active_notes[note][0]
                                # quantise time
                                if quantise is not None:
                                    onset_time = int(round(onset_time / quantise)) * quantise
                                    note_duration = int(round(note_duration / quantise)) * quantise
                                # append to track
                                track.append(Event(time=LinearTime(onset_time),
                                                   duration=LinearTimeDuration(note_duration),
                                                   data=EnharmonicPitch(value=msg.note) if as_enharmonic else
                                                   MIDINote(value=msg.note,
                                                            velocity=active_notes[note][1],
                                                            channel=msg.channel,
                                                            track=track_id)))
                                del active_notes[note]
                            else:
                                raise ValueError(f"{note} not active (time={time}, msg.type={msg.type}, msg.velocity={msg.velocity})")
        piece += track
    return list(sorted(piece, key=lambda x: x.time))


def read_midi_music21(path, *args, **kwargs):
    events = []
    piece = music21.converter.parse(path)
    for part_id, part in enumerate(piece.parts):
        for note in part.flat.notes:
            if isinstance(note, (music21.note.Note, music21.chord.Chord)):
                for pitch in note.pitches:
                    events.append(Event(data=MIDINote(value=pitch.ps, part=part_id),
                                        time=LinearTime(note.offset),
                                        duration=LinearTimeDuration(note.duration.quarterLength)))
            else:
                raise Warning(f"Encountered unknown MIDI stream object {note} (type: {type(note)}) "
                              f"while reading file '{path}'")
    return list(sorted(events, key=lambda e: e.time))


read_midi = read_midi_mido


def read_mscx(path, *args, **kwargs):
    raise NotImplementedError
