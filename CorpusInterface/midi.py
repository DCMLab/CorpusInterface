from fractions import Fraction
from CorpusInterface.datatypes import Pitch, Interval, EnharmonicPitch


class MIDINote(EnharmonicPitch):

    @staticmethod
    def convert_to_EnharmonicPitch(midi_note):
        return EnharmonicPitch(midi_note._value)

    def __init__(self, value, velocity, channel, track, *args, **kwargs):
        super().__init__(value, *args, **kwargs)
        self.velocity = velocity
        self.channel = channel
        self.track = track

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._value == other._value and self.channel == other.channel and self.velocity == other.velocity
        else:
            return NotImplemented

    def __hash__(self):
        return hash((self._value, self.channel, self.velocity))

    def __repr__(self):
        return super().__repr__() + f" [velocity={self.velocity}, channel={self.channel}, track={self.track}]"

    def to_pitch_class(self):
        return self.__class__(value=self._value,
                              velocity=self.velocity,
                              channel=self.channel,
                              track=self.track,
                              is_pitch_class=True)


@MIDINote.link_interval_class(overwrite_interval_class=True)
class MIDIInterval(Interval):
    pass


Pitch.register_converter(MIDINote, EnharmonicPitch, MIDINote.convert_to_EnharmonicPitch)


class MIDITempo(int):
    def __new__(cls, tempo, *args, **kwargs):
        return super(MIDITempo, cls).__new__(cls, tempo)

    def __repr__(self):
        return f"Tempo({super().__repr__()}ms/beat"

    def __str__(self):
        return self.__repr__()


class MIDITimeSignature(Fraction):

    def __new__(cls, numerator, denominator, *args, **kwargs):
        return super(MIDITimeSignature, cls).__new__(cls, numerator=numerator, denominator=denominator)

    def __init__(self, numerator, denominator, *args, **kwargs):
        self.orig_numerator = numerator
        self.orig_denominator = denominator

    def __repr__(self):
        return f"TimeSignature({self.orig_numerator}/{self.orig_denominator})"

    def __str__(self):
        return self.__repr__()
