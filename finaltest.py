import unittest
from finalproj import *

### Test based on DETROIT search ###

class TestDatabase(unittest.TestCase):

    def test1_yelp_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM YelpResto'
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertIn(('Bakersfield',), result_list, 'testing Bakersfield in list')
        self.assertTrue(len(result_list)<=100, 'testing record count not exceeds 100')

        sql = '''
            SELECT Name, CategoryName
            FROM YelpResto
            WHERE Name = 'Pie Sci'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(result_list[0][1], 'Pizza', 'testing category is Pizza')

        sql = '''
            SELECT Name, CategoryName
            FROM YelpResto
            WHERE Name = "Jose's Tacos"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(result_list[0][1], 'Tacos', 'testing category is Tacos')

        conn.close()

    def test2_zomato_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM ZomatoResto'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Red Smoke Barbecue',), result_list, 'testing Red Smoke Barbecue in list')
        self.assertTrue(len(result_list)<=100, 'testing record count not exceeds 100')

        sql = '''
            SELECT Name, Cuisine
            FROM ZomatoResto
            WHERE Name = 'Benihana'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(result_list[0][1], 'Japanese', 'testing category is Japanese')

        sql = '''
            SELECT Name, Cuisine
            FROM ZomatoResto
            WHERE Name = "Angelo's"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(result_list[0][1], 'Breakfast', 'testing category is Breakfast')

        conn.close()

    def test3_categories(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT CategoryName FROM Categories'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Bars',), result_list, 'testing Bars in list')
        self.assertIn(('French',), result_list, 'testing French in list')

        conn.close()

    def test4_cuisines(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Cuisine FROM Cuisines'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Burger',), result_list, 'testing Burger in list')
        self.assertIn(('Breakfast',), result_list, 'testing Breakfast in list')
        
        conn.close()

class TestYelpSearch(unittest.TestCase):

    def test5_yelp_list_command(self):
        results = process_command('list yelp top 10')
        self.assertEqual(len(results), 10, 'testing limit works' )
        self.assertEqual(len(results[0]), 4, 'testing record is a 4-value tuple')

class TestZomatoSearch(unittest.TestCase):

    def test6_zomato_list_command(self):
        results = process_command('list zomato bottom 5')
        self.assertEqual(len(results), 5, 'testing limit works' )
        self.assertEqual(len(results[0]), 4, 'testing record is a 4-value tuple')


### RUN TEST CASE ###
unittest.main(verbosity = 2)
