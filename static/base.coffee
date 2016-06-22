class BaseManager

    constructor: ->
        @get_vm 2
        @get_buyer 1

    ask: (method, url) ->
        xhr = new XMLHttpRequest
        xhr.open method, url, false
        xhr.send()
        if xhr.status == 200
            return JSON.parse(xhr.responseText)
        return

    get_vm: (vm_id) ->
        data = @ask 'GET', '/vms/' + vm_id
        if data
            @vm = new VendingMachine data
            @vm.render()
        return

    get_buyer: (buyer_id) ->
        data = @ask 'GET', '/buyer/' + buyer_id
        if data
            @buyer = new Buyer data
            @buyer.render()
        return


class VendingMachine

    constructor: (data) ->
        @id = data.vm.id
        @coins = data.vm.coins
        @goods = data.vm.goods
        @buffer = data.vm.buffer

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
                    <button class="good col-md-2" data-value="{{ good.name }}" data-price="{{ good.price }}" data-amount="{{ good.amount }}">
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
            <div id="message"></div>
            '
        @preview = document.getElementById('vm')
        content = swig.render template, locals: {vm: @}
        @preview.innerHTML = content
        vm = @
        @preview.querySelector('.good').addEventListener('click', ->
            success = base.ask 'PUT', '/vms/' + vm.id + '/pay/' + this.dataset.value
            if success
                base.get_vm vm.id
        )
        @preview.querySelector('.return').addEventListener('click', ->
            success = base.ask 'PUT', '/vms/' + vm.id + '/buyer/' + base.buyer.id + '/return'
            if success
                base.get_vm vm.id
                base.get_buyer base.buyer.id
        )


class Buyer

    constructor: (data) ->
        @id = data.buyer.id
        @coins = data.buyer.coins
    
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
                if data
                    base.get_vm base.vm.id
                    base.get_buyer base.buyer.id
                console.log this
                console.log vm
            )


base = new BaseManager
