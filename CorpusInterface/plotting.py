import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from CorpusInterface.util import split_midi_by_parts
import numpy as np


def pianoroll(events, ax=None, show=False, **kwargs):
    # create axis if needed
    if ax is None:
        fig, ax_ = plt.subplots(1, 1, **kwargs)
    else:
        fig = None
        ax_ = ax
    data = [np.array([[int(e.data), e.time, e.time + e.duration] for e in part])
            for part in split_midi_by_parts(events)]
    min_pitch = float(min(min(d[:, 0]) for d in data))
    max_pitch = float(max(max(d[:, 0]) for d in data))
    min_time = float(min(min(d[:, 1]) for d in data))
    max_time = float(max(max(d[:, 2]) for d in data))
    part_height = max_pitch - min_pitch + 1
    for part_idx, part in enumerate(data):
        color = next(ax_._get_lines.prop_cycler)['color']
        offset = part_idx * part_height
        ax_.add_patch(Rectangle((min_time, offset),
                                max_time - min_time,
                                part_height,
                                color=color,
                                alpha=0.1))
        for pitch, start, end in part:
            # ax_.plot([start, end], [pitch + offset, pitch + offset], linewidth=1)
            ax_.add_patch(Rectangle((start, pitch - min_pitch + offset), end - start, 1, color=color))
    ax_.set_xlim(min_time, max_time)
    ax_.set_ylim(0, (max_pitch - min_pitch) * len(data))
    ax_.set_yticks([n * (max_pitch - min_pitch) for n in range(len(data))])
    ax_.set_xlabel("time")
    ax_.set_ylabel("pitch")
    ax_.set_yticks([])
    ax_.grid(b=True, which='major', color='#666666', linestyle='-')
    ax_.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    if show:
        plt.show()
    if ax is None:
        return fig, ax_
