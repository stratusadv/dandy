import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]


def _eval_testing_enabled() -> bool:
    value = os.environ.get('EVAL_TESTING')
    return value is not None and value not in ('', '0')


# In the checker container the task project is copied flat next to the hidden
# tests (seed.json at TASK/seed.json). In the repo the tests verify the
# reference solution: the task project overlaid with solution/ in a temp dir.
if _eval_testing_enabled() and not (TASK / 'seed.json').is_file():
    PROJECT = Path(tempfile.mkdtemp(prefix='dandy-eval-solution-'))
    shutil.copytree(TASK / 'project', PROJECT, dirs_exist_ok=True)
    for solution_file in (TASK / 'solution').rglob('*'):
        if solution_file.is_file():
            destination = PROJECT / 'stockroom' / solution_file.relative_to(TASK / 'solution')
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(solution_file, destination)
    SEED = TASK / 'project' / 'seed.json'
    sys.path.insert(0, str(PROJECT))
    atexit.register(shutil.rmtree, PROJECT, ignore_errors=True)
else:
    PROJECT = TASK
    SEED = TASK / 'seed.json'

ENV = {**os.environ, 'PYTHONPATH': str(PROJECT)}

SEED_REPORT = {
    'A1': {'skus': 22, 'units': 112, 'value': 382.73},
    'A2': {'skus': 21, 'units': 105, 'value': 385.57},
    'B1': {'skus': 21, 'units': 105, 'value': 378.42},
    'B2': {'skus': 21, 'units': 105, 'value': 366.26},
    'C1': {'skus': 21, 'units': 105, 'value': 389.12},
    'C2': {'skus': 21, 'units': 105, 'value': 376.97},
    'D1': {'skus': 21, 'units': 105, 'value': 374.81},
    'T1': {'skus': 1, 'units': 5, 'value': 0.18},
    'T2': {'skus': 1, 'units': 3, 'value': 0.08},
}

FIXTURE_SPLIT = [
    {'sku': 'F-1', 'name': 'F One', 'location': 'B1', 'count': 7, 'unit_price': 2.0},
    {'sku': 'F-1', 'name': 'F One', 'location': 'A1', 'count': 4, 'unit_price': 2.0},
    {'sku': 'F-2', 'name': 'F Two', 'location': 'A1', 'count': 2, 'unit_price': 3.25},
]

FIXTURE_INVALID = [
    {'sku': 'V-1', 'name': 'V One', 'location': 'A1', 'count': 3, 'unit_price': 1.0},
    {'sku': '', 'name': '', 'location': '', 'count': -1, 'unit_price': 0.0},
    {'sku': 'V-1', 'name': 'V One', 'location': 'A1', 'count': 5, 'unit_price': 1.0},
    {'sku': 'V-2', 'name': 'V Two A', 'location': 'A1', 'count': 2, 'unit_price': 2.0},
    {'sku': 'V-2', 'name': 'V Two B', 'location': 'B1', 'count': 2, 'unit_price': 2.5},
    {'sku': 'V-3', 'name': 'V Three', 'location': 'C1', 'count': 1, 'unit_price': -1.5},
]

FIXTURE_NIGHTLY = [
    {'sku': 'K-1', 'name': 'K One', 'location': 'A1', 'count': 4, 'unit_price': 2.5},
    {'sku': 'K-2', 'name': 'K Two', 'location': 'B1', 'count': 5, 'unit_price': 1.25},
    {'sku': 'K-3', 'name': 'K Three', 'location': 'C1', 'count': 6, 'unit_price': 0.9},
    {'sku': 'K-4', 'name': 'K Four', 'location': 'A1', 'count': 0, 'unit_price': 3.0},
]


def run_cli(args, file_arg):
    cmd = [sys.executable, '-m', 'stockroom', '--file', str(file_arg)] + args
    return subprocess.run(cmd, cwd=str(PROJECT), env=ENV, capture_output=True, text=True)


def run_nightly(file_arg):
    cmd = [sys.executable, str(PROJECT / 'tools' / 'nightly_restock.py'), '--file', str(file_arg)]
    return subprocess.run(cmd, cwd=str(PROJECT), env=ENV, capture_output=True, text=True)


def top_level_key_order(text):
    # Keys of the outermost JSON object in on-wire order, ignoring separators.
    order = []

    def _hook(pairs):
        order.append(pairs)
        return dict(pairs)

    json.loads(text, object_pairs_hook=_hook)
    return [key for key, _value in order[-1]]


# Skipped unless EVAL_TESTING is set to a non-empty, non-'0' value; the
# checker container exports EVAL_TESTING=1, and in-repo it runs the tests
# against the reference solution overlay above.
eval_test = unittest.skipUnless(
    _eval_testing_enabled(), 'Requires the EVAL_TESTING environment variable.'
)


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.file = self.tmp / 'inv.json'
        shutil.copy(SEED, self.file)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def rows(self):
        return json.loads(self.file.read_text())

    def rows_of(self, sku):
        return [row for row in self.rows() if row['sku'] == sku]

    def write_fixture(self, rows):
        path = self.tmp / 'fixture.json'
        path.write_text(json.dumps(rows, indent=2) + '\n')
        return path


@eval_test
class PricingMathTest(unittest.TestCase):
    def _rounded(self, text) -> str:
        from stockroom.pricing import format_money, round_money

        return format_money(round_money(Decimal(text)))

    def test_round_half_up_0175(self):
        self.assertEqual(self._rounded('0.175'), '0.18')

    def test_round_half_up_0075(self):
        self.assertEqual(self._rounded('0.075'), '0.08')

    def test_round_half_up_1005(self):
        self.assertEqual(self._rounded('1.005'), '1.01')

    def test_round_half_up_2675(self):
        self.assertEqual(self._rounded('2.675'), '2.68')

    def test_round_half_up_123455(self):
        self.assertEqual(self._rounded('123.455'), '123.46')

    def test_round_no_change(self):
        self.assertEqual(self._rounded('12.34'), '12.34')
        self.assertEqual(self._rounded('10'), '10.00')

    def test_line_value_exact(self):
        from stockroom.pricing import line_value

        self.assertEqual(line_value(5, 0.035), Decimal('0.175'))
        self.assertEqual(line_value(3, 0.025), Decimal('0.075'))


@eval_test
class OpsUnitTest(unittest.TestCase):
    def test_add_merges_existing_row(self):
        from stockroom.data import Item
        from stockroom.ops import add_stock

        items = [Item('S-1', 'S One', 'A1', 4, 1.5)]
        add_stock(items, 'S-1', 'S One', 'A1', 2, 1.5)
        self.assertEqual([item.count for item in items], [6])

    def test_add_creates_row(self):
        from stockroom.ops import add_stock

        items = []
        add_stock(items, 'S-3', 'S Three', 'Z9', 5, 9.99)
        self.assertEqual(
            [(item.sku, item.location, item.count, item.unit_price) for item in items],
            [('S-3', 'Z9', 5, 9.99)],
        )

    def test_add_conflicting_name_raises(self):
        from stockroom.data import Item
        from stockroom.ops import AttributeConflict, add_stock

        items = [Item('S-1', 'S One', 'A1', 4, 1.5)]
        with self.assertRaises(AttributeConflict):
            add_stock(items, 'S-1', 'Wrong Name', 'A1', 2, 1.5)
        self.assertEqual([item.count for item in items], [4])

    def test_add_conflicting_price_raises(self):
        from stockroom.data import Item
        from stockroom.ops import AttributeConflict, add_stock

        items = [Item('S-1', 'S One', 'A1', 4, 1.5)]
        with self.assertRaises(AttributeConflict):
            add_stock(items, 'S-1', 'S One', 'A1', 2, 1.6)
        self.assertEqual([item.count for item in items], [4])

    def test_add_split_new_location(self):
        from stockroom.data import Item
        from stockroom.ops import add_stock

        items = [Item('S-1', 'S One', 'A1', 4, 1.5)]
        add_stock(items, 'S-1', 'S One', 'B1', 3, 1.5)
        self.assertEqual([(item.location, item.count) for item in items], [('A1', 4), ('B1', 3)])

    def test_remove_exact_full_quantity(self):
        from stockroom.data import Item
        from stockroom.ops import remove_stock

        items = [Item('R-1', 'R One', 'A1', 6, 1.0)]
        remove_stock(items, 'R-1', 6)
        self.assertEqual([item.count for item in items], [0])

    def test_remove_more_than_available_raises(self):
        from stockroom.data import Item
        from stockroom.ops import InsufficientStock, remove_stock

        items = [Item('R-1', 'R One', 'A1', 6, 1.0)]
        with self.assertRaises(InsufficientStock):
            remove_stock(items, 'R-1', 7)
        self.assertEqual([item.count for item in items], [6])

    def test_remove_unknown_sku_raises(self):
        from stockroom.data import Item
        from stockroom.ops import InsufficientStock, remove_stock

        items = [Item('R-1', 'R One', 'A1', 6, 1.0)]
        with self.assertRaises(InsufficientStock):
            remove_stock(items, 'ZZ-9', 1)

    def test_remove_uses_explicit_location(self):
        from stockroom.data import Item
        from stockroom.ops import remove_stock

        items = [Item('R-1', 'R One', 'A1', 4, 1.0), Item('R-1', 'R One', 'B1', 3, 1.0)]
        remove_stock(items, 'R-1', 2, 'B1')
        self.assertEqual([(item.location, item.count) for item in items], [('A1', 4), ('B1', 1)])

    def test_remove_default_location_lexicographic_first(self):
        from stockroom.data import Item
        from stockroom.ops import remove_stock

        items = [Item('R-1', 'R One', 'B1', 3, 1.0), Item('R-1', 'R One', 'A1', 4, 1.0)]
        remove_stock(items, 'R-1', 3)
        self.assertEqual([(item.location, item.count) for item in items], [('B1', 3), ('A1', 1)])

    def test_remove_empty_location_raises(self):
        from stockroom.data import Item
        from stockroom.ops import InsufficientStock, remove_stock

        items = [Item('R-1', 'R One', 'A1', 4, 1.0)]
        with self.assertRaises(InsufficientStock):
            remove_stock(items, 'R-1', 1, 'C1')

    def test_move_merges_into_existing(self):
        from stockroom.data import Item
        from stockroom.ops import move_stock

        items = [Item('M-1', 'M One', 'A1', 5, 1.0), Item('M-1', 'M One', 'B1', 2, 1.0)]
        move_stock(items, 'M-1', 'A1', 'B1')
        self.assertEqual([(item.location, item.count) for item in items], [('A1', 0), ('B1', 7)])

    def test_move_no_source_stock_raises(self):
        from stockroom.data import Item
        from stockroom.ops import InsufficientStock, move_stock

        items = [Item('M-1', 'M One', 'A1', 5, 1.0)]
        with self.assertRaises(InsufficientStock):
            move_stock(items, 'M-1', 'C1', 'A1')

    def test_transfer_moves_exact_count(self):
        from stockroom.data import Item
        from stockroom.ops import transfer_stock

        items = [Item('T-9', 'T Nine', 'A1', 10, 2.0)]
        transfer_stock(items, 'T-9', 'A1', 'B1', 4)
        self.assertEqual([(item.location, item.count) for item in items], [('A1', 6), ('B1', 4)])

    def test_transfer_merges_into_existing(self):
        from stockroom.data import Item
        from stockroom.ops import transfer_stock

        items = [Item('T-9', 'T Nine', 'A1', 10, 2.0), Item('T-9', 'T Nine', 'B1', 4, 2.0)]
        transfer_stock(items, 'T-9', 'B1', 'A1', 2)
        self.assertEqual([(item.location, item.count) for item in items], [('A1', 12), ('B1', 2)])

    def test_transfer_insufficient_raises(self):
        from stockroom.data import Item
        from stockroom.ops import InsufficientStock, transfer_stock

        items = [Item('T-9', 'T Nine', 'A1', 10, 2.0)]
        with self.assertRaises(InsufficientStock):
            transfer_stock(items, 'T-9', 'A1', 'B1', 99)
        self.assertEqual([item.count for item in items], [10])

    def test_low_stock_single_row_boundary(self):
        from stockroom.data import Item
        from stockroom.ops import low_stock

        items = [Item('L-3', 'L Three', 'A1', 4, 1.0), Item('L-2', 'L Two', 'A1', 5, 1.0)]
        self.assertEqual(low_stock(items, 5), [('L-2', 5), ('L-3', 4)])

    def test_low_stock_uses_per_sku_totals(self):
        from stockroom.data import Item
        from stockroom.ops import low_stock

        split_at_threshold = [
            Item('L-1', 'L One', 'A1', 5, 1.0),
            Item('L-1', 'L One', 'B1', 1, 1.0),
        ]
        self.assertEqual(low_stock(split_at_threshold, 5), [])
        over_total = [Item('L-4', 'L Four', 'A1', 4, 1.0), Item('L-4', 'L Four', 'B1', 4, 1.0)]
        self.assertEqual(low_stock(over_total, 5), [])
        under_total = [Item('L-5', 'L Five', 'A1', 2, 1.0), Item('L-5', 'L Five', 'B1', 3, 1.0)]
        self.assertEqual(low_stock(under_total, 5), [('L-5', 5)])

    def test_total_value_exact(self):
        from stockroom.data import Item
        from stockroom.ops import total_value
        from stockroom.pricing import format_money

        trap = [Item('V-1', 'V One', 'A1', 5, 0.035)]
        self.assertEqual(format_money(total_value(trap)), '0.18')
        trap2 = [Item('V-2', 'V Two', 'B1', 3, 0.025)]
        self.assertEqual(format_money(total_value(trap2)), '0.08')
        both = trap + trap2
        self.assertEqual(format_money(total_value(both)), '0.25')

    def test_sku_total(self):
        from stockroom.data import Item
        from stockroom.ops import sku_total

        items = [Item('S-1', 'S One', 'A1', 4, 1.0), Item('S-1', 'S One', 'B1', 3, 1.0)]
        self.assertEqual(sku_total(items, 'S-1'), 7)
        self.assertEqual(sku_total(items, 'ZZ-9'), 0)


@eval_test
class LoaderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_legacy_seed(self):
        from stockroom.data import load_items

        items = load_items(SEED)
        self.assertEqual(len(items), 150)
        a001 = next(item for item in items if item.sku == 'A-001')
        self.assertEqual(
            (a001.name, a001.location, a001.count, a001.unit_price),
            ('Alder Part 001', 'A1', 4, 1.11),
        )
        t001 = next(item for item in items if item.sku == 'T-001')
        self.assertEqual((t001.location, t001.count, t001.unit_price), ('T1', 5, 0.035))

    def test_load_split_file(self):
        from stockroom.data import load_items

        path = self.tmp / 'split.json'
        path.write_text(json.dumps(FIXTURE_SPLIT, indent=2) + '\n')
        items = load_items(path)
        self.assertEqual(len(items), 3)
        self.assertEqual(
            [(item.sku, item.location) for item in items],
            [('F-1', 'B1'), ('F-1', 'A1'), ('F-2', 'A1')],
        )

    def test_save_drops_zero_and_sorts(self):
        from stockroom.data import Item, save_items

        items = [
            Item('B-1', 'B One', 'Z9', 3, 1.0),
            Item('A-1', 'A One', 'B1', 0, 2.0),
            Item('B-1', 'B One', 'A1', 2, 1.0),
        ]
        path = self.tmp / 'out.json'
        save_items(path, items)
        rows = json.loads(path.read_text())
        self.assertEqual(
            [(row['sku'], row['location'], row['count']) for row in rows],
            [('B-1', 'A1', 2), ('B-1', 'Z9', 3)],
        )

    def test_save_load_round_trip(self):
        from stockroom.data import load_items, save_items

        items = load_items(SEED)
        path = self.tmp / 'round.json'
        save_items(path, items)
        again = load_items(path)
        self.assertEqual(
            [(item.sku, item.location, item.count) for item in again],
            [(item.sku, item.location, item.count) for item in items],
        )
        self.assertEqual(
            [(item.sku, item.location) for item in again],
            sorted((item.sku, item.location) for item in again),
        )

    def test_load_missing_file(self):
        from stockroom.data import load_items

        self.assertEqual(load_items(self.tmp / 'nope.json'), [])


@eval_test
class CliContractTest(CliTestCase):
    def test_list_sorted_full_seed(self):
        result = run_cli(['list'], self.file)
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 150)
        self.assertEqual(lines, sorted(lines))
        self.assertEqual(lines[0], 'A-001\tA1\tAlder Part 001\t4\t1.11')
        self.assertEqual(lines[49], 'A-050\tA1\tMaple Housing 050\t5\t4.44')
        self.assertEqual(lines[50], 'B-001\tA2\tAlder Part 001\t6\t4.61')
        self.assertEqual(lines[147], 'C-048\tA1\tJuniper Gasket 048\t7\t2.15')
        self.assertEqual(lines[148], 'T-001\tT1\tWalnut Trap 001\t5\t0.04')
        self.assertEqual(lines[149], 'T-002\tT2\tWalnut Trap 002\t3\t0.03')

    def test_value_total(self):
        result = run_cli(['value'], self.file)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '2654.13')

    def test_value_location(self):
        self.assertEqual(run_cli(['value', 'A1'], self.file).stdout.strip(), '382.73')
        self.assertEqual(run_cli(['value', 'B2'], self.file).stdout.strip(), '366.26')

    def test_value_trap_locations(self):
        self.assertEqual(run_cli(['value', 'T1'], self.file).stdout.strip(), '0.18')
        self.assertEqual(run_cli(['value', 'T2'], self.file).stdout.strip(), '0.08')

    def test_low_default(self):
        result = run_cli(['low'], self.file)
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 100)
        self.assertEqual(lines[0], 'A-001\t4')
        self.assertEqual(lines[1], 'A-002\t5')
        self.assertEqual(lines[-1], 'T-002\t3')

    def test_low_threshold_6(self):
        result = run_cli(['low', '6'], self.file)
        self.assertEqual(len(result.stdout.splitlines()), 149)

    def test_low_threshold_0(self):
        self.assertEqual(run_cli(['low', '0'], self.file).stdout, '')

    def test_add_merges(self):
        result = run_cli(['add', 'A-001', 'Alder Part 001', 'A1', '10', '1.11'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.rows()), 150)
        self.assertEqual(
            self.rows_of('A-001'),
            [
                {
                    'sku': 'A-001',
                    'name': 'Alder Part 001',
                    'location': 'A1',
                    'count': 14,
                    'unit_price': 1.11,
                }
            ],
        )

    def test_add_new_sku(self):
        result = run_cli(['add', 'Z-900', 'Zebra Test 001', 'Z9', '4', '12.5'], self.file)
        self.assertEqual(result.returncode, 0)
        rows = self.rows()
        self.assertEqual(len(rows), 151)
        self.assertEqual(
            rows[-1],
            {
                'sku': 'Z-900',
                'name': 'Zebra Test 001',
                'location': 'Z9',
                'count': 4,
                'unit_price': 12.5,
            },
        )

    def test_add_conflicting_name_exit_1(self):
        before = self.file.read_text()
        result = run_cli(['add', 'A-001', 'Wrong Name', 'A1', '10', '1.11'], self.file)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.file.read_text(), before)

    def test_add_conflicting_price_exit_1(self):
        before = self.file.read_text()
        result = run_cli(['add', 'A-001', 'Alder Part 001', 'A1', '10', '1.12'], self.file)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.file.read_text(), before)

    def test_add_non_positive_count_exit_2(self):
        self.assertEqual(
            run_cli(['add', 'A-001', 'Alder Part 001', 'A1', '0', '1.11'], self.file).returncode, 2
        )

    def test_add_non_positive_price_exit_2(self):
        self.assertEqual(
            run_cli(['add', 'Z-900', 'Zebra Test 001', 'Z9', '4', '0'], self.file).returncode, 2
        )

    def test_remove_full_quantity(self):
        result = run_cli(['remove', 'T-002', '3'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = self.rows()
        self.assertEqual(len(rows), 149)
        self.assertEqual(self.rows_of('T-002'), [])

    def test_remove_full_quantity_explicit_location(self):
        result = run_cli(['remove', 'T-001', '5', 'T1'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.rows_of('T-001'), [])

    def test_remove_more_than_available_exit_1(self):
        before = self.file.read_text()
        result = run_cli(['remove', 'A-001', '5'], self.file)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.file.read_text(), before)

    def test_remove_unknown_sku_exit_1(self):
        self.assertEqual(run_cli(['remove', 'ZZ-999', '1'], self.file).returncode, 1)

    def test_remove_empty_location_exit_1(self):
        before = self.file.read_text()
        result = run_cli(['remove', 'A-001', '1', 'Z9'], self.file)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.file.read_text(), before)

    def test_remove_non_positive_count_exit_2(self):
        before = self.file.read_text()
        self.assertEqual(run_cli(['remove', 'A-001', '0'], self.file).returncode, 2)
        self.assertEqual(run_cli(['remove', 'A-001', '-2'], self.file).returncode, 2)
        self.assertEqual(self.file.read_text(), before)

    def test_move_into_new_location(self):
        result = run_cli(['move', 'A-001', 'A1', 'A9'], self.file)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            self.rows_of('A-001'),
            [
                {
                    'sku': 'A-001',
                    'name': 'Alder Part 001',
                    'location': 'A9',
                    'count': 4,
                    'unit_price': 1.11,
                }
            ],
        )

    def test_move_same_location_exit_2(self):
        before = self.file.read_text()
        self.assertEqual(run_cli(['move', 'A-001', 'A1', 'A1'], self.file).returncode, 2)
        self.assertEqual(self.file.read_text(), before)

    def test_move_no_stock_exit_1(self):
        before = self.file.read_text()
        self.assertEqual(run_cli(['move', 'A-001', 'B9', 'A1'], self.file).returncode, 1)
        self.assertEqual(self.file.read_text(), before)

    def test_low_negative_threshold_exit_2(self):
        self.assertEqual(run_cli(['low', '-1'], self.file).returncode, 2)

    def test_unknown_command_exit_2(self):
        self.assertEqual(run_cli(['frobnicate'], self.file).returncode, 2)


@eval_test
class MissingCommandsTest(CliTestCase):
    def test_transfer_creates_row(self):
        path = self.write_fixture(FIXTURE_SPLIT)
        result = run_cli(['transfer', 'F-1', 'B1', 'A1', '3'], path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(path.read_text()),
            [
                {'sku': 'F-1', 'name': 'F One', 'location': 'A1', 'count': 7, 'unit_price': 2.0},
                {'sku': 'F-1', 'name': 'F One', 'location': 'B1', 'count': 4, 'unit_price': 2.0},
                {'sku': 'F-2', 'name': 'F Two', 'location': 'A1', 'count': 2, 'unit_price': 3.25},
            ],
        )

    def test_transfer_exact_full_quantity(self):
        path = self.write_fixture(FIXTURE_SPLIT)
        result = run_cli(['transfer', 'F-1', 'B1', 'A1', '7'], path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(path.read_text()),
            [
                {'sku': 'F-1', 'name': 'F One', 'location': 'A1', 'count': 11, 'unit_price': 2.0},
                {'sku': 'F-2', 'name': 'F Two', 'location': 'A1', 'count': 2, 'unit_price': 3.25},
            ],
        )

    def test_transfer_more_than_available_exit_1(self):
        path = self.write_fixture(FIXTURE_SPLIT)
        result = run_cli(['transfer', 'F-1', 'B1', 'A1', '8'], path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(path.read_text()), FIXTURE_SPLIT)

    def test_transfer_same_location_exit_2(self):
        path = self.write_fixture(FIXTURE_SPLIT)
        self.assertEqual(run_cli(['transfer', 'F-1', 'A1', 'A1', '1'], path).returncode, 2)

    def test_transfer_non_positive_count_exit_2(self):
        path = self.write_fixture(FIXTURE_SPLIT)
        self.assertEqual(run_cli(['transfer', 'F-1', 'A1', 'B1', '0'], path).returncode, 2)

    def test_summary_seed(self):
        result = run_cli(['summary'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {'low_stock_count': 100, 'total_skus': 150, 'total_units': 750, 'total_value': 2654.13},
        )

    def test_summary_fixture(self):
        path = self.write_fixture(FIXTURE_SPLIT)
        result = run_cli(['summary'], path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {'low_stock_count': 1, 'total_skus': 2, 'total_units': 13, 'total_value': 28.5},
        )

    def test_summary_after_remove_full_quantity(self):
        result = run_cli(['remove', 'T-002', '3'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(run_cli(['summary'], self.file).stdout),
            {'low_stock_count': 99, 'total_skus': 149, 'total_units': 747, 'total_value': 2654.05},
        )

    def test_summary_empty(self):
        path = self.write_fixture([])
        result = run_cli(['summary'], path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(
            json.loads(result.stdout),
            {'low_stock_count': 0, 'total_skus': 0, 'total_units': 0, 'total_value': 0.0},
        )

    def test_report_seed(self):
        result = run_cli(['report'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), SEED_REPORT)
        self.assertEqual(top_level_key_order(result.stdout), sorted(SEED_REPORT))

    def test_report_fixture(self):
        path = self.write_fixture(FIXTURE_SPLIT)
        result = run_cli(['report'], path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                'A1': {'skus': 2, 'units': 6, 'value': 14.5},
                'B1': {'skus': 1, 'units': 7, 'value': 14.0},
            },
        )
        # The fixture's first row is in B1, so a first-appearance-order
        # implementation prints B1 before A1; the spec demands location order.
        self.assertEqual(top_level_key_order(result.stdout), ['A1', 'B1'])

    def test_report_after_move(self):
        result = run_cli(['move', 'A-001', 'A1', 'A2'], self.file)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(run_cli(['report'], self.file).stdout)
        self.assertEqual(payload['A1'], {'skus': 21, 'units': 108, 'value': 378.29})
        self.assertEqual(payload['A2'], {'skus': 22, 'units': 109, 'value': 390.01})

    def test_report_empty(self):
        path = self.write_fixture([])
        result = run_cli(['report'], path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {})

    def test_validate_clean(self):
        result = run_cli(['validate'], self.file)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr, '')
        path = self.write_fixture([])
        self.assertEqual(run_cli(['validate'], path).returncode, 0)

    def test_validate_duplicate_rows(self):
        path = self.write_fixture(
            [
                {'sku': 'D-1', 'name': 'D One', 'location': 'A1', 'count': 3, 'unit_price': 1.0},
                {'sku': 'D-1', 'name': 'D One', 'location': 'A1', 'count': 5, 'unit_price': 1.0},
            ]
        )
        result = run_cli(['validate'], path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, 'INVALID: row 1 duplicates (sku, location) of row 0\n')

    def test_validate_violations(self):
        path = self.write_fixture(FIXTURE_INVALID)
        result = run_cli(['validate'], path)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.splitlines(),
            [
                'INVALID: row 1 has empty sku',
                'INVALID: row 1 has empty name',
                'INVALID: row 1 has empty location',
                'INVALID: row 1 has negative count',
                'INVALID: row 1 has non-positive price',
                'INVALID: row 2 duplicates (sku, location) of row 0',
                'INVALID: row 5 has non-positive price',
                'INVALID: sku V-2 has inconsistent name',
                'INVALID: sku V-2 has inconsistent price',
            ],
        )


@eval_test
class SequenceTest(CliTestCase):
    def test_add_transfer_remove_value_summary(self):
        self.assertEqual(
            run_cli(['add', 'A-001', 'Alder Part 001', 'A2', '6', '1.11'], self.file).returncode, 0
        )
        self.assertEqual(run_cli(['transfer', 'A-001', 'A2', 'A1', '4'], self.file).returncode, 0)
        self.assertEqual(run_cli(['remove', 'A-001', '2'], self.file).returncode, 0)
        self.assertEqual(
            self.rows_of('A-001'),
            [
                {
                    'sku': 'A-001',
                    'name': 'Alder Part 001',
                    'location': 'A1',
                    'count': 6,
                    'unit_price': 1.11,
                },
                {
                    'sku': 'A-001',
                    'name': 'Alder Part 001',
                    'location': 'A2',
                    'count': 2,
                    'unit_price': 1.11,
                },
            ],
        )
        self.assertEqual(run_cli(['value'], self.file).stdout.strip(), '2658.57')
        self.assertEqual(
            json.loads(run_cli(['summary'], self.file).stdout),
            {'low_stock_count': 99, 'total_skus': 150, 'total_units': 754, 'total_value': 2658.57},
        )

    def test_transfer_preserves_value(self):
        self.assertEqual(run_cli(['transfer', 'A-001', 'A1', 'B1', '2'], self.file).returncode, 0)
        self.assertEqual(run_cli(['value'], self.file).stdout.strip(), '2654.13')

    def test_move_merge_preserves_value(self):
        b001 = self.rows_of('B-001')[0]
        self.assertEqual(
            run_cli(
                ['add', 'B-001', b001['name'], 'B2', '7', str(b001['unit_price'])], self.file
            ).returncode,
            0,
        )
        self.assertEqual(
            run_cli(['move', 'B-001', b001['location'], 'B2'], self.file).returncode, 0
        )
        self.assertEqual(
            self.rows_of('B-001'),
            [
                {
                    'sku': 'B-001',
                    'name': 'Alder Part 001',
                    'location': 'B2',
                    'count': 13,
                    'unit_price': 4.61,
                }
            ],
        )
        self.assertEqual(run_cli(['value'], self.file).stdout.strip(), '2686.40')
        result = run_cli(['validate'], self.file)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, '')

    def test_low_reports_per_sku_total_after_split(self):
        self.assertEqual(
            run_cli(['add', 'A-001', 'Alder Part 001', 'A2', '1', '1.11'], self.file).returncode, 0
        )
        lines = run_cli(['low'], self.file).stdout.splitlines()
        self.assertIn('A-001\t5', lines)
        self.assertNotIn('A-001\t4', lines)

    def test_reloaded_state_keeps_split_rows(self):
        self.assertEqual(
            run_cli(['add', 'A-001', 'Alder Part 001', 'A2', '6', '1.11'], self.file).returncode, 0
        )
        lines = run_cli(['list'], self.file).stdout.splitlines()
        a001 = [line for line in lines if line.startswith('A-001\t')]
        self.assertEqual(
            a001, ['A-001\tA1\tAlder Part 001\t4\t1.11', 'A-001\tA2\tAlder Part 001\t6\t1.11']
        )


@eval_test
class NightlyRestockTest(CliTestCase):
    def test_restocks_low_skus(self):
        path = self.write_fixture(FIXTURE_NIGHTLY)
        result = run_nightly(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'restocked K-1 +10\nrestocked K-2 +10\n')
        self.assertEqual(
            json.loads(path.read_text()),
            [
                {'sku': 'K-1', 'name': 'K One', 'location': 'A1', 'count': 14, 'unit_price': 2.5},
                {'sku': 'K-2', 'name': 'K Two', 'location': 'B1', 'count': 15, 'unit_price': 1.25},
                {'sku': 'K-3', 'name': 'K Three', 'location': 'C1', 'count': 6, 'unit_price': 0.9},
            ],
        )

    def test_second_run_noop(self):
        path = self.write_fixture(FIXTURE_NIGHTLY)
        run_nightly(path)
        second = run_nightly(path)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(second.stdout, '')

    def test_restocks_seed_scale(self):
        result = run_nightly(self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 100)
        self.assertEqual(lines[0], 'restocked A-001 +10')
        self.assertEqual(lines[-1], 'restocked T-002 +10')
        self.assertEqual(
            json.loads(run_cli(['summary'], self.file).stdout),
            {'low_stock_count': 0, 'total_skus': 150, 'total_units': 1750, 'total_value': 6171.03},
        )


@eval_test
class LegacyReportTest(unittest.TestCase):
    def test_render_exact_output(self):
        from stockroom.data import Item
        from stockroom.legacy_report import render

        items = [
            Item('A-001', 'Alder Part 001', 'A1', 12, 19.99),
            Item('T-001', 'Walnut Trap 001', 'T1', 5, 0.035),
        ]
        self.assertEqual(
            render(items),
            'STOCKROOM LEGACY REPORT\n'
            '======================\n'
            'sku,location,name,count,unit_price,value\n'
            'A-001,A1,Alder Part 001,12,19.99,239\n'
            'T-001,T1,Walnut Trap 001,5,0.035,0\n'
            'TOTAL,239\n',
        )


if __name__ == '__main__':
    unittest.main()
