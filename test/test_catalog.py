import json
import os
import unittest
import shutil

from satstac import __version__, Catalog, STACError, Item


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):

    path = os.path.join(testpath, 'test-catalog')

    @classmethod
    def tearDownClass(cls):
        """ Remove test files """
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path)

    @classmethod
    def get_catalog(cls):
        """ Open existing test catalog """
        return Catalog.open(os.path.join(testpath, 'catalog/catalog.json'))

    @classmethod
    def create_catalog(cls, name):
        path = os.path.join(cls.path, name)
        return Catalog.create(path)

    def test_init(self):
        with open(os.path.join(testpath, 'catalog/catalog.json')) as f:
            data = json.loads(f.read())
        cat = Catalog(data)
        assert(cat.id == 'stac')

    def test_open(self):
        """ Initialize Catalog with a file """
        cat = self.get_catalog()
        assert(len(cat.keys()) == 4)
        assert(cat.id == 'stac')
        assert(len(cat.links())==3)

    def test_properties(self):
        cat = self.get_catalog()
        assert(cat.stac_version == __version__)
        assert(cat.description == 'A STAC of public datasets')

    def test_create(self):
        """ Create new catalog file """
        cat = Catalog.create()
        assert(cat.id == 'stac-catalog')

    def test_create_with_keywords(self):
        path = os.path.join(testpath, 'test-catalog', 'create_with_keywords')
        desc = 'this is a catalog'
        cat = Catalog.create(path, description=desc)
        assert(cat.description == desc)

    def test_links(self):
        root = self.get_catalog()
        child = root.children()[0]
        assert(child.parent().id == root.id)

    def test_get_catalogs(self):
        catalogs = [i for i in self.get_catalog().catalogs()]
        assert(len(catalogs) == 4)

    def test_get_collections(self):
        collections = [i for i in self.get_catalog().collections()]
        assert(len(collections) == 2)
        assert(collections[0].id in ['landsat-8-l1', 'sentinel-2-l1c'])
        assert(collections[1].id in ['landsat-8-l1', 'sentinel-2-l1c'])

    def test_get_items(self):
        items = [i for i in self.get_catalog().items()]
        assert(len(items) == 2)

    def test_add_catalog(self):
        cat = Catalog.create().save_as(os.path.join(self.path, 'catalog.json'), root=True)
        col = Catalog.open(os.path.join(testpath, 'catalog/eo/landsat-8-l1/catalog.json'))
        cat.add_catalog(col)
        assert(cat.children()[0].id == col.id)

    def test_add_catalog_without_saving(self):
        cat = Catalog.create()
        with self.assertRaises(STACError):
           cat.add_catalog({})

    def test_publish(self):
        path = os.path.join(self.path, 'test_publish')
        shutil.copytree('catalog', path)
        cat = Catalog.open(os.path.join(path, 'catalog.json'))
        cat.publish('https://my.cat')
        item = Item.open(os.path.join(path, 'eo/landsat-8-l1/item.json'))
        assert(item.links('self')[0] == 'https://my.cat/eo/landsat-8-l1/item.json')