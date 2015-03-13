from ...strategies import (
    drop_unspecified_subcategories,
    normalize_biosphere_categories,
    normalize_biosphere_names,
    strip_biosphere_exc_locations,
)
from ...data import (
    get_biosphere_2_3_name_migration_data,
    get_biosphere_2_3_category_migration_data,
)
from ...errors import StrategyError
from ...migrations import Migration
from bw2data import Database
from bw2data.tests import BW2DataTest
import copy
import unittest


class BiosphereNameNormalizationTestCase(BW2DataTest):
    def extra_setup(self):
        Migration("biosphere-2-3-names").write(
            get_biosphere_2_3_name_migration_data(),
            u"Change biosphere flow names to ecoinvent version 3"
        )

    def test_normalize_ds_name(self):
        ds = [{
            'categories': ['air'],
            'name': "Carbon dioxide, biogenic",
            'unit': 'kilogram',
            'type': "emission",
        }]
        expected = [{
            'categories': ['air'],
            'name': "Carbon dioxide, non-fossil",
            'unit': 'kilogram',
            'type': "emission",
        }]
        self.assertEqual(
            expected,
            normalize_biosphere_names(ds)
        )

    def test_normalize_ds_name_no_unit(self):
        ds = [{
            'categories': ['air'],
            'name': "Carbon dioxide, biogenic",
            'type': "emission",
        }]
        self.assertEqual(
            ds,
            normalize_biosphere_names(copy.deepcopy(ds))
        )

    def test_normalize_ds_name_not_emission(self):
        ds = [{
            'categories': ['air'],
            'name': "Carbon dioxide, biogenic",
            'unit': 'kilogram',
        }]
        self.assertEqual(
            ds,
            normalize_biosphere_names(copy.deepcopy(ds))
        )

    def test_normalize_ds_name_no_category(self):
        ds = [{
            'name': "Carbon dioxide, biogenic",
            'type': "emission",
        }]
        self.assertEqual(
            ds,
            normalize_biosphere_names(copy.deepcopy(ds))
        )

    def test_normalize_exc_name(self):
        ds = [{
            'exchanges': [{
                'categories': ['air'],
                'name': "Carbon dioxide, biogenic",
                'unit': 'kilogram',
                'type': "biosphere",
            }]
        }]
        expected = [{
            'exchanges': [{
                'categories': ['air'],
                'name': "Carbon dioxide, non-fossil",
                'unit': 'kilogram',
                'type': "biosphere",
            }]
        }]
        self.assertEqual(
            expected,
            normalize_biosphere_names(ds)
        )

    def test_normalize_exc_name_already_linked(self):
        ds = [{
            'exchanges': [{
                'categories': ['air'],
                'name': "Carbon dioxide, biogenic",
                'type': "biosphere",
                'unit': 'kilogram',
                'input': ('foo', 'bar'),
            }]
        }]
        expected = [{
            'exchanges': [{
                'categories': ['air'],
                'name': "Carbon dioxide, non-fossil",
                'type': "biosphere",
                'unit': 'kilogram',
                'input': ('foo', 'bar'),
            }]
        }]
        self.assertEqual(
            expected,
            normalize_biosphere_names(ds)
        )

    def test_normalize_exc_name_not_biosphere(self):
        ds = [{
            'exchanges': [{
                'categories': ['air'],
                'name': "Carbon dioxide, biogenic",
                'unit': 'kilogram',
            }]
        }]
        self.assertEqual(
            ds,
            normalize_biosphere_names(copy.deepcopy(ds))
        )

    def test_normalize_exc_name_no_category(self):
        ds = [{
            'exchanges': [{
                'type': "biosphere",
                'name': "Carbon dioxide, biogenic",
            }]
        }]
        self.assertEqual(
            ds,
            normalize_biosphere_names(copy.deepcopy(ds))
        )


class BiosphereCategoryNormalizationTestCase(BW2DataTest):
    def extra_setup(self):
        Migration("biosphere-2-3-categories").write(
            get_biosphere_2_3_category_migration_data(),
            u"Change biosphere category and subcategory labels to ecoinvent version 3"
        )

    def test_no_categories(self):
        ds = [{'name': 'foo'}]
        self.assertEqual(
            copy.deepcopy(ds),
            normalize_biosphere_categories(ds)
        )

    def test_ds_wrong_type(self):
        ds = [{
            'categories': ('resource', 'in ground'),
            'type': 'process'
        }]
        self.assertEqual(
            copy.deepcopy(ds),
            normalize_biosphere_categories(ds)
        )

    def test_ds(self):
        ds = [
            {
                'categories': ('resource', 'in ground'),
                'type': 'emission'
            },  {
                'categories': ('resource', 'all around'),
                'type': 'emission'
            }
        ]
        expected = [
            {
                'categories': [u'natural resource', u'in ground'],
                'type': 'emission'
            }, {
                'categories': ('resource', 'all around'),
                'type': 'emission'
            }
        ]
        self.assertEqual(
            expected,
            normalize_biosphere_categories(ds)
        )

    def test_exc_no_categories(self):
        ds = [{
            'exchanges': [{'name': 'foo'}]
        }]
        self.assertEqual(
            copy.deepcopy(ds),
            normalize_biosphere_categories(ds)
        )

    def test_exc(self):
        ds = [{
            'exchanges': [
                {
                    'categories': ('resource', 'in ground'),
                    'type': 'biosphere',
                }, {
                    'categories': ('resource', 'all around'),
                    'type': 'biosphere'
                }
            ]
        }]
        expected = [{
            'exchanges': [
                {
                    'categories': [u'natural resource', u'in ground'],
                    'type': 'biosphere',
                }, {
                    'categories': ('resource', 'all around'),
                    'type': 'biosphere'
                }
            ]
        }]
        self.assertEqual(
            expected,
            normalize_biosphere_categories(ds)
        )


class UnspecifiedCategoryTestCase(unittest.TestCase):
    def test_ds_no_categories(self):
        ds = [{'name': 'foo'}]
        self.assertEqual(
            copy.deepcopy(ds),
            drop_unspecified_subcategories(ds)
        )

    def test_ds_wrong_type(self):
        ds = [{'categories': ('foo', 'unspecified')}]
        self.assertEqual(
            copy.deepcopy(ds),
            drop_unspecified_subcategories(ds)
        )

    def test_ds_wrong_categories_length(self):
        ds = [{
            'categories': ('foo', 'unspecified', 'bar'),
            'type': 'emission'
        }]
        self.assertEqual(
            copy.deepcopy(ds),
            drop_unspecified_subcategories(ds)
        )
        ds = [{
            'categories': ('foo', ),
            'type': 'emission'
        }]
        self.assertEqual(
            copy.deepcopy(ds),
            drop_unspecified_subcategories(ds)
        )

    def test_ds(self):
        ds = [
            {
                'categories': ('foo', 'unspecified'),
                'type': 'emission'
            }, {
                'categories': ('foo', 'bar'),
                'type': 'emission'
            }, {
                'categories': ('foo', '(unspecified)'),
                'type': 'emission'
            }, {
                'categories': ('foo', None),
                'type': 'emission'
            }, {
                'categories': ('foo', ''),
                'type': 'emission'
            }
        ]
        expected = [
            {
                'categories': ('foo',),
                'type': 'emission'
            }, {
                'categories': ('foo', 'bar'),
                'type': 'emission'
            }, {
                'categories': ('foo',),
                'type': 'emission'
            }, {
                'categories': ('foo',),
                'type': 'emission'
            }, {
                'categories': ('foo',),
                'type': 'emission'
            }
        ]
        self.assertEqual(
            expected,
            drop_unspecified_subcategories(ds)
        )

    def test_exc_no_categories(self):
        ds = [{
            'exchanges': [{
                'name': 'foo'
            }]
        }]
        self.assertEqual(
            copy.deepcopy(ds),
            drop_unspecified_subcategories(ds)
        )

    def test_exc_wrong_type(self):
        ds = [{
            'exchanges': [{
                'categories': ('foo', 'unspecified')
            }]
        }]
        self.assertEqual(
            copy.deepcopy(ds),
            drop_unspecified_subcategories(ds)
        )

    def test_exc_wrong_categories_length(self):
        ds = [{
            'exchanges': [{
                'categories': ('foo', 'unspecified', 'bar'),
                'type': 'biosphere'
            }]
        }]
        self.assertEqual(
            copy.deepcopy(ds),
            drop_unspecified_subcategories(ds)
        )

    def test_exc(self):
        ds = [{
            'exchanges': [
                {
                    'categories': ('foo', 'unspecified'),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', 'bar'),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', '(unspecified)'),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', ''),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', None),
                    'type': 'biosphere'
                }
            ]
        }]
        expected = [{
            'exchanges': [
                {
                    'categories': ('foo', ),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', 'bar'),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', ),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', ),
                    'type': 'biosphere'
                }, {
                    'categories': ('foo', ),
                    'type': 'biosphere'
                }
            ]
        }]
        self.assertEqual(
            expected,
            drop_unspecified_subcategories(ds)
        )


class BiosphereLinkingTestCase(BW2DataTest):
    def create_biosphere(self):
        db = Database("biosphere")
        data = {
            ('biosphere', 'oxygen'): {
                'name': 'oxygen',
                'unit': 'kilogram',
                'type': 'emission',
            },
            ('biosphere', 'argon'): {
                'name': 'argon',
                'unit': 'kilogram',
                'type': 'emission',
            },
            ('biosphere', 'nitrogen'): {
                'name': 'nitrogen',
                'unit': 'kilogram'
            },
        }
        db.register()
        db.write(data)

    def test_strip_biosphere_exc_location(self):
        data = [{
            'exchanges': [{
                'name': 'Boron trifluoride',
                'categories': ('air',),
                'unit': 'kilogram',
                'type': 'biosphere',
                'location': 'GLO',
            }, {
                'name': 'Boron trifluoride',
                'categories': ('air', 'another'),
                'unit': 'kilogram',
                'type': 'biosphere',
                'location': 'GLO',
            }]
        }]
        expected = [{
            'exchanges': [{
                'name': 'Boron trifluoride',
                'categories': ('air',),
                'unit': 'kilogram',
                'type': 'biosphere',
            }, {
                'name': 'Boron trifluoride',
                'categories': ('air', 'another'),
                'unit': 'kilogram',
                'type': 'biosphere',
            }]
        }]
        self.assertEqual(
            expected,
            strip_biosphere_exc_locations(data)
        )

    # Tests covered by link_iter (link_iterable.py)
    # def test_force_rewrites_links(self):
    #     self.create_biosphere()
    #     data = [
    #         {
    #             'exchanges': [{
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #                 'input': ('foo', 'bar')
    #             }]
    #         }
    #     ]
    #     expected = [
    #         {
    #             'exchanges': [{
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #                 'input': ('biosphere', 'oxygen')
    #             }]
    #         }
    #     ]
    #     self.assertEqual(
    #         expected,
    #         link_biosphere_by_activity_hash(data, 'biosphere', True)
    #     )

    # def test_linking(self):
    #     self.create_biosphere()
    #     data = [{
    #         'exchanges': [
    #             {     # Simple match
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #             }, {  # No type attribute - skip
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #             }, {  # Nitrogen is wrong type in db - skip
    #                 'name': 'nitrogen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #             }, {  # Wrong type - skip
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'foo',
    #             }, {  # Existing link - skip
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #                 'input': ('foo', 'bar'),
    #             }, {  # No match in db - skip
    #                 'name': 'xenon',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #             }
    #         ]
    #     }]
    #     expected = [{
    #         'exchanges': [
    #             {
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #                 'input': ('biosphere', 'oxygen'),
    #             }, {
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #             }, {
    #                 'name': 'nitrogen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #             }, {
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'foo',
    #             }, {
    #                 'name': 'oxygen',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #                 'input': ('foo', 'bar'),
    #             }, {
    #                 'name': 'xenon',
    #                 'unit': 'kilogram',
    #                 'type': 'biosphere',
    #             }
    #         ]
    #     }]
    #     self.assertEqual(
    #         expected,
    #         link_biosphere_by_activity_hash(data, 'biosphere')
    #     )
