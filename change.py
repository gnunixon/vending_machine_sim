def change_money(money, coins):
    """
    This function will change the given amount of money in more efficient
    mode. In our case we can use greedy algorithm, because there we have
    a canonical coin system.

    :param int money: the summ to change
    :param  coins: the dict with available coins in form {coin: umount}
    :returns: a dict in form {coin: amount, ...} with resulted coins
    :rtype: dict
    """
    ret = {}
    while money:
        # Let's filter the unusable coins (the amount is 0, or the coin value is
        # greater then the amount of money that we need to change
        coins = {k: v for k, v in coins.iteritems() if v > 0 and k <= money}

        # If there are not more available coins, then we can't finish the task
        # and it's time to return an empty dict :-( But usualy we will call
        # validate_transaction function before ask for change_money
        if not coins:
            return {}

        # Take the greatest value of coin
        coin_to_change = max(coins)

        # Take the maximum number of coins of this value
        coin_amount = min(money / coin_to_change, coins[coin_to_change])

        # Update the sum and the available amount of coins for next iteration
        money -= coin_to_change * coin_amount
        ret[coin_to_change] = coin_amount
        coins[coin_to_change] -= coin_amount
    return ret


def validate_transaction(money, coins):
    """
    This function will show us if we potentialy can change the given amount of
    money with available coins

    :param int money: the summ to change
    :param  coins: the dict with available coins in form {coin: umount}
    :returns: None if no money at all, False if no coins for that and True if ok
    :rtype: dict
    """
    # No money - no need to change
    if money == 0:
        return None

    # Calculate the amount of available money for change
    available_sum = sum([k * v for k, v in coins.iteritems()])

    # The user want more, so we can't make anything for him
    if money > available_sum:
        return False

    # It seems that the transaction is valid
    return True
