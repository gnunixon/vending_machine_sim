import flask
import flask_sqlalchemy
from change import change_money

app = flask.Flask(__name__, static_url_path='/home/nixon/vms/static')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/vms'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_ECHO'] = True
db = flask_sqlalchemy.SQLAlchemy(app)


class Good(db.Model):
    """
    This is something that we can sell in Vending Machine. Can be tea, coffee,
    or even a nuclear weapon - it's your Vending Machine, so you can decide what
    you want to sell in it.
    """
    #: the unique id
    id = db.Column(db.Integer, primary_key=True)
    #: the human readable name of this stuff
    name = db.Column(db.String)
    #: the price per unit
    price = db.Column(db.Integer)
    #: how many items we have in stock
    amount = db.Column(db.Integer)
    #: the Vending Machine where we sell it
    vm_id = db.Column(db.Integer, db.ForeignKey('vending_machine.id'))


class Buyer(db.Model):
    """
    This is the user, how can buy something in Vending Machine (or just change
    some money)
    """
    #: the unique id
    id = db.Column(db.Integer, primary_key=True)
    #: how many coins of 1 ruble the user have
    coins_1 = db.Column(db.Integer, default=10)
    #: how many coins of 2 rubles the user have
    coins_2 = db.Column(db.Integer, default=30)
    #: how many coins of 5 rubles the user have
    coins_5 = db.Column(db.Integer, default=20)
    #: how many coins of 10 rubles the user have
    coins_10 = db.Column(db.Integer, default=15)
    #: the unique token for identify the buyer
    token = db.Column(db.String, unique=True)

    def get_coins(self):
        """
        This method return a dict with all available coins
        """
        coins = {1: self.coins_1, 2: self.coins_2,
                5: self.coins_5, 10: self.coins_10}
        return coins

    def give_coin(self, coin):
        """
        This method ask for a coin and return True if user give this coin, or
        False if it haven't this kind of coins

        :param int coin: the coin ask we for
        :returns: True if the operation is successful
        :rtype: bool
        """
        field = 'coins_%d' % coin
        if hasattr(self, field):
            value = getattr(self, field)
            if value > 0:
                setattr(self, field, value - 1)
                return True
        return False

    def add_coins(self, coins):
        """
        This method will put in the wallet of user the given coins

        :param dict coins: a dict with key as value of coin and value as its amount
        :returns: True is operation is successful
        :rtype: bool
        """
        for coin, amount in coins.iteritems():
            field = 'coins_%d' % coin
            value = getattr(self, field)
            setattr(self, field, value + amount)
        return True


class VendingMachine(db.Model):
    """
    This is our Vending Machine
    """
    #: unique id
    id = db.Column(db.Integer, primary_key=True)
    #: how many coins of 1 ruble the vm have
    coins_1 = db.Column(db.Integer, default=100)
    #: how many coins of 2 rubles the vm have
    coins_2 = db.Column(db.Integer, default=100)
    #: how many coins of 5 rubles the vm have
    coins_5 = db.Column(db.Integer, default=100)
    #: how many coins of 10 rubles the vm have
    coins_10 = db.Column(db.Integer, default=100)
    #: the amount of money, available for buying something
    buff = db.Column(db.Integer, default=0)
    #: the list of all stuff we can buy in VM
    goods = db.relationship(Good, backref="vm")
    #: the current user that use this VM
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'), nullable=True)
    buyer = db.relationship(Buyer, backref='vending_machine')

    def get_coins(self):
        """
        This method return a dict with all available coins
        """
        coins = {1: self.coins_1, 2: self.coins_2,
                5: self.coins_5, 10: self.coins_10}
        return coins

    def substract(self, coins):
        """
        Substract the given list of coins from Vending Machine

        :param dict coins: a dict of coins (format like in get_coins)
        :returns: True if operation was successful
        :rtype: bool
        """
        for coin, amount in coins.iteritems():
            field = 'coins_%d' % coin
            value = getattr(self, field)
            setattr(self, field, value - amount)
        return True

    def add_to_buff(self, coin):
        """
        Add a coin to buffer

        :param int coin: the value of coin
        :returns: True if the operation was successful
        :rtype: bool
        """
        field = 'coins_%d' % coin
        if hasattr(self, field):
            value = getattr(self, field)
            setattr(self, field, value + 1)
            self.buff += coin
            return True
        return False

    def return_from_buff(self):
        """
        Return all money from VMs buffer to user

        :returns: a dict with changed money from buffer (as in get_coins)
        :rtype: dict
        """
        ret = {}
        if self.buff > 0:
            ret = change_money(self.buff, self.get_coins())
            self.substract(ret)
            self.buff = 0
        return ret
