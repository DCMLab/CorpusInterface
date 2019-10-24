import re

class Point:
    """
    Base class for objects describing a point in a space. Examples would be a pitch, a point in time, or a point in
    Euclidean space. The purpose of this class is to make developing and maintaining these kinds of classes convenient
    by providing basic functionality, like a one-liner to create the associated vector class and basic arithmetic
    operations (see Vector class). Otherwise, the abstract Point class is just a wrapper around some value. The
    semantics of this value and any extended functionality is defined via the derived classes.
    """
    class Vector:
        """
        Base class for objects describing direction and magnitude in a space. A class derived from Vector should have an
        associated Point class and should be defined via the Point class' create_vector_class method, which will also
        take care of letting both classes know of each other. Creating multiple Vector class for the same Point class
        is likely to cause trouble, but you can force it if feel that you absolutely need to.
        """

        @classmethod
        def _assert_has_point_class(cls):
            if not hasattr(cls, "_point_class"):
                raise AttributeError(f"This class ({cls}) does not have a '_point_class' attribute")

        @classmethod
        def _assert_is_vector(cls, other):
            if not isinstance(other, cls):
                raise TypeError(f"Object is not of correct type (expected {cls}, got {type(other)}")

        def __init__(self, value, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._value = value

        def __repr__(self):
            return f"{self.__class__.__name__}({self._value})"

        def __sub__(self, other):
            self._assert_is_vector(other)
            return self.__class__(self._value - other._value)

        def __add__(self, other):
            self._assert_is_vector(other)
            return self.__class__(self._value + other._value)

        def __mul__(self, other):
            return self.__class__(self._value * other)

        def __rmul__(self, other):
            return self.__mul__(other)

        def __eq__(self, other):
            return isinstance(other, self.__class__) and self._value == other._value

        def to_point(self):
            self._assert_has_point_class()
            return self._point_class(self._value)

    @classmethod
    def create_vector_class(cls, name=None, *, force_overwrite=False):
        """
        Create the corresponding vector class for this point class and link the two classes
        :param name: optional name for the vector class (default is to append "Vector" to the point class name)
        :return: the vector class object
        """
        # create vector class derived from abstract vector class
        vector_class = type(cls.__name__ + "Vector" if name is None else name,
                            (Point.Vector,),
                            {})
        # link classes
        cls.link_vector_class(vector_class, force_overwrite=force_overwrite)
        # return class
        return vector_class

    @classmethod
    def link_vector_class(cls, vcls, *, force_overwrite=False):
        """
        Link point class 'cls' and vector class 'vcls' by adding _vector_class and _point_class attribute, respectively.
        Raises an error if one of the classes already has the corresponding attribute, which would be overwritten.
        Overwriting can be forced by setting force_overwrite=True.
        :param vcls: vector class to be linked (will be modified by adding the _point_class attribute)
        :param force_overwrite: ignore existing links
        """
        # check if point class already has an associated vector class
        if hasattr(cls, "_vector_class") and not force_overwrite:
            raise AttributeError(f"Class '{cls}' already has an associated vector class ({cls._vector_class})")
        # check if point class already has an associated vector class
        if hasattr(vcls, "_point_class") and not force_overwrite:
            raise AttributeError(f"Class '{vcls}' already has an associated point class ({vcls._point_class})")
        # let the point class know its vector class and vice versa
        cls._vector_class = vcls
        vcls._point_class = cls

    @classmethod
    def _assert_has_vector_class(cls):
        if not hasattr(cls, "_vector_class"):
            raise AttributeError(f"This class ({cls}) does not have a '_vector_class' attribute")

    @classmethod
    def _assert_is_point(cls, other):
        if not isinstance(other, cls):
            raise TypeError(f"Object is not of correct type (expected {cls}, got {type(other)}")

    @classmethod
    def _assert_is_vector(cls, other):
        if not isinstance(other, cls._vector_class):
            raise TypeError(f"Object is not of correct type (expected {cls._vector_class}, got {type(other)}")

    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __sub__(self, other):
        self._assert_has_vector_class()
        try:
            self._assert_is_point(other)
            return self._vector_class(self._value - other._value)
        except TypeError:
            self._assert_is_vector(other)
            return self.__class__(self._value - other._value)

    def __add__(self, other):
        self._assert_has_vector_class()
        self._assert_is_vector(other)
        return self.__class__(self._value + other._value)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._value == other._value

    def to_vector(self):
        self._assert_has_vector_class()
        return self._vector_class(self._value)


class Pitch(Point):
    """
    Base class for pitches. Behaves like Point/Vector but adds renamed versions for:
        to_point --> to_pitch
        to_vector --> to_interval
        create_vector_class --> create_interval_class
        link_vector_class --> link_interval_class
        Point.Vector --> Pitch.Interval
    """

    # for pitches, intervals are the equivalent of vectors
    Interval = Point.Vector

    @classmethod
    def create_interval_class(cls, name=None, *, force_overwrite=False):
        # give it a proper default name
        if name is None:
            name = cls.__name__+"Interval"
        # call parent function to create
        interval_class = cls.create_vector_class(name=name, force_overwrite=force_overwrite)
        # add properly renamed version of to_point
        interval_class.to_pitch = interval_class.to_point
        # return
        return interval_class

    @classmethod
    def link_interval_class(cls, icls, *, force_overwrite=False):
        cls.link_vector_class(icls, force_overwrite=force_overwrite)

    def to_interval(self):
        return self.to_vector()


class Time(Point):
    """
    Base class for time-like types. Behaves like Point/Vector but adds renamed versions for:
        to_point --> to_time
        to_vector --> to_duration
        create_vector_class --> create_duration_class
        link_vector_class --> link_duration_class
    """

    @classmethod
    def create_duration_class(cls, name=None, *, force_overwrite=False):
        # give it a proper default name
        if name is None:
            name = cls.__name__+"Duration"
        # call parent function to create
        duration_class = cls.create_vector_class(name=name, force_overwrite=force_overwrite)
        # add properly renamed version of to_point
        duration_class.to_time = duration_class.to_point
        # return
        return duration_class

    @classmethod
    def link_duration_class(cls, icls, *, force_overwrite=False):
        cls.link_vector_class(icls, force_overwrite=force_overwrite)

    def to_duration(self):
        return self.to_vector()


class LinearTime(Time):
    """
    Class for "normal" time types that have a total order
    """

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        else:
            return self._value < other._value

    def __float__(self):
        return float(self._value)


LinearTimeDuration = LinearTime.create_duration_class()


class MIDIPitch(Pitch):

    _diatonic_pitch_class = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 6, "A": 9, "B": 11}
    _base_names_sharp = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    _base_names_flat = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    name_regex = re.compile("^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>-?[0-9]+)$")

    def __init__(self, value, part=None, expect_int=True, *args, **kwargs):
        if isinstance(value, str):
            # extract pitch class, modifiers, and octave
            match = MIDIPitch.name_regex.match(value)
            if match is None:
                raise ValueError(f"{value} does not match the regular expression for MIDI pitch names "
                                 f"'{MIDIPitch.name_regex.pattern}'.")
            # initialise value with diatonic pitch class
            value = MIDIPitch._diatonic_pitch_class[match['class']]
            # add modifiers
            if "#" in match['modifiers']:
                value += len(match['modifiers'])
            else:
                value -= len(match['modifiers'])
            # add octave
            value += 12 * (int(match['octave']) + 1)
        if expect_int:
            int_value = int(value)
            if int_value != value:
                raise ValueError(f"Expected integer pitch value but got {value}")
            value = int_value
        super().__init__(value=value, *args, **kwargs)
        self.part = part
        # compute frequency
        self.freq = 2 ** ((self._value - 69) / 12) * 440

    def __int__(self):
        return self._value

    def __repr__(self):
        return self.name()

    def octave(self):
        return self._value // 12 - 1

    def pitch_class(self):
        return self._value % 12

    def name(self, sharp_flat=None):
        if sharp_flat is None:
            sharp_flat = "sharp"
        if sharp_flat == "sharp":
            base_names = self._base_names_sharp
        elif sharp_flat == "flat":
            base_names = self._base_names_flat
        else:
            raise ValueError("parameter 'sharp_flat' must be on of ['sharp', 'flat']")
        return f"{base_names[self.pitch_class()]}{self.octave()}"


MIDIPitchInterval = MIDIPitch.create_interval_class()


class MIDIPitchClass(MIDIPitch):

    def __init__(self, value, *args, **kwargs):
        if isinstance(value, MIDIPitch):
            super().__init__(value._value % 12, *args, **kwargs)
        else:
            super().__init__(value % 12, *args, **kwargs)

    def name(self, sharp_flat=None):
        if sharp_flat is None:
            sharp_flat = "sharp"
        if sharp_flat == "sharp":
            base_names = self._base_names_sharp
        elif sharp_flat == "flat":
            base_names = self._base_names_flat
        else:
            raise ValueError("parameter 'sharp_flat' must be on of ['sharp', 'flat']")
        return f"{base_names[self.pitch_class()]}"


class Event:

    def __init__(self, time, duration, data):
        self.time = time
        self.duration = duration
        self.data = data

    def __repr__(self):
        return f"{self.__class__.__name__}(time={self.time}, duration={self.duration}, data={self.data})"
