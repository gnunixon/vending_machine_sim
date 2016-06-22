import flask
import flask_sqlalchemy
from change import change_money

app = flask.Flask(__name__, static_url_path='/home/nixon/vms/static')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = flask_sqlalchemy.SQLAlchemy(app)


class Good(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    vm_id = db.Column(db.Integer, db.ForeignKey('vending_machine.id'))


class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coins_1 = db.Column(db.Integer, default=10)
    coins_2 = db.Column(db.Integer, default=30)
    coins_5 = db.Column(db.Integer, default=20)
    coins_10 = db.Column(db.Integer, default=15)

    def get_coins(self):
        coins = {1: self.coins_1, 2: self.coins_2,
                5: self.coins_5, 10: self.coins_10}
        return coins

    def give_coin(self, coin):
        field = 'coins_%d' % coin
        if hasattr(self, field):
            value = getattr(self, field)
            setattr(self, field, value - 1)
            return True
        return False

    def add_coins(self, coins):
        for coin, amount in coins.iteritems():
            field = 'coins_%d' % coin
            value = getattr(self, field)
            setattr(self, field, value + amount)
        return True


class VendingMachine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coins_1 = db.Column(db.Integer, default=100)
    coins_2 = db.Column(db.Integer, default=100)
    coins_5 = db.Column(db.Integer, default=100)
    coins_10 = db.Column(db.Integer, default=100)
    buff = db.Column(db.Integer, default=0)
    goods = db.relationship(Good, backref="vm")

    def get_coins(self):
        coins = {1: self.coins_1, 2: self.coins_2,
                5: self.coins_5, 10: self.coins_10}
        return coins

    def substract(self, coins):
        for coin, amount in coins.iteritems():
            field = 'coins_%d' % coin
            value = getattr(self, field)
            setattr(self, field, value - amount)
        return True

    def add_to_buff(self, coin):
        field = 'coins_%d' % coin
        if hasattr(self, field):
            value = getattr(self, field)
            setattr(self, field, value + 1)
            self.buff += coin
            return True
        return False

    def return_from_buff(self):
        ret = {}
        if self.buff > 0:
            ret = change_money(self.buff, self.get_coins())
            self.substract(ret)
            self.buff = 0
        return ret
