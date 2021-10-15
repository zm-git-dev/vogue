#!/usr/bin/env python


def get_genotype_plate(adapter, plate_id: str) -> dict:
    plates_pipe = [
        {"$match": {"plate": {"$exists": "True"}, "snps.comp": {"$exists": "True"}}},
        {"$group": {"_id": {"plate": "$plate"}}},
    ]
    aggregate_result = list(adapter.genotype_analysis_aggregate(plates_pipe))
    plates = [plate["_id"]["plate"] for plate in aggregate_result]

    plate_id = plates[0] if not plate_id else plate_id

    samples_pipe = [{"$match": {"plate": plate_id, "snps.comp": {"$exists": "True"}}}]

    samples = list(adapter.genotype_analysis_aggregate(samples_pipe))
    data = []
    x_labels = list(samples[0]["snps"]["comp"].keys())
    y_labels = []
    x_labels.sort()
    for row, sample in enumerate(samples):
        comp = sample["snps"].get("comp")
        genotype = sample["snps"].get("genotype")
        sequence = sample["snps"].get("sequence")
        y_labels.append(sample["_id"])
        for col, key in enumerate(x_labels):
            internal = "".join(genotype[key])
            external = "".join(sequence[key])
            data.append((col, row, int(comp[key]), f"{internal} : {external}"))

    return {
        "data": data,
        "x_labels": x_labels,
        "y_labels": y_labels,
        "plates": plates,
        "plate_id": plate_id,
    }
