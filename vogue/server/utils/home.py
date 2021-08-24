#!/usr/bin/env python


def home_samples(adapter, year, month):
    match = {"year": {"$eq": year}}
    if month:
        match["month"] = {"$eq": month}
    pipe = [
        {"$match": {"received_date": {"$exists": "True"}}},
        {
            "$project": {
                "month": {"$month": "$received_date"},
                "year": {"$year": "$received_date"},
                "category": 1,
                "priority": 1,
            }
        },
        {"$match": match},
        {
            "$group": {
                "_id": {"category": "$category", "priority": "$priority"},
                "count": {"$sum": 1},
            }
        },
    ]
    aggregate_result = adapter.samples_aggregate(pipe)
    samples = {}
    samples_output = {}
    cathegories = []
    for result in aggregate_result:
        cat = result["_id"].get("category", "missing")
        cathegories.append(cat)
        prio = result["_id"].get("priority", "missing")
        count = result.get("count", 0)
        if prio in samples:
            samples[prio][cat] = count
            continue
        samples[prio] = {cat: count}
        samples_output[prio] = []

    cathegories = list(set(cathegories))
    for prio, data in samples.items():
        for cat in cathegories:
            samples_output[prio].append(data.get(cat, 0))
    return samples_output, cathegories


def home_customers(adapter, year, month):
    match = {"year": {"$eq": year}}
    if month:
        match["month"] = {"$eq": month}
    pipe = [
        {"$match": {"received_date": {"$exists": "True"}}},
        {
            "$project": {
                "month": {"$month": "$received_date"},
                "year": {"$year": "$received_date"},
                "customer": 1,
            }
        },
        {"$match": match},
        {"$group": {"_id": {"customer": "$customer"}, "count": {"$sum": 1}}},
    ]
    aggregate_result = adapter.samples_aggregate(pipe)
    customers = {}
    for cust in aggregate_result:
        customer = cust["_id"].get("customer") if cust["_id"].get("customer") else "missing"
        customers[customer] = cust["count"]
    return customers
