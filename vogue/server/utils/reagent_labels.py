from statistics import mean


def reagent_category_data(adapter, index_categroy: str) -> dict:
    """Preraring data for index performance view grouped on reagent label category""" 
    
    pipe = [{
        '$lookup': {
            'from': 'reagent_label_category', 
            'localField': 'index', 
            'foreignField': '_id', 
            'as': 'index_category'}
        }, {
        '$match': {
            'index_category.category': index_categroy}
        }] + _normalized_performance_pipe()

    aggregate_result = list(adapter.reagent_label_aggregate(pipe))

    average_normalized_peformance = []

    for data in aggregate_result:
        normalized_peformance = _build_normalized_index_performance_data(data)
        mean_performance = mean([val for fc, val in normalized_peformance])
        average_normalized_peformance.append({'name': data['_id']['index'], 
                                              'y': mean_performance,
                                              'nr_runs': len(normalized_peformance),
                                              'url': data['_id']['index'].replace(' ','')})
    return average_normalized_peformance


def reagent_label_data(adapter, index: str) -> list:
    """Preraring data for index performance view grouped on reagent label"""

    pipe = [{
        '$match': {
            'url': {'$eq': index}}
        }] + _normalized_performance_pipe()

    aggregate_result = list(adapter.reagent_label_aggregate(pipe))

    if not aggregate_result:
        return []

    data = aggregate_result[0]
    normalized_peformance = _build_normalized_index_performance_data(data)

    return normalized_peformance


def _build_normalized_index_performance_data(data: dict) -> list:
    """Filtering out flowcells with low performance."""

    normalized_peformance=[]
    ziped_data = zip(data['flowcell_performance'], 
                     data['normalized_index_performance'], 
                     data['flowcell_id'])

    for fc_performance, norm_performance, fc_id in ziped_data:
        if fc_performance > 0.1:
            normalized_peformance.append([fc_id, norm_performance])

    return normalized_peformance


def _normalized_performance_pipe() -> list:
    """Mongo aggregation pipe to get normalized index performance."""

    return [{
        '$match': {
            'flowcell_target_reads': {'$exists': 'True', '$ne': None, '$ne': 0}, 
            'flowcell_total_reads': {'$exists': 'True', '$ne': None, '$ne': 0}, 
            'index_target_reads': {'$exists': 'True', '$ne': None, '$ne': 0}, 
            'index_total_reads':{'$exists': 'True', '$ne': None, '$gt': 1000}}
        },{
        '$project': {
            'flowcell_id': 1, 
            'index_performance': {'$divide': ['$index_total_reads', '$index_target_reads']}, 
            'flowcell_performance': {'$divide': ['$flowcell_total_reads', '$flowcell_target_reads']}, 
            'index': 1}
        }, {
        '$project': {
            'normalized_index_performance': {'$divide': [
                    '$index_performance', '$flowcell_performance']}, 
            'flowcell_id': 1, 
            'flowcell_performance': 1, 
            'index': 1}
        }, {
        '$group': {
            '_id': {'index': '$index'}, 
            'normalized_index_performance': {'$push': '$normalized_index_performance'}, 
            'flowcell_performance': {'$push': '$flowcell_performance'},
            'flowcell_id': {'$push': '$flowcell_id'}}
        }]