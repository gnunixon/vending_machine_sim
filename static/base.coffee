class BaseManager

    constructor: ->
        @get_vm 1
        @get_buyer 1

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
                        @get_vm @vm.id
                        @get_buyer @buyer.id
                    else if data.action == 'buy'
                        @get_vm @vm.id
                        document.querySelector('#messages').innerHTML = data.message
                    else if data.action == 'return_founds'
                        @get_vm @vm.id
                        @get_buyer @buyer.id
        xhr.onerror = ->
            console.log 'Network problem'
        xhr.send(null)

    get_vm: (vm_id) ->
        data = @ask 'GET', '/vms/' + vm_id
        return

    get_buyer: (buyer_id) ->
        data = @ask 'GET', '/buyer/' + buyer_id
        return


class VendingMachine

    constructor: (data) ->
        @id = data.id
        @coins = data.coins
        @goods = data.goods
        @buffer = data.buffer

    render: ->
        template = '
            <h1>Vending Machine {{ vm.id }}</h1>
            <div class="coins col-md-12">
                {% for coin in vm.coins %}
                    <button class="btn-warning coin" data-value="{{ coin.nominal }}" data-amount="{{ coin.amount }}">
                        <span class="glyphicon glyphicon-rub"></span> {{ coin.nominal }} X {{ coin.amount }}
                    </button>
                {% endfor %}
            </div>
            <div class="goods col-md-12 thumbnail">
                {% for good in vm.goods %}
                    <button class="good col-md-2" data-value="{{ good.name }}" data-price="{{ good.price }}" data-amount="{{ good.amount }}" data-id="{{ good.id }}">
                        <h4>{{ good.name }}</h4>
                        <h3>{{ good.amount }}</h3>
                        <h4><span class="glyphicon glyphicon-rub"></span> {{ good.price }}</h4>
                    </button>
                {% endfor %}
            </div>
            <div class="buffer thumbnail col-md-6" data-amount="{{ vm.buffer }}">
                {{ vm.buffer }}
            </div>
            <button class="return btn-danger"><span class="glyphicon glyphicon-repeat"></span></button>
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
            success = base.ask 'PUT', '/vms/' + vm.id + '/buyer/' + base.buyer.id + '/return'
        )


class Buyer

    constructor: (data) ->
        @id = data.id
        @coins = data.coins
    
    render: ->
        template = '
            <h1>Your pocket</h1>
            <div class="coins">
                {% for coin in buyer.coins %}
                    <button class="btn-warning coin" data-value="{{ coin.nominal }}" data-amount="{{ coin.amount }}">
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
                data = base.ask 'PUT', '/vms/' + base.vm.id + '/buyer/' + base.buyer.id + '/add/' + this.dataset.value
            )


base = new BaseManager
