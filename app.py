import flask
import flask_sqlalchemy
from models import VendingMachine, Buyer, Good

app = flask.Flask(__name__, static_url_path='/home/nixon/vms/static')
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = flask_sqlalchemy.SQLAlchemy(app)


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
    return flask.jsonify({'vms': ret})


@app.route('/vms/<int:vm_id>', methods=['GET'])
def get_vm(vm_id):
    vm = VendingMachine.query.get(vm_id)
    coins = [{'nominal': key, 'amount': value} for key, value in vm.get_coins().iteritems()]
    goods = []
    for good in vm.goods:
        goods.append({'name': good.name,
                      'price': good.price,
                      'amount': good.amount})
    ret = {'id': vm.id, 'coins': coins, 'buffer': vm.buff,
           'goods': goods}
    return flask.jsonify({'vm': ret})


@app.route('/buyer/<int:buyer_id>', methods=['GET'])
def get_buyer_info(buyer_id):
    buyer = Buyer.query.get(buyer_id)
    coins = [{'nominal': key, 'amount': value} for key, value in buyer.get_coins().iteritems()]
    ret = {'id': buyer.id, 'coins': coins}
    return flask.jsonify({'buyer': ret})


@app.route('/vms/<int:vm_id>/buyer/<int:buyer_id>/add/<int:coin>', methods=['PUT'])
def add_coin(vm_id, buyer_id, coin):
    vm = VendingMachine.query.get(vm_id)
    buyer = Buyer.query.get(buyer_id)
    success = buyer.give_coin(coin)
    if success:
        success = vm.add_to_buff(coin)
    db.session.commit()
    return flask.jsonify({'success': success})


@app.route('/vms/<int:vm_id>/pay/<int:good_id>', methods=['PUT'])
def buy(vm_id, good_id):
    success = False
    good = Good.query.filter(db.and_(Good.id == good_id, Good.vm_id == vm_id)).first()
    if good:
        vm = VendingMachine.query.get(vm_id)
        if good and vm.buff >= good.price and good.amount > 0:
            good.amount -= 1
            vm.buff -= good.price
            db.session.commit()
            success = True
    return flask.jsonify({'success': success})


@app.route('/vms/<int:vm_id>/buyer/<int:buyer_id>/return', methods=['PUT'])
def return_founds(vm_id, buyer_id):
    vm = VendingMachine.query.get(vm_id)
    buyer = Buyer.query.get(buyer_id)
    coins = vm.return_from_buff()
    success = buyer.add_coins(coins)
    db.session.commit()
    return flask.jsonify({'success': success})


# Create the database tables.
db.create_all()

# Create the Flask-Restless API manager.
# manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
# manager.create_api(VendingMachine, methods=['GET', 'POST', 'DELETE'])

# start the flask loop
app.run(host='0.0.0.0')
