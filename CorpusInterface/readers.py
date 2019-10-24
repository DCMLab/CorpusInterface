import pandas as pd
import music21
from CorpusInterface.datatypes import Event, MIDIPitch, LinearTime, LinearTimeDuration

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
    for key in kwargs:
      if key == "time":
        time_col = kwargs[key]
      if key == "duration":
        duration_col = kwargs[key]
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


def read_midi(path, *args, **kwargs):
    events = []
    piece = music21.converter.parse(path)
    for part_id, part in enumerate(piece.parts):
        for note in part.flat.notes:
            if isinstance(note, (music21.note.Note, music21.chord.Chord)):
                for pitch in note.pitches:
                    events.append(Event(data=MIDIPitch(value=pitch.ps, part=part_id),
                                        time=LinearTime(note.offset),
                                        duration=LinearTimeDuration(note.duration.quarterLength)))
            else:
                raise Warning(f"Encountered unknown MIDI stream object {note} (type: {type(note)}) "
                              f"while reading file '{path}'")
    return list(sorted(events, key=lambda e: e.time))


def read_mscx(path, *args, **kwargs):
    raise NotImplementedError
