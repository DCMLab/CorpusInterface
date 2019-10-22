import pandas as pd
import music21
from CorpusInterface.datatypes import Event, MIDIPitch, LinearTime, LinearTimeDuration


def read_txt(path, *args, **kwargs):
    return open(path, *args, **kwargs).read()


def read_csv(path, *args, **kwargs):
    return pd.read_csv(path, *args, **kwargs)


def read_tsv(path, *args, **kwargs):
    return pd.read_csv(path, sep='\t', *args, **kwargs)


def read_midi(path, *args, **kwargs):
    events = []
    for note in music21.converter.parse(path).flat.notes:
        if isinstance(note, (music21.note.Note, music21.chord.Chord)):
            for pitch in note.pitches:
                events.append(Event(data=MIDIPitch(value=pitch.ps),
                                    time=LinearTime(note.offset),
                                    duration=LinearTimeDuration(note.duration.quarterLength)))
        else:
            raise Warning(f"Encountered unknown MIDI stream object {note} (type: {type(note)}) "
                          f"while reading file '{path}'")
    return list(sorted(events, key=lambda e: e.time))


def read_mscx(path, *args, **kwargs):
    raise NotImplementedError
