import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SEED = PROJECT / 'seed.json'

ENV = {**os.environ, 'PYTHONPATH': str(PROJECT)}


def run_cli(args, file_arg):
    cmd = [sys.executable, '-m', 'stockroom', '--file', str(file_arg)] + args
    return subprocess.run(cmd, cwd=str(PROJECT), env=ENV, capture_output=True, text=True)


class StockroomCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.file = self.tmp / 'inv.json'
        shutil.copy(SEED, self.file)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_list_sorted(self):
        result = run_cli(['list'], self.file)
        self.assertEqual(result.returncode, 0)
        skus = [line.split('\t')[0] for line in result.stdout.splitlines()]
        self.assertEqual(skus, sorted(skus))
        self.assertEqual(len(skus), 6)

    def test_value_total(self):
        result = run_cli(['value'], self.file)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '1612.78')

    def test_value_location(self):
        result = run_cli(['value', 'A1'], self.file)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '257.38')

    def test_low_includes_equal(self):
        result = run_cli(['low'], self.file)
        self.assertEqual(result.returncode, 0)
        skus = [line.split('\t')[0] for line in result.stdout.splitlines()]
        self.assertEqual(skus, ['CD-200', 'GH-400', 'KL-600'])

    def test_remove_full_quantity_ok(self):
        result = run_cli(['remove', 'GH-400', '3'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(self.file.read_text())
        gh = next(i for i in data if i['sku'] == 'GH-400')
        self.assertEqual(gh['count'], 0)

    def test_remove_more_than_available_fails(self):
        result = run_cli(['remove', 'GH-400', '4'], self.file)
        self.assertEqual(result.returncode, 1)
        data = json.loads(self.file.read_text())
        gh = next(i for i in data if i['sku'] == 'GH-400')
        self.assertEqual(gh['count'], 3)

    def test_remove_unknown_sku_fails(self):
        result = run_cli(['remove', 'ZZ-999', '1'], self.file)
        self.assertEqual(result.returncode, 1)

    def test_add_merges_counts(self):
        result = run_cli(['add', 'AB-100', 'Alder Box', 'A1', '8', '19.99'], self.file)
        self.assertEqual(result.returncode, 0)
        data = json.loads(self.file.read_text())
        ab = next(i for i in data if i['sku'] == 'AB-100')
        self.assertEqual(ab['count'], 20)
        self.assertEqual(len(data), 6)

    def test_add_new_sku(self):
        result = run_cli(['add', 'MN-700', 'Maple Tray', 'D4', '4', '12.5'], self.file)
        self.assertEqual(result.returncode, 0)
        data = json.loads(self.file.read_text())
        mn = next(i for i in data if i['sku'] == 'MN-700')
        self.assertEqual(mn['count'], 4)
        self.assertEqual(mn['unit_price'], 12.5)
        self.assertEqual(len(data), 7)

    def test_move_moves_all_units(self):
        result = run_cli(['move', 'KL-600', 'D4'], self.file)
        self.assertEqual(result.returncode, 0)
        data = json.loads(self.file.read_text())
        kl = next(i for i in data if i['sku'] == 'KL-600')
        self.assertEqual(kl['location'], 'D4')
        self.assertEqual(kl['count'], 1)

    def test_move_unknown_sku_fails(self):
        result = run_cli(['move', 'ZZ-999', 'D4'], self.file)
        self.assertEqual(result.returncode, 1)

    def test_summary(self):
        result = run_cli(['summary'], self.file)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload,
            {'low_stock_count': 3, 'total_skus': 6, 'total_units': 37, 'total_value': 1612.78},
        )

    def test_summary_after_changes(self):
        run_cli(['remove', 'GH-400', '2'], self.file)
        result = run_cli(['summary'], self.file)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload,
            {'low_stock_count': 3, 'total_skus': 6, 'total_units': 35, 'total_value': 1595.28},
        )

    def test_non_positive_count_rejected(self):
        result = run_cli(['add', 'AB-100', 'Alder Box', 'A1', '0', '19.99'], self.file)
        self.assertEqual(result.returncode, 2)


class StockroomOpsImportTest(unittest.TestCase):
    def test_low_stock_boundary(self):
        from stockroom.data import Item
        from stockroom.ops import low_stock

        items = [Item('X-1', 'X', 'A1', 5, 1.0), Item('Y-2', 'Y', 'A1', 6, 1.0)]
        skus = [i.sku for i in low_stock(items, 5)]
        self.assertEqual(skus, ['X-1'])


if __name__ == '__main__':
    unittest.main()
