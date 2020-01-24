import music21


def write_midi(piece, file_name=None, title="Title"):
    note_list = []
    time = 0
    for event in piece:
        n = music21.note.Note(pitch=int(event.data))
        n.offset = time
        note_list.append(n)
        time += event.duration
    score = music21.stream.Score(givenElements=note_list)
    score.insert(0, music21.metadata.Metadata())
    score.metadata.title = title
    if file_name is None:
        return score
    else:
        score.write('midi', file_name)
