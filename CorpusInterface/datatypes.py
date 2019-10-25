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

        @staticmethod
        def _vector_add(vec1, vec2):
            return vec1 + vec2

        @staticmethod
        def _vector_sub(vec1, vec2):
            return vec1 - vec2

        @staticmethod
        def _scalar_mul(scalar, vec):
            return scalar * vec

        def __init__(self, value, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._value = value

        def __repr__(self):
            return f"{self.__class__.__name__}({self._value})"

        def __sub__(self, other):
            self._assert_is_vector(other)
            return self.__class__(self._vector_sub(self._value, other._value))

        def __add__(self, other):
            self._assert_is_vector(other)
            return self.__class__(self._vector_add(self._value, other._value))

        def __mul__(self, other):
            return self.__class__(self._scalar_mul(other, self._value))

        def __rmul__(self, other):
            return self.__mul__(other)

        def __eq__(self, other):
            return isinstance(other, self.__class__) and self._value == other._value

        def to_point(self):
            self._assert_has_point_class()
            return self._point_class(self._value)

    @classmethod
    def create_vector_class(cls, name=None, *, force_overwrite=False, vector_class=None):
        """
        Create the corresponding vector class for this point class and link the two classes
        :param name: optional name for the vector class (default is to append "Vector" to the point class name)
        :param force_overwrite: whether to overwrite an existing vector class
        :param vector_class: an optional class, derived from Vector, that is used as base class
        :return: the vector class object
        """
        # if class was provided check that it is actually derived from Vector
        if vector_class is not None:
            if Point.Vector not in vector_class.__bases__:
                raise TypeError(f"Provided class {vector_class} does not derive from {Point.Vector}")
        else:
            vector_class = Point.Vector
        # create vector class derived from abstract vector class
        vector_class = type(cls.__name__ + "Vector" if name is None else name,
                            (vector_class,),
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
        Overwriting can be forced by setting force_overwrite=True. This is for instance needed when linking a vector
        class to a point class that was derived from another point class, which already has an associated vector class.
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

    @staticmethod
    def _vector_add(point, vec):
        return point + vec

    @staticmethod
    def _point_sub(p1, p2):
        return p1 - p2

    @staticmethod
    def _vector_sub(point, vec):
        return point - vec

    @staticmethod
    def _scalar_mul(scalar, vec):
        return scalar * vec

    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self._value})"

    def __sub__(self, other):
        self._assert_has_vector_class()
        try:
            self._assert_is_point(other)
            return self._vector_class(self._point_sub(self._value, other._value))
        except TypeError:
            self._assert_is_vector(other)
            return self.__class__(self._vector_sub(self._value, other._value))

    def __add__(self, other):
        self._assert_has_vector_class()
        self._assert_is_vector(other)
        return self.__class__(self._vector_add(self._value, other._value))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._value == other._value

    def to_vector(self):
        self._assert_has_vector_class()
        return self._vector_class(self._value)


class Pitch(Point):
    """
    Base class for pitches. Pitch and Interval behave like Point and vector so we add renamed versions for:
        to_point --> to_pitch
        to_vector --> to_interval
        create_vector_class --> create_interval_class
        link_vector_class --> link_interval_class
        Point.Vector --> Pitch.Interval
    """

    class Interval(Point.Vector):

        @classmethod
        def _assert_has_pitch_class(cls):
            cls._assert_has_point_class()

        @classmethod
        def _assert_is_interval(cls, other):
            cls._assert_is_vector(other)

        def __init__(self, value, *args, **kwargs):
            # if value is derived from Pitch.Interval, try to convert to converter to this type and get the _value
            if Pitch.Interval in value.__class__.__mro__:
                value = value.convert_to(self.__class__)._value
            super().__init__(value, *args, **kwargs)

        def to_pitch(self):
            self._assert_has_pitch_class()
            return self._pitch_class(self._value)

        def convert_to(self, other_type):
            """Attempts to convert intervals using the converters from the corresponding Pitch classes."""
            self._assert_has_pitch_class()
            other_type._assert_has_pitch_class()
            # convert interval-->equivalent pitch-->other pitch type-->equivalent interval
            other_interval = self.to_pitch().convert_to(other_type._pitch_class).to_interval()
            # but point<-->value (pitch<-->interval) conversion relies on an implicit origin;
            # if the two origins of the two different pitch classes are not identical,
            # we are off by the corresponding difference;
            # the origin can be retrieved as the equivalent point of the zero vector
            origin_from = (self - self).to_pitch().convert_to(other_type._pitch_class) # point
            origin_to = (other_interval - other_interval).to_pitch() # point
            origin_difference = origin_to - origin_from # vector
            # now we add that difference (we move from the "from" origin to the "to" origin)
            return other_interval + origin_difference

    # store converters for classes derived from Pitch;
    # it's a dict of dicts, so that __converters__[A][B] returns is a list of functions that, when executed
    # successively, converts A to B
    __converters__ = {}

    @staticmethod
    def register_converter(from_type, to_type, conv_func,
                           overwrite_explicit_converters=None,
                           overwrite_implicit_converter=True,
                           extend_implicit_converters=True):
        """
        Register a converter from from_type to other type. The converter function should be function taking as its
        single argument an from_type object and returning an other_type object.
        :param to_type: other type derived from Pitch, which the converter function converts to
        :param conv_func: converter function from from_type to other_type
        :param overwrite_explicit_converters: can be True, False, or None (default); if True and there exists an
        explicit converter (i.e. the list of converter functions is of length 1), replace it by this converter function;
        if False, don't replace explicit converters; if None, raise a ValueError if an explicit converter exists
        :param overwrite_implicit_converter: if there exists an implicit converter (i.e. the list of converter functions
        is of length greater than 1) replace it by this converter function
        :param extend_implicit_converters: if there is an (explicit or implicit) converter from type X to type
        from_type, add an implicit converter from type X to other_type by extending the list of converter functions from
        X to from_type by this converter function; if there already exists an (explicit or implicit) converter from X to
        other_type, it will not be overwritten
        """
        # initialise converter dict if it does not exist
        if from_type not in Pitch.__converters__:
            Pitch.__converters__[from_type] = {}
        # get existing converters from from_type to to_type and decide whether to set new converter
        set_new_converter = False
        try:
            converter = from_type.get_converter(to_type)
        except NotImplementedError:
            # no existing converters
            set_new_converter = True
        else:
            # implicit or explicit converter are already registered
            if len(converter) == 1:
                # explicit converter
                if overwrite_explicit_converters is None:
                    raise ValueError("An explicit converter already exists. Set overwrite_explicit_converters=True to "
                                     "overwrite.")
                elif overwrite_explicit_converters:
                    set_new_converter = True
            else:
                # implicit converter
                if overwrite_implicit_converter:
                    set_new_converter = True
        # set the new converter
        if set_new_converter:
            Pitch.__converters__[from_type][to_type] = [conv_func]
        # extend implicit converters
        if extend_implicit_converters:
            for another_from_type, other_converters in Pitch.__converters__.items():
                # remember new converters to not change dict while iterating over it
                new_converters = []
                for another_to_type, converter_pipeline in other_converters.items():
                    # trying to prepend this converter [from_type --> to_type == another_from_type --> another_to_type]
                    if to_type == another_from_type:
                        # get existing converters from_type --> ???
                        converters = from_type.get_converter()
                        # add the extended converter if one does not exist
                        if another_to_type not in converters:
                            converters[another_to_type] = [conv_func] + converter_pipeline
                    # try to append this converter [another_from_type --> another_to_type == from_type --> to_type]
                    if another_to_type == from_type:
                        # already initialised and we have the existing converters another_from_type --> ???
                        # add the extended converter if one does not exist
                        if to_type not in other_converters:
                            new_converters.append((to_type, converter_pipeline + [conv_func]))
                # insert new converters
                for key, val in new_converters:
                    other_converters[key] = val

    @classmethod
    def get_converter(cls, other_type=None):
        # return dedicated converter if other_type was specified or list of existing converters otherwise
        if other_type is not None:
            all_converters = cls.get_converter()
            try:
                return all_converters[other_type]
            except KeyError:
                raise NotImplementedError(f"Type '{cls}' does not have any converter registered for type "
                                          f"'{other_type}'")
        else:
            try:
                return Pitch.__converters__[cls]
            except KeyError:
                raise NotImplementedError(f"There are no converters registered for type '{cls}'")

    @classmethod
    def create_interval_class(pitch_class, name=None, *, force_overwrite=False):
        # give it a proper default name
        if name is None:
            name = pitch_class.__name__ + "Interval"
        # call parent function to create
        interval_class = pitch_class.create_vector_class(name=name,
                                                         force_overwrite=force_overwrite,
                                                         vector_class=Pitch.Interval)
        # add properly renamed versions
        interval_class.to_pitch = interval_class.to_point
        pitch_class._interval_class = pitch_class._vector_class
        interval_class._pitch_class = interval_class._point_class
        # return
        return interval_class

    @classmethod
    def link_interval_class(pitch_class, interval_class, *, force_overwrite=False):
        pitch_class.link_vector_class(interval_class, force_overwrite=force_overwrite)
        pitch_class._interval_class = pitch_class._vector_class
        interval_class._pitch_class = interval_class._point_class

    def __init__(self, value, *args, **kwargs):
        # if value is derived from Pitch, try to convert to converter to this type and get the _value
        if Pitch in value.__class__.__mro__:
            value = value.convert_to(self.__class__)._value
        super().__init__(value, *args, **kwargs)

    def convert_to(self, other_type):
        ret = self
        for converter in self.__class__.get_converter(other_type):
            ret = converter(ret)
        return ret

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

    _diatonic_pitch_class = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    _base_names_sharp = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    _base_names_flat = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    name_regex = re.compile("^(?P<class>[A-G])(?P<modifiers>(b*)|(#*))(?P<octave>-?[0-9]+)$")

    def __init__(self, value, part=None, expect_int=True, *args, **kwargs):
        super().__init__(value=value, *args, **kwargs)
        if isinstance(self._value, str):
            # extract pitch class, modifiers, and octave
            match = MIDIPitch.name_regex.match(self._value)
            if match is None:
                raise ValueError(f"{self._value} does not match the regular expression for MIDI pitch names "
                                 f"'{MIDIPitch.name_regex.pattern}'.")
            # initialise value with diatonic pitch class
            self._value = MIDIPitch._diatonic_pitch_class[match['class']]
            # add modifiers
            if "#" in match['modifiers']:
                self._value += len(match['modifiers'])
            else:
                self._value -= len(match['modifiers'])
            # add octave
            self._value += 12 * (int(match['octave']) + 1)
        if expect_int:
            int_value = int(self._value)
            if int_value != self._value:
                raise ValueError(f"Expected integer pitch value but got {self._value}")
            self._value = int_value
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

    @staticmethod
    def convert_from_MIDIPitch(midi_pitch):
        return MIDIPitchClass(midi_pitch._value)

    def __init__(self, value, *args, **kwargs):
        super().__init__(value, *args, **kwargs)
        self._value %= 12

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


Pitch.register_converter(MIDIPitch, MIDIPitchClass, MIDIPitchClass.convert_from_MIDIPitch)


class MIDIPitchClassInterval(Pitch.Interval):

    def __init__(self, value, *args, **kwargs):
        super().__init__(value, *args, **kwargs)
        self._value %= 12
        if self._value > 6:
            self._value -= 12

    def __int__(self):
        return int(self._value)

    def to_pitch(self):
        return self._pitch_class(self._value % 12)


MIDIPitchClass.link_interval_class(MIDIPitchClassInterval, force_overwrite=True)


class Event:

    def __init__(self, time, duration, data):
        self.time = time
        self.duration = duration
        self.data = data

    def __repr__(self):
        return f"{self.__class__.__name__}(time={self.time}, duration={self.duration}, data={self.data})"
