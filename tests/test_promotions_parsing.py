from item import Item
from promotion import RewardType, find_promo_function, get_discount_rate


# TODO: create a test for Shufersal promo type 3

def test_shufersal_promo_type_1():
    reward_type = RewardType(1)
    discounted_price = 100.00
    orig_discount_rate = None

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark=' מחיר המבצע הינו המחיר לק"ג ',
        promo_description='300ב30 פטה פיראוס 20% במשקל',
        min_qty=0.3,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('פטה פיראוס 20%', 113, 1, '', '')
    assert promo_func(item) == 100


def test_shufersal_promo_type_2():
    reward_type = RewardType(2)
    discounted_price = None
    orig_discount_rate = 2000

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='20%הנחה גרנולה פנינה רוזנבלום500',
        min_qty=1,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('חגיגת גרנולה פ.יבשים500ג', 26.9, 1, '', '')
    assert promo_func(item) == 21.52


def test_shufersal_promo_type_6_1():
    reward_type = RewardType(6)
    discounted_price = 0.00
    orig_discount_rate = None

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark=' מחיר המבצע הינו המחיר לק"ג ',
        promo_description='ב-קנה350גרם נקניק במעדניה קבל קופסת מתנה',
        min_qty=0.35,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('פסטרמה מקסיקנית במשקל', 89, 1, '', '')
    assert promo_func(item) == 89


def test_shufersal_promo_type_6_2():
    reward_type = RewardType(6)
    discounted_price = 0.00
    orig_discount_rate = None

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='מכונת קפה לוואצה גולי2-חב קפסולות',
        min_qty=1.00,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('מכונת לוואצה ג\'ולי אדומה', 449, 1, '', '')
    assert promo_func(item) == 449


def test_shufersal_promo_type_7_1():
    reward_type = RewardType(7)
    discounted_price = None
    orig_discount_rate = 10000

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='1+1הזול מוצרי קולקשיין שופרסל',
        min_qty=2.00,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('פינצטה 2011 שחורה/כסופה', 14.9, 1, '', '')
    assert promo_func(item) == 7.45


def test_shufersal_promo_type_7_2():
    reward_type = RewardType(7)
    discounted_price = None
    orig_discount_rate = 10000

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='3+1 יוגורט עיזים ביו 150 גרם',
        min_qty=4.00,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('יוגורט עיזים 500 גרם', 12.9, 1, '', '')
    assert promo_func(item) == 12.9 * 0.75


def test_shufersal_promo_type_9_1():
    reward_type = RewardType(9)
    discounted_price = None
    orig_discount_rate = 5000

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='שני ב%50הנחה מוצרי מותג קבוצת יבנה',
        min_qty=2.00,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('זיתים מבוקעים פיקנטי540ג', 9.3, 1, '', '')
    assert promo_func(item) == 9.3 * 0.75


def test_shufersal_promo_type_9_2():
    reward_type = RewardType(9)
    discounted_price = 10.00
    orig_discount_rate = None

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='ב-שני ב10 ירקות קפואים שופרסל',
        min_qty=2.00,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('שעועית לבנה שופרסל 800גר', 18.9, 1, '', '')
    assert promo_func(item) == (18.9 + 10) / 2


def test_shufersal_promo_type_9_3():
    reward_type = RewardType(9)
    discounted_price = None
    orig_discount_rate = 5000

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='השני ב50% הזול אביזרי שיער BE NOW',
        min_qty=2.00,
        discount_rate=discount_rate,
        discounted_price=discounted_price,
    )
    item = Item('גומיות שחורות 12 יח', 9.9, 1, '', '')
    assert promo_func(item) == 9.9 * 0.75


def test_shufersal_promo_type_10_1():
    reward_type = RewardType(10)
    discounted_price = 10
    orig_discount_rate = None

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='2ב10משקה סויה מועשר בחלבון 250 מ"ל',
        min_qty=2,
        discount_rate=discount_rate,
        discounted_price=discounted_price
    )
    item = Item('טופו טעם טבעי  300 גרם', 10.9, 1, '7296073345763', '')
    assert promo_func(item) == 5


def test_shufersal_promo_type_10_2():
    reward_type = RewardType(10)
    discounted_price = 14
    orig_discount_rate = None

    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark='',
        promo_description='2ב14טופו טבעי/רך מועשר בסידן 300 גרם',
        min_qty=2,
        discount_rate=discount_rate,
        discounted_price=discounted_price
    )
    item = Item('טופו טעם טבעי  300 גרם', 10.9, 1, '7296073345763', 'כפרי בריא משק ויילר')
    assert promo_func(item) == 7


def assert_discount(discounted_price, item_barcode, item_manufacturer, item_name, min_qty, orig_discount_rate,
                    orig_price, price_after_discount, promo_description, reward_type, remark):
    is_discount_in_percentage = reward_type == RewardType.DISCOUNT_IN_PERCENTAGE or not discounted_price
    discount_rate = get_discount_rate(orig_discount_rate, is_discount_in_percentage)
    promo_func = find_promo_function(
        reward_type=reward_type,
        remark=remark,
        promo_description=promo_description,
        min_qty=min_qty,
        discount_rate=discount_rate,
        discounted_price=discounted_price
    )
    item = Item(item_name, orig_price, 1, item_barcode, item_manufacturer)
    assert abs(promo_func(item) - price_after_discount) <= 1e-5, promo_description


def test_coop_promo_type_2():
    reward_type = RewardType(2)
    discounted_price = 6.95
    orig_discount_rate = 50
    promo_description = 'ק/עגבני. השני ב50% הנחה רסק/תרכיז/המשתתפים'
    orig_price = 13.9
    price_after_discount = 13.9 * 0.75
    item_name = 'מחית עגבניות גרנד איטליה 700גר'
    item_manufacturer = 'תה ויסוצקי (ישראל)בעמ'
    item_barcode = '7290015150088'
    min_qty = 2
    remark = ''

    assert_discount(discounted_price, item_barcode, item_manufacturer, item_name, min_qty, orig_discount_rate,
                    orig_price, price_after_discount, promo_description, reward_type, remark)


def test_coop_promo_type_3_1():
    reward_type = RewardType(3)
    discounted_price = 19.90
    orig_discount_rate = 20
    promo_description = '*ק/מקס/בירה ב19.90ש עד2יח סטלה 1/6 330מ"ל'
    orig_price = 39.90
    price_after_discount = 19.90
    item_name = 'בירה סטלה מארז שישיה 330 מ"ל'
    item_manufacturer = 'קומפלקס כימיקלסבעמ ~~~'
    item_barcode = '7290002814016'
    min_qty = 1
    remark = ''

    assert_discount(discounted_price, item_barcode, item_manufacturer, item_name, min_qty, orig_discount_rate,
                    orig_price, price_after_discount, promo_description, reward_type, remark)


def test_coop_promo_type_3_2():
    reward_type = RewardType(3)
    discounted_price = 14.90
    orig_discount_rate = 2.50
    promo_description = 'ק/אמנטל ב14.90 נעם 30% 200גר'
    orig_price = 17.4
    price_after_discount = 14.90
    item_name = 'אמנטל נעם 200ג'
    item_manufacturer = '*חברה המרכזית להפצתמשקאותבעמ*'
    item_barcode = '7290102397730'
    min_qty = 1
    remark = ''

    assert_discount(discounted_price, item_barcode, item_manufacturer, item_name, min_qty, orig_discount_rate,
                    orig_price, price_after_discount, promo_description, reward_type, remark)


def test_coop_promo_type_7_1():
    reward_type = RewardType(7)
    discounted_price = None
    orig_discount_rate = 100
    promo_description = 'ק/מגוון מוצרי סנפרוסט 3+1 הזול מבניהם ללא לקטים'
    orig_price = 23.9
    price_after_discount = orig_price * 0.75
    item_name = 'עדשים מבושלים 1ק"ג'
    item_manufacturer = 'תנובה בשר'
    item_barcode = '104072'
    min_qty = 4
    remark = ''

    assert_discount(discounted_price, item_barcode, item_manufacturer, item_name, min_qty, orig_discount_rate,
                    orig_price, price_after_discount, promo_description, reward_type, remark)


def test_coop_promo_type_7_2():
    reward_type = RewardType(7)
    discounted_price = 0
    orig_discount_rate = 100
    promo_description = 'ק/2+1ספיד סטיק הזול מבניהם המשתתפים'
    orig_price = 26.9
    price_after_discount = orig_price * 2 / 3
    item_name = '##ספיד סטיק ג ל-כחול'
    item_manufacturer = 'ש.שסטוביץ בעמ'
    item_barcode = '22200956932'
    min_qty = 3
    remark = ''

    assert_discount(discounted_price, item_barcode, item_manufacturer, item_name, min_qty, orig_discount_rate,
                    orig_price, price_after_discount, promo_description, reward_type, remark)


def test_coop_promo_type_10():
    reward_type = RewardType(10)
    discounted_price = 25
    orig_discount_rate = 2.57
    promo_description = 'ק/סנו סושי 3ב25 מטליות זיגזג 1/3/כריות הפלא/9מטליו'
    orig_price = 10.90
    price_after_discount = 25 / 3
    item_name = 'סנו סושי מטלית הפלא לרצפה Decor'
    item_manufacturer = 'החב הדרומית לשיווק'
    item_barcode = '7290108353686'
    min_qty = 3
    remark = ''

    assert_discount(discounted_price, item_barcode, item_manufacturer, item_name, min_qty, orig_discount_rate,
                    orig_price, price_after_discount, promo_description, reward_type, remark)
