import random
import string
import typing
from datetime import date, datetime, timedelta
from dateutil.parser import parse

class Any():

    def __init__(self, mode_datadirty: bool=False):
        self._mode_datadirty = mode_datadirty

    def of(self, options: list):
        return random.choice(options)


    def listOf(self, factoryFunction, min: int =1, max: int = 5):
        result = []
        amount = random.randrange(min, max)
        for i in range(0, amount):
            data = factoryFunction()
            result.append(data)

        return result

    def subsetOf(self, items: list, min: int = None, max: int=None):
        if min == None:
            min=1
        if max == None or max > len(items):
            max=len(items)

        amount_to_get = random.randrange(min, max)

        items_randomized = random.sample(items, len(items))
        return items_randomized[:amount_to_get] # grab X first elements

    def digits(self, min: int, max: int) -> int:
        if min == max:
            number= min
        else:
            number: int =random.randrange(min, max)

        return random.randint(
            10**(number-1),
            10**number-1
        )

    def positiveInt(self, min: int = 0, max=9999) -> int:
        number: int =random.randrange(min, max)
        if self._mode_datadirty == True:
            return self.of([number, str(number)])

        return int(number)

    def negativeInt(self, min: int = -9999, max=0) -> int:
        number: int = random.randrange(min, max)

        if self._mode_datadirty == True:
            return self.of([number, str(number)])

        return int(number)

    def anyInt(self, min=-1000, max=1000) -> int:
        number: int = random.randrange(min, max)
        if self._mode_datadirty == True:
            return self.of([number, str(number)])

        return int(number)

    def positiveFloat(self, min: int = 0, max: int =9999) -> float:
        number: float =random.uniform(min, max)
        if self._mode_datadirty == True:
            return self.of([number, str(number)])

        return number

    def negativeFloat(self, min: int = -9999, max: int =0) -> float:
        number: float = random.uniform(min, max)

        if self._mode_datadirty == True:
            return self.of([number, str(number)])

        return number

    def anyFloat(self, min =-1000, max =1000) -> float:
        number: float = random.uniform(min, max)
        if self._mode_datadirty == True:
            return self.of([number, str(number)])

        return number


    def anyLetter(self) -> str:
        letter = self.of(list(string.ascii_lowercase))

        if self._mode_datadirty == True:
            return self.of([f" {letter}", letter, f"{letter} ", f" {letter} "])

        return letter

    def word(self, min = 1, max = 30) -> str:
        length = random.randrange(min, max)

        alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1)]

        word = ''.join(random.choice(alphabet) for i in range(length))

        if self._mode_datadirty == True:
            return self.of([f" {word}", word, f"{word} ", f" {word} "])

        return word

    def sentence(self, min_words: int = 2, max_words: int = 5) -> str:
        amount_words = random.randrange(min_words, max_words)

        words=[]
        for i in range(amount_words):
            words.append(self.word())

        sentence = ' '.join(words)

        return sentence

    def bytes(self, min=1, max=30) -> bytes:
        word = self.word(min, max)
        return word.encode('UTF-8')


    def bool(self) -> bool:
        boolean = self.of([True, False])
        if self._mode_datadirty == True:
            return self.of([boolean, "true", "True", "false", "False"])

        return boolean

    def null(self) -> None:
        if self._mode_datadirty == True:
            return self.of([None, "None", "null"])

        return None


    def dateTimeInPast(self) -> datetime:
        now = datetime.now()
        return now - timedelta(days = int(self.positiveInt()))


    def dateTimeInFuture(self) -> datetime:
        now = datetime.now()
        return now + timedelta(days=int(self.positiveInt()))

    def dateTimeBefore(self, beforeDateTime) -> datetime:
        if isinstance(beforeDateTime, str):
            beforeDateTime = parse(beforeDateTime, fuzzy=True)

        return beforeDateTime - timedelta(days=int(self.positiveInt()))

    def dateTimeAfter(self, afterDateTime) -> datetime:
        if isinstance(afterDateTime, str):
            afterDateTime = parse(afterDateTime, fuzzy=True)

        return afterDateTime + timedelta(days=int(self.positiveInt()))

    def datetimeBetween(self, from_datetime, to_datetime) -> datetime:
        if isinstance(from_datetime, str):
            from_datetime = parse(from_datetime, fuzzy=True)

        if isinstance(to_datetime, str):
            to_datetime = parse(to_datetime, fuzzy=True)

        from_datetime_ts = from_datetime.timestamp()
        to_datetime_ts = to_datetime.timestamp()

        random_ts_between = int(self.positiveInt(min=from_datetime_ts, max=to_datetime_ts))

        return datetime.fromtimestamp(random_ts_between)

    def dateTime(self) -> datetime:
        return self.of([self.dateTimeInPast(), self.dateTimeInFuture()])

    def date(self) -> date:
        return self.dateTime().date()

    def ip(self) -> str:
        ip = [
            str(self.positiveInt(min=10, max=255)),
            str(self.positiveInt(min=10, max=255)),
            str(self.positiveInt(min=10, max=255)),
            str(self.positiveInt(min=10, max=255))
        ]

        return ".".join(ip)


    def filepath(self) -> str:
        extension=self.of(options=[
            "csv","pdf", "json", "xml", "png", "jpg", "parquet", "avro", "zip", "rar", "gzp"
        ])

        min_words=2
        max_words=8
        amount_words = random.randrange(min_words, max_words)

        words=[]
        for i in range(amount_words):
            words.append(self.word(min=1, max=7))

        sentence = '/'.join(words)

        path= sentence

        return f"{path}.{extension}"


    def email(self) -> str:
        extension = self.of(["es", "com", "net", "co.uk", "io"])
        return f"{self.word()}@{self.word()}.{extension}"

    def object_like(self, class_of_interest):
        import inspect
        from typing import get_args

        parameters = inspect.signature(class_of_interest.__init__).parameters

        param_values = {}

        def create_value(param_annotation, param_default):
            if param_annotation == int:
                if param_default == inspect.Parameter.empty:  # no default value
                    return self.anyInt()
                return self.of([self.anyInt(), param_default])


            elif param_annotation == float:
                if param_default == inspect.Parameter.empty:
                    return self.anyFloat()
                return self.of([self.anyFloat(), param_default])

            elif param_annotation == str:
                if param_default == inspect.Parameter.empty:
                    return self.word()
                return self.of([self.word(), param_default])

            elif param_annotation == bool:
                if param_default == inspect.Parameter.empty:
                    return self.bool()
                return self.of([self.bool(), param_default])

            elif param_annotation == datetime:
                if param_default == inspect.Parameter.empty:
                    return self.dateTime()
                return self.of([self.dateTime(), param_default])

            elif param_annotation == date:
                if param_default == inspect.Parameter.empty:
                    return self.date()
                return  self.of([self.date(), param_default])

            elif typing.get_origin(param_annotation) is typing.Union:
                nested_type = get_args(param_annotation)[0]
                return create_value(nested_type, param_default)

            elif typing.get_origin(param_annotation) is list:
                nested_type = get_args(param_annotation)[0]

                values = []
                for i in range(0, self.positiveInt(min=0, max=4)):
                    values.append(create_value(nested_type, param_default))

                if param_default == inspect.Parameter.empty:
                    return values
                return self.of(values, param_default)

            # composite values
            # ---------------
            else:
                return self.object_like(param_annotation)

        for param_name, param_type in parameters.items():
            if param_name != "self":
                param_values[param_name] = create_value(
                    param_type.annotation,
                    param_type.default
                )

        return class_of_interest(**param_values)
