from CorpusInterface.datatypes import MIDIPitch


def split_midi_by_parts(events):
    part_list = []
    part_ids = []
    part_indices = {}
    for e in events:
        if not isinstance(e.data, MIDIPitch):
            raise TypeError("Expect events with MIDIPitch data")
        part = e.data.part
        if part not in part_indices:
            part_indices[part] = len(part_indices)
            part_ids.append(part)
            part_list.append([])
        part_list[part_indices[part]].append(e)
    return part_list
