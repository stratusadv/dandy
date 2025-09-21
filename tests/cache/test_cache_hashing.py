import time
import uuid
from dataclasses import dataclass
from unittest import TestCase

from pydantic import BaseModel

from dandy.cache.utils import convert_to_hashable_str, generate_cache_key

from tests.intel.intelligence.intel import PersonIntel, BagIntel, ThingIntel

@dataclass
class Puppet:
    name: str
    is_fuzzy: bool


class Treasure(BaseModel):
    quantity: int
    quality: float
    contains_puppet: bool = False


class Mushroom:
    def __init__(self, color: str):
        self.color = color


def mushroom_to_treasure(color: str, puppet: Puppet | None = None):
    return Treasure(
        quantity=len(color),
        quality=4.5,
        contains_puppet=bool(puppet)
    )


class TestCacheHashing(TestCase):
    def setUp(self):
        self.puppet = Puppet(
            name='Batman',
            is_fuzzy=True
        )
        self.treasure = Treasure(
            quantity=456,
            quality=7.8
        )
        self.built_ins = [
            1,
            1.0,
            '1',
            '1.0',
            True,
            False,
            None,
            [1, 2, 3],
            {'a': 1, 'b': 2},
            (1, 2, 3),
            {'a', 'b', 'c'}
        ]

    def test_built_ins_hashing(self):

        converted_built_ins = []

        for built_in in self.built_ins:
            converted_built_ins.append(
                convert_to_hashable_str(built_in)
            )

        self.assertEqual(
            len(self.built_ins),
            len(converted_built_ins),
        )

    def test_data_class_hashing(self):
        converted_puppet = convert_to_hashable_str(self.puppet)

        self.assertEqual(
            converted_puppet,
            "{'name': 'Batman', 'is_fuzzy': 'True'}"
        )

    def test_pydantic_model_hashing(self):
        converted_treasure = convert_to_hashable_str(self.treasure)

        self.assertEqual(
            converted_treasure,
            "{'quantity': 456, 'quality': 7.8, 'contains_puppet': False}"
        )

    def test_class_hashing(self):
        classes = [
            Mushroom,
            Treasure,
            Puppet,
        ]

        converted_classes = []

        for cls in classes:
            converted_classes.append(
                convert_to_hashable_str(cls)
            )

        self.assertEqual(
            len(classes),
            len(converted_classes)
        )

    def cache_key_performance_test(self) -> float:
        args = (
            self.puppet,
            Puppet,
            self.treasure,
            uuid.uuid4(),
            Treasure,
            {
                'treasure': self.treasure,
                'puppet': self.puppet,
                'mushroom': Mushroom('brown'),
                'person': PersonIntel(
                    first_name='John',
                    middle_name='Smith',
                    last_name='Doe',
                    age=30,
                    bag=BagIntel(
                        color='red',
                        stylish=True,
                        pockets=1,
                        things=[
                            ThingIntel(
                                name='taco',
                                description='a delicious taco'
                            ),
                            ThingIntel(
                                name='carrot',
                                description='a delicious carrot full of fibre'
                            )
                        ]
                    )
                ),
            },
            Mushroom,
        ) + tuple(self.built_ins)

        kwargs = {
            'purple_mushrooms': Mushroom('purple'),
            'some_treasure': Treasure(
                quantity=123,
                quality=4.5
            ),
            'mushroom_class': Mushroom,
            'built_ins': (built_in for built_in in self.built_ins),
        }

        start_time = time.perf_counter()

        _ = generate_cache_key(
            mushroom_to_treasure,
            *args,
            **kwargs,
        )

        end_time = time.perf_counter()

        return end_time - start_time

    def test_cache_key_generation(self):
        try:
            self.cache_key_performance_test()
        except Exception as e:
            self.fail(f'Failed to generate cache key: {e}')


    def test_matched_key_generation(self):
        first_puppet = Puppet(
            name='Bat Sir',
            is_fuzzy=True
        )

        first_cache_key = generate_cache_key(
            mushroom_to_treasure,
            'aquamarine',
            puppet=first_puppet,
        )

        matched_puppet = Puppet(
            name='Bat Sir',
            is_fuzzy=True
        )

        matched_cache_key = generate_cache_key(
            mushroom_to_treasure,
            'aquamarine',
            puppet=matched_puppet,
        )

        unmatched_puppet = Puppet(
            name='Snake Girl',
            is_fuzzy=True
        )

        unmanaged_cache_key = generate_cache_key(
            mushroom_to_treasure,
            'aquamarine',
            puppet=unmatched_puppet,
        )

        self.assertEqual(first_cache_key, matched_cache_key)
        self.assertNotEqual(first_cache_key, unmanaged_cache_key)


    def test_hashing_performance(self):
        timing = []

        for _ in range(1000):
            timing.append(
                self.cache_key_performance_test()
            )

        average_time = sum(timing) / len(timing)

        print(f'Average time: {average_time}')

        self.assertLess(average_time, 0.001)



