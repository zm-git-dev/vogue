import pymongo
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.trending
from vogue.load.lims import MongoSample
from argparse import ArgumentParser

DESC = ''


def build_sample(sample_id):
    MS = MongoSample(sample_id)
    MS.get_sample_level_data()
    MS.get_concantration_and_nr_defrosts()
    MS.get_sequenced_date()
    MS.get_received_date()
    MS.get_prepared_date()
    MS.get_delivery_date()
    MS.get_times()
    new_id = db.sample.insert_one(MS.mongo_sample).inserted_id

def build_all():
    from genologics.lims import Lims
    from genologics.config import BASEURI,USERNAME,PASSWORD
    lims = Lims(BASEURI,USERNAME,PASSWORD)
    for sample in lims.get_samples():
        build_sample(sample.id)

def main(args):
    if args.sample_id:
        build_sample(args.sample_id)
    else:
        build_all()        


if __name__ == "__main__":
    parser = ArgumentParser(description=DESC)
    parser.add_argument('-s', dest = 'sample_id', default = None,
                        help='Sample Lims id for')
                 

    args = parser.parse_args()

    main(args)