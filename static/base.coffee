class BaseManager

    constructor: ->
        @token = @get_cookie('token')
        if @token == ''
            @create_buyer()
        else
            @get_vm()
            @get_buyer()

    ask: (method, url) ->
        xhr = new XMLHttpRequest
        xhr.open method, url, true
        xhr.onload = =>
            if xhr.readyState == 4
                if xhr.status == 200
                    data = JSON.parse(xhr.responseText)
                    if data.action == 'get_vm'
                        @vm = new VendingMachine data.data
                        @vm.render()
                    else if data.action == 'get_buyer'
                        @buyer = new Buyer data.data
                        @buyer.render()
                    else if data.action == 'add_coin'
                        @get_vm()
                        @get_buyer()
                    else if data.action == 'buy'
                        @get_vm()
                        document.querySelector('#messages').innerHTML = data.message
                    else if data.action == 'return_founds'
                        @get_vm()
                        @get_buyer()
                    else if data.action == 'create_buyer'
                        @token = data.data
                        @set_cookie 'token', @token, 1
                        @get_vm()
                        @get_buyer()
        xhr.onerror = ->
            @set_cookie 'token', '', 0
        xhr.send(null)

    set_cookie: (name, value, days) ->
        if days
            date = new Date
            date.setTime date.getTime + (days * 24 * 3600 * 1000)
            expires = '; expires=' + date.toGMTString()
        else
            expires = ''
        document.cookie = name + "=" + value + expires + "; path=/"

    get_cookie: (c_name) ->
        if (document.cookie.length > 0)
            c_start = document.cookie.indexOf c_name + "="
            if (c_start != -1)
                c_start = c_start + c_name.length + 1
                c_end = document.cookie.indexOf ";", c_start
                if (c_end == -1)
                    c_end = document.cookie.length
                return unescape document.cookie.substring(c_start, c_end)
        return ""

    get_vm: ->
        data = @ask 'GET', '/vms/' + @token
        return

    get_buyer: ->
        data = @ask 'GET', '/buyer/' + @token
        return

    create_buyer: ->
        data = @ask 'GET', '/buyer/add'
        return


class VendingMachine

    constructor: (data) ->
        @id = data.id
        @coins = data.coins
        @goods = data.goods
        @buffer = data.buffer

    render: ->
        template = '
            <h1>Торговый автомат №{{ vm.id }}</h1>
            <div class="coins col-md-12">
                {% for coin in vm.coins %}
                    <button class="btn btn-warning coin" data-value="{{ coin.nominal }}" data-amount="{{ coin.amount }}">
                        <span class="glyphicon glyphicon-rub"></span> {{ coin.nominal }} X {{ coin.amount }}
                    </button>
                {% endfor %}
            </div>
            <div class="goods col-md-12 thumbnail">
                {% for good in vm.goods %}
                    <button class="btn btn-default good col-md-3" data-value="{{ good.name }}" data-price="{{ good.price }}" data-amount="{{ good.amount }}" data-id="{{ good.id }}">
                        <h5>{{ good.name }}</h5>
                        <h3>{{ good.amount }}</h3>
                        <h5><span class="glyphicon glyphicon-rub"></span> {{ good.price }}</h5>
                    </button>
                {% endfor %}
            </div>
            <div class="buffer thumbnail col-md-6" data-amount="{{ vm.buffer }}">
                Внесенная сумма: {{ vm.buffer }}
            </div>
            <button class="btn return btn-danger"><span class="glyphicon glyphicon-repeat"></span>Сдача</button>
            '
        @preview = document.getElementById('vm')
        content = swig.render template, locals: {vm: @}
        @preview.innerHTML = content
        vm = @
        goods = @preview.querySelectorAll('.good')
        for good in goods
            good.addEventListener('click', ->
                data = base.ask 'PUT', '/vms/' + vm.id + '/pay/' + this.dataset.id
            )
        @preview.querySelector('.return').addEventListener('click', ->
            success = base.ask 'PUT', '/vms/' + vm.id + '/buyer/' + base.token + '/return'
        )


class Buyer

    constructor: (data) ->
        @id = data.id
        @coins = data.coins
    
    render: ->
        template = '
            <h1>Ваш кошелёк</h1>
            <div class="coins">
                {% for coin in buyer.coins %}
                    <button class="btn btn-warning coin" data-value="{{ coin.nominal }}" data-amount="{{ coin.amount }}">
                        <span class="glyphicon glyphicon-rub"></span> {{ coin.nominal }} X {{ coin.amount }}
                    </button>
                {% endfor %}
            </div>
            '
        @preview = document.getElementById('buyer')
        content = swig.render template, locals: {buyer: @}
        @preview.innerHTML = content
        coins = @preview.querySelectorAll('.coin')
        for coin in coins
            coin.addEventListener('click', ->
                data = base.ask 'PUT', '/vms/' + base.vm.id + '/buyer/' + base.token + '/add/' + this.dataset.value
            )


base = new BaseManager
