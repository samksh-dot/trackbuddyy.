def calculate_trip_budget(travelers_count=4, days_count=2, intercity_transit=0.0, hotel_price_per_night=650.0, rooms_count=1, local_transit_est=400.0, attraction_tickets_per_person=150.0, daily_food_per_person=350.0, misc_per_person=100.0, student_discount_total=0.0):
    """
    Deterministically computes category-wise and per-person budgets:
    Total = Intercity + Local + Accommodation + Tickets + Food + Misc - Verified Discounts
    """
    travelers = max(1, int(travelers_count))
    days = max(1, int(days_count))
    nights = max(1, days - 1 if days > 1 else 1)

    # Accommodation: rooms needed or dorm beds
    accommodation_cost = round(float(hotel_price_per_night) * nights * rooms_count, 2)
    
    # Local transport (pooled or per person)
    local_transport_cost = round(float(local_transit_est), 2)
    
    # Intercity transport
    intercity_cost = round(float(intercity_transit), 2)
    
    # Attraction tickets
    tickets_cost = round(float(attraction_tickets_per_person) * travelers, 2)
    
    # Food & meals (e.g. ₹350/person/day for Jaipur dal baati, kachoris, thali)
    food_cost = round(float(daily_food_per_person) * days * travelers, 2)
    
    # Miscellaneous
    misc_cost = round(float(misc_per_person) * travelers, 2)

    subtotal = accommodation_cost + local_transport_cost + intercity_cost + tickets_cost + food_cost + misc_cost
    
    discounts = min(subtotal, round(float(student_discount_total), 2))
    total_cost = round(subtotal - discounts, 2)
    per_person = round(total_cost / travelers, 2)
    daily_budget = round(total_cost / days, 2)

    categories = [
        {'category': 'Accommodation', 'amount': accommodation_cost, 'percentage': round((accommodation_cost / subtotal) * 100, 1) if subtotal > 0 else 0},
        {'category': 'Food & Meals', 'amount': food_cost, 'percentage': round((food_cost / subtotal) * 100, 1) if subtotal > 0 else 0},
        {'category': 'Local Transport', 'amount': local_transport_cost, 'percentage': round((local_transport_cost / subtotal) * 100, 1) if subtotal > 0 else 0},
        {'category': 'Attraction Tickets', 'amount': tickets_cost, 'percentage': round((tickets_cost / subtotal) * 100, 1) if subtotal > 0 else 0},
        {'category': 'Intercity Transit', 'amount': intercity_cost, 'percentage': round((intercity_cost / subtotal) * 100, 1) if subtotal > 0 else 0},
        {'category': 'Miscellaneous', 'amount': misc_cost, 'percentage': round((misc_cost / subtotal) * 100, 1) if subtotal > 0 else 0}
    ]

    return {
        'total_cost': total_cost,
        'per_person_cost': per_person,
        'daily_budget': daily_budget,
        'discounts_applied': discounts,
        'subtotal': subtotal,
        'travelers_count': travelers,
        'days_count': days,
        'categories': categories
    }

def calculate_group_split_balances(expenses, members):
    """
    Given actual recorded expenses and members list:
    Calculates who paid what, their fair share, and debt settlement matrix (who owes whom).
    """
    if not members:
        return {'total_spent': 0, 'per_person_share': 0, 'member_balances': {}, 'settlements': []}

    num_members = len(members)
    member_paid = {m: 0.0 for m in members}
    total_spent = 0.0

    for exp in expenses:
        payer = exp.get('paid_by')
        amount = float(exp.get('amount', 0.0))
        total_spent += amount
        if payer in member_paid:
            member_paid[payer] += amount
        else:
            member_paid[payer] = amount

    fair_share = round(total_spent / num_members, 2)
    balances = {m: round(member_paid.get(m, 0.0) - fair_share, 2) for m in members}

    # Calculate optimal settlement transfers
    debtors = []
    creditors = []
    for m, bal in balances.items():
        if bal < -0.01:
            debtors.append({'member': m, 'amount': -bal})
        elif bal > 0.01:
            creditors.append({'member': m, 'amount': bal})

    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)

    settlements = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        settle_amt = min(debtor['amount'], creditor['amount'])
        
        if settle_amt > 0.01:
            settlements.append({
                'from': debtor['member'],
                'to': creditor['member'],
                'amount': round(settle_amt, 2)
            })
            debtor['amount'] -= settle_amt
            creditor['amount'] -= settle_amt

        if debtor['amount'] <= 0.01:
            i += 1
        if creditor['amount'] <= 0.01:
            j += 1

    return {
        'total_spent': round(total_spent, 2),
        'per_person_share': fair_share,
        'member_paid': member_paid,
        'member_balances': balances,
        'settlements': settlements
    }
