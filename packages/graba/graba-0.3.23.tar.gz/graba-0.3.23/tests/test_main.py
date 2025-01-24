from datetime import datetime
from typing import Optional, List

from graba.main import Any

any = Any()
def test_positiveNumber():
    def createData():
        return {
            "age": any.positiveInt(),
            "name": any.word()
        }


    result = any.listOf(
        min=3,
        max=7,
        factoryFunction=createData
    )
    print(result)
    # [
    #     {'age': 7323, 'name': 'vecalmzbdcvdwuqk'},
    #     {'age': 9705, 'name': 'bdqqpgtpgbfbci'},
    #     {'age': 9656, 'name': 'ojizqxl'}
    # ]


def test_anyFloat():
    result = any.anyFloat()
    print(result) # -520.9585233638023

def test_anySentence():
    result = any.sentence()
    print(result) # -520.9585233638023

def test_anyWord():
    result = any.word()
    print(result) # lpiqwzwyvcxuxbsaijdgtnvhhluj

def test_subsetOf():
    result = any.subsetOf(min=1, max=4, items=["a", "b", "c", "d", "e", "f"])
    print(result) # ['d', 'e', 'b']

def test_dateTimeBefore():
    result = any.dateTimeBefore(datetime(2015, 12, 25, 10, 30, 45))
    print(result) # 1994-10-22 10:30:45

    result = any.dateTimeBefore("2022-10-10")
    print(result) # 2000-03-16 00:00:00

    result = any.dateTimeBefore("2022-10-10 23:11:05")
    print(result) # 2016-12-28 23:11:05

def test_datetimebetween():
    result = any.datetimeBetween("2023-10-10", "2027-09-09")
    print(result) # 2025-08-10 22:00:19

def test_ip():
    print(any.ip()) # 250.127.163.208


def test_filepath():
    print(any.filepath()) # d/gfv/mctk/yjgz.pdf

def test_email():
    print(any.email()) # fivjby@fgs.es

def test_digits():
    print(any.digits(min=3, max=7)) # 53081
    print(any.digits(min=8, max=8)) # 64746287

def test_object_like():
    class Car:
        def __init__(self, color: str, engine_capacity: int, brand: str):
            self.color = color
            self.engine_capacity = engine_capacity
            self.brand = brand

        def __str__(self):
            return f"Car(color='{self.color}', engine_capacity='{self.engine_capacity}', brand='{self.brand}')"

    class Person:
        def __init__(self,
                     colors: List[str],
                     car: Car,
                     name: Optional[str] = "asdf",
                     age: int = None,
                 ):
            self.colors = colors
            self.name = name
            self.age = age
            self.car = car

        def __str__(self):
            return f"Person(colors='{self.colors}', name='{self.name}', age='{self.age}', car='{self.car}')"



    result: Person = any.object_like(Person)

    print(result.colors)
    print(result.name)
    print(result.age)
    print(result.car)
