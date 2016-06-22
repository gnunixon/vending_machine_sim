#!/usr/bin/python2.7
#-*- encoding: utf-8 -*-

import flask
import flask_sqlalchemy
from models import VendingMachine, Buyer, Good, db, app
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
import uuid

admin = Admin(app)
admin.add_view(ModelView(VendingMachine, db.session))
admin.add_view(ModelView(Buyer, db.session))
admin.add_view(ModelView(Good, db.session))


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/base.js')
def base():
    return app.send_static_file('base.js')


@app.route('/swig.min.js')
def swig():
    return app.send_static_file('swig.min.js')


def create_vm():
    """
    It's a function for create a new Vending Machine with all the staff

    :rtype: VendingMachine
    """
    vm = VendingMachine(coins_1 = 100, coins_2 = 100, coins_5 = 100, coins_10 = 100, buff = 0)
    tea = Good(name = u'Чай', price = 13, amount = 10, vm = vm)
    coffee = Good(name = u'Кофе', price = 18, amount = 20, vm = vm)
    latte = Good(name = u'Кофе с молоком', price = 21, amount = 20, vm = vm)
    juice = Good(name = u'Сок', price = 35, amount = 15, vm = vm)
    db.session.add_all([vm, tea, coffee, latte, juice])
    db.session.commit()
    return vm


@app.route('/vms/<string:token>', methods=['GET'])
def get_vm(token):
    """
    Get the info about a specific Vending Machine (available coins, available
    stuff for selling, the state of buffer), associated to the buyer with the
    given token

    :param str token: the token of the buyer
    :rtype: json
    """
    vm = VendingMachine.query.\
        options(flask_sqlalchemy.orm.joinedload('goods')).\
        filter(VendingMachine.buyer.has(token=token)).first()
    if not vm:
        vm = VendingMachine.query.\
            options(flask_sqlalchemy.orm.joinedload('goods')).\
            filter(VendingMachine.buyer_id == None).first()
        if not vm:
            vm = create_vm()
        vm.buyer = Buyer.query.filter(Buyer.token == token).first()
        db.session.commit()
    coins = [{'nominal': key, 'amount': value} for key, value in vm.get_coins().iteritems()]
    goods = []
    for good in vm.goods:
        goods.append({'name': good.name,
                      'price': good.price,
                      'amount': good.amount,
                      'id': good.id})
    ret = {'id': vm.id, 'coins': coins, 'buffer': vm.buff,
           'goods': goods}
    success = True
    message = ''
    return flask.jsonify({'success': success,
                          'message': message,
                          'action': 'get_vm',
                          'data': ret})


@app.route('/vms/<int:vm_id>/logout/<string:token>', methods=['PUT'])
def logout(vm_id, token):
    print 'LOGOUT'
    vm = VendingMachine.query.\
        filter(VendingMachine.buyer.has(token=token)).first()
    vm.buyer_id = None
    db.session.commit()
    return


@app.route('/vms/add', methods=['POST'])
def add_vm():
    """
    Add a new Vending Machine with tea, coffee, latte and juice

    :rtype: json
    """
    create_vm()
    return flask.jsonify({'success': True,
                          'message': '',
                          'action': 'add_vm',
                          'data': None})


@app.route('/buyer/<string:token>', methods=['GET'])
def get_buyer_info(token):
    """
    Get the info about a specific buyer (id and available coins)

    :param str token: the token of the buyer
    :rtype: json
    """
    buyer = Buyer.query.filter(Buyer.token == token).first()
    coins = [{'nominal': key, 'amount': value} for key, value in buyer.get_coins().iteritems()]
    ret = {'id': buyer.id, 'coins': coins}
    success = True
    message = ''
    return flask.jsonify({'success': success,
                          'message': message,
                          'action': 'get_buyer',
                          'data': ret})


@app.route('/buyer/add', methods=['GET'])
def create_buyer():
    """
    Create a new buyer

    :rtype: json
    """
    success = False
    token = uuid.uuid4().hex
    if not Buyer.query.filter(Buyer.token == token).count():
        buyer = Buyer(coins_1 = 10, coins_2 = 30, coins_5 = 20, coins_10 = 15,
                      token = token)
        db.session.add(buyer)
        db.session.commit()
        success = True
    return flask.jsonify({'success': success,
                          'message': '',
                          'action': 'create_buyer',
                          'data': token})


@app.route('/vms/<int:vm_id>/buyer/<string:token>/add/<int:coin>', methods=['PUT'])
def add_coin(vm_id, token, coin):
    """
    Add a coin to Vending Machine (and give it from buyer)

    :param int vm_id: the id of VM
    :param str token: the token of buyer
    :param int coin: the value of coin

    :rtype: json
    """
    success = False
    message = ''
    vm = VendingMachine.query.\
        filter(db.and_(VendingMachine.id == vm_id, VendingMachine.buyer.has(token=token))).\
        options(flask_sqlalchemy.orm.joinedload('buyer')).first()
    if vm:
        buyer = vm.buyer
        success = buyer.give_coin(coin)
        if success:
            success = vm.add_to_buff(coin)
        else:
            message = u'У вас нет такой монеты'
        db.session.commit()
    return flask.jsonify({'success': success,
                          'message': message,
                          'action': 'add_coin',
                          'data': None})


@app.route('/vms/<int:vm_id>/pay/<int:good_id>', methods=['PUT'])
def buy(vm_id, good_id):
    """
    Buy something from VM

    :param int vm_id: the id of VM
    :param int good_id: the id of stuff to buy

    :rtype: json
    """
    success = False
    message = u'Недостаточно средств'
    good = Good.query.filter(db.and_(Good.id == good_id, Good.vm_id == vm_id)).options(flask_sqlalchemy.orm.joinedload('vm').load_only('buff')).first()
    print 'Hello'
    if good:
        vm = good.vm
        if good and vm.buff >= good.price and good.amount > 0:
            good.amount -= 1
            vm.buff -= good.price
            success = True
            message = u'Спасибо!'
        elif not good.amount:
            message = u'Извините, мы продали уже весь %s' % good.name
    else:
        message = u'Извините, у нас нет подобного в ассортименте'
    db.session.commit()
    return flask.jsonify({'success': success,
                          'message': message,
                          'action': 'buy',
                          'data': None})


@app.route('/vms/<int:vm_id>/buyer/<string:token>/return', methods=['PUT'])
def return_founds(vm_id, token):
    """
    Return all money from buffer of VM.

    :param int vm_id: the id of VM
    :param str token: the token of buyer

    :rtype: json
    """
    success = False
    vm = VendingMachine.query.get(vm_id)
    buyer = Buyer.query.filter(Buyer.token == token).first()
    if vm.buyer_id == buyer.id:
        coins = vm.return_from_buff()
        success = buyer.add_coins(coins)
        db.session.commit()
    message = ''
    return flask.jsonify({'success': success,
                          'message': message,
                          'action': 'return_founds',
                          'data': None})


# Create the database tables.
db.create_all()

app.secret_key = 'super secret key'
if __name__ == "__main__":

    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
