#-*- encoding: utf-8 -*-

import flask
from models import VendingMachine, Buyer, Good, db
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin

app = flask.Flask(__name__, static_url_path='/home/nixon/vms/static')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
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


@app.route('/vms', methods=['GET'])
def get_vms():
    vms = VendingMachine.query.all()
    ret = [{'id': vm.id} for vm in vms]
    success = True
    message = ''
    return flask.jsonify({'success': success,
                          'message': message,
                          'action': 'get_vms',
                          'data': ret})


@app.route('/vms/<int:vm_id>', methods=['GET'])
def get_vm(vm_id):
    vm = VendingMachine.query.get(vm_id)
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


@app.route('/vms/add', methods=['POST'])
def add_vm():
    vm = VendingMachine(coins_1 = 100, coins_2 = 100, coins_5 = 100, coins_10 = 100, buff = 0)
    tea = Good(name = u'Чай', price = 13, amount = 10, vm = vm)
    coffee = Good(name = u'Кофе', price = 18, amount = 20, vm = vm)
    latte = Good(name = u'Кофе с молоком', price = 21, amount = 20, vm = vm)
    juice = Good(name = u'Сок', price = 35, amount = 15, vm = vm)
    db.session.add_all([vm, tea, coffee, latte, juice])
    db.session.commit()
    return flask.jsonify({'success': True,
                          'message': '',
                          'action': 'add_vm',
                          'data': None})



@app.route('/buyer/<int:buyer_id>', methods=['GET'])
def get_buyer_info(buyer_id):
    buyer = Buyer.query.get(buyer_id)
    coins = [{'nominal': key, 'amount': value} for key, value in buyer.get_coins().iteritems()]
    ret = {'id': buyer.id, 'coins': coins}
    success = True
    message = ''
    return flask.jsonify({'success': success,
                          'message': message,
                          'action': 'get_buyer',
                          'data': ret})


@app.route('/vms/<int:vm_id>/buyer/<int:buyer_id>/add/<int:coin>', methods=['PUT'])
def add_coin(vm_id, buyer_id, coin):
    vm = VendingMachine.query.get(vm_id)
    buyer = Buyer.query.get(buyer_id)
    success = buyer.give_coin(coin)
    message = ''
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
    success = False
    message = u'Недостаточно средств'
    good = Good.query.filter(db.and_(Good.id == good_id, Good.vm_id == vm_id)).first()
    if good:
        vm = VendingMachine.query.get(vm_id)
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


@app.route('/vms/<int:vm_id>/buyer/<int:buyer_id>/return', methods=['PUT'])
def return_founds(vm_id, buyer_id):
    vm = VendingMachine.query.get(vm_id)
    buyer = Buyer.query.get(buyer_id)
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

# Create the Flask-Restless API manager.
# manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
# manager.create_api(VendingMachine, methods=['GET', 'POST', 'DELETE'])

# start the flask loop
app.secret_key = 'super secret key'
#app.run(host='0.0.0.0')
if __name__ == "__main__":

    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
