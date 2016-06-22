// Generated by CoffeeScript 1.10.0
var BaseManager, Buyer, VendingMachine, base;

BaseManager = (function() {
  function BaseManager() {
    this.token = this.get_cookie('token');
    console.log(this.token);
    if (this.token === '') {
      console.log('is empty');
      this.create_buyer();
    } else {
      this.get_vm();
      this.get_buyer();
    }
  }

  BaseManager.prototype.ask = function(method, url) {
    var xhr;
    xhr = new XMLHttpRequest;
    xhr.open(method, url, true);
    xhr.onload = (function(_this) {
      return function() {
        var data;
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            data = JSON.parse(xhr.responseText);
            console.log;
            if (data.action === 'get_vm') {
              _this.vm = new VendingMachine(data.data);
              return _this.vm.render();
            } else if (data.action === 'get_buyer') {
              _this.buyer = new Buyer(data.data);
              return _this.buyer.render();
            } else if (data.action === 'add_coin') {
              _this.get_vm();
              return _this.get_buyer();
            } else if (data.action === 'buy') {
              _this.get_vm();
              return document.querySelector('#messages').innerHTML = data.message;
            } else if (data.action === 'return_founds') {
              _this.get_vm();
              return _this.get_buyer();
            } else if (data.action === 'create_buyer') {
              console.log(data);
              _this.token = data.data;
              console.log(_this.token);
              _this.set_cookie('token', _this.token, 1);
              _this.get_vm();
              return _this.get_buyer();
            }
          }
        }
      };
    })(this);
    xhr.onerror = function() {
      return console.log('Network problem');
    };
    return xhr.send(null);
  };

  BaseManager.prototype.set_cookie = function(name, value, days) {
    var date, expires;
    if (days) {
      date = new Date;
      date.setTime(date.getTime + (days * 24 * 3600 * 1000));
      expires = '; expires=' + date.toGMTString();
    } else {
      expires = '';
    }
    return document.cookie = name + "=" + value + expires + "; path=/";
  };

  BaseManager.prototype.get_cookie = function(c_name) {
    var c_end, c_start;
    if (document.cookie.length > 0) {
      c_start = document.cookie.indexOf(c_name + "=");
      if (c_start !== -1) {
        c_start = c_start + c_name.length + 1;
        c_end = document.cookie.indexOf(";", c_start);
        if (c_end === -1) {
          c_end = document.cookie.length;
        }
        return unescape(document.cookie.substring(c_start, c_end));
      }
    }
    return "";
  };

  BaseManager.prototype.get_vm = function() {
    var data;
    data = this.ask('GET', '/vms/' + this.token);
  };

  BaseManager.prototype.get_buyer = function() {
    var data;
    data = this.ask('GET', '/buyer/' + this.token);
  };

  BaseManager.prototype.create_buyer = function() {
    var data;
    data = this.ask('GET', '/buyer/add');
  };

  return BaseManager;

})();

VendingMachine = (function() {
  function VendingMachine(data) {
    this.id = data.id;
    this.coins = data.coins;
    this.goods = data.goods;
    this.buffer = data.buffer;
  }

  VendingMachine.prototype.render = function() {
    var content, good, goods, i, len, template, vm;
    template = '<h1>Vending Machine {{ vm.id }}</h1> <div class="coins col-md-12"> {% for coin in vm.coins %} <button class="btn-warning coin" data-value="{{ coin.nominal }}" data-amount="{{ coin.amount }}"> <span class="glyphicon glyphicon-rub"></span> {{ coin.nominal }} X {{ coin.amount }} </button> {% endfor %} </div> <div class="goods col-md-12 thumbnail"> {% for good in vm.goods %} <button class="good col-md-2" data-value="{{ good.name }}" data-price="{{ good.price }}" data-amount="{{ good.amount }}" data-id="{{ good.id }}"> <h4>{{ good.name }}</h4> <h3>{{ good.amount }}</h3> <h4><span class="glyphicon glyphicon-rub"></span> {{ good.price }}</h4> </button> {% endfor %} </div> <div class="buffer thumbnail col-md-6" data-amount="{{ vm.buffer }}"> Внесенная сумма: {{ vm.buffer }} </div> <button class="return btn-danger"><span class="glyphicon glyphicon-repeat"></span>Сдача</button>';
    this.preview = document.getElementById('vm');
    content = swig.render(template, {
      locals: {
        vm: this
      }
    });
    this.preview.innerHTML = content;
    vm = this;
    goods = this.preview.querySelectorAll('.good');
    for (i = 0, len = goods.length; i < len; i++) {
      good = goods[i];
      good.addEventListener('click', function() {
        var data;
        return data = base.ask('PUT', '/vms/' + vm.id + '/pay/' + this.dataset.id);
      });
    }
    return this.preview.querySelector('.return').addEventListener('click', function() {
      var success;
      return success = base.ask('PUT', '/vms/' + vm.id + '/buyer/' + base.token + '/return');
    });
  };

  return VendingMachine;

})();

Buyer = (function() {
  function Buyer(data) {
    this.id = data.id;
    this.coins = data.coins;
  }

  Buyer.prototype.render = function() {
    var coin, coins, content, i, len, results, template;
    template = '<h1>Your pocket</h1> <div class="coins"> {% for coin in buyer.coins %} <button class="btn-warning coin" data-value="{{ coin.nominal }}" data-amount="{{ coin.amount }}"> <span class="glyphicon glyphicon-rub"></span> {{ coin.nominal }} X {{ coin.amount }} </button> {% endfor %} </div>';
    this.preview = document.getElementById('buyer');
    content = swig.render(template, {
      locals: {
        buyer: this
      }
    });
    this.preview.innerHTML = content;
    coins = this.preview.querySelectorAll('.coin');
    results = [];
    for (i = 0, len = coins.length; i < len; i++) {
      coin = coins[i];
      results.push(coin.addEventListener('click', function() {
        var data;
        return data = base.ask('PUT', '/vms/' + base.vm.id + '/buyer/' + base.token + '/add/' + this.dataset.value);
      }));
    }
    return results;
  };

  return Buyer;

})();

base = new BaseManager;
