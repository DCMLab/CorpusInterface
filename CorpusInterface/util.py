from CorpusInterface.datatypes import Event, Vector
from CorpusInterface.midi import MIDINote


def split_midi_by_parts(events):
    part_list = []
    part_ids = []
    part_indices = {}
    for e in events:
        if not isinstance(e.data, MIDINote):
            raise TypeError("Expect events with MIDIPitch data")
        part = (e.data.channel, e.data.track)
        if part not in part_indices:
            part_indices[part] = len(part_indices)
            part_ids.append(part)
            part_list.append([])
        part_list[part_indices[part]].append(e)
    return part_list


def chordify(piece, duration_threshold=0):
    # create dictionary with time on- and offsets and events starting at a certain onset
    event_dict = {}
    for e in piece:
        # add onset and offset time slot
        if not e.time in event_dict:
            event_dict[e.time] = set()
        if not e.time + e.duration in event_dict:
            event_dict[e.time + e.duration] = set()
        # add event to onset time slot
        event_dict[e.time].add(e)
    # turn dict into ordered list of time-events pairs
    event_list = list(sorted(event_dict.items(), key=lambda item: item[0]))
    # take care of events that extend over multiple time slots
    active_events = set()
    for time, events in event_list:
        # from the active events (that started earlier) only keep those that reach into current time slot
        active_events = set(event for event in active_events if event.time + event.duration > time)
        # add these events to the current time slot
        events |= active_events
        # remember events that start with this slot to possibly add them in later slots
        active_events |= events
    # the last element should not contain any events as it was only created because the last event(s) ended at that time
    if event_list[-1][1]:
        raise ValueError("The last time slot should be empty. This is a bug (maybe due to floating point arithmetics?)")
    # turn dict into an ordered list of events with correct durations and combined event data
    return [Event(time=time, duration=next_time - time, data=frozenset([e.data for e in events]))
            for (time, events), (next_time, next_events) in zip(event_list, event_list[1:])
            if float(next_time - time) >= duration_threshold]


def linspace(start, stop, num=50, endpoint=True, retstep=False):
    step = (stop - start) / (num - int(endpoint))
    ret = [start + n * step for n in range(num)]
    if retstep:
        return ret, step
    else:
        return ret


def prange(start, stop, step=None, *, endpoint=False):
    if step is None:
        if isinstance(stop - start, Vector):
            step = (stop - start).__class__(1, is_interval_class=start.is_pitch_class())
        else:
            step = 1
    negative_step = step < (start - start)
    running = start
    while True:
        if not endpoint and running == stop:
            break
        if negative_step and running < stop:
            break
        if not negative_step and running > stop:
            break
        yield running
        running = running + step
