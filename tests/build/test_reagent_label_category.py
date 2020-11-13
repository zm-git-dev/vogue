from vogue.build.reagent_label_category import build_reagent_label_category


def test_build_reagent_label_category(lims_reagent_label):
    # GIVEN a lims_reagent_label with category, name, sequence given
    category = 'Illumina IDT'
    name = 'IDT_10nt_NXT_109'
    sequence = 'TAGGAAGCGG-CCTGGATTGG'

    lims_reagent_label.category = category
    lims_reagent_label.name = name
    lims_reagent_label.sequence = sequence

    # WHEN running build_reagent_label_category:
    mongo_reagent_label = build_reagent_label_category(lims_reagent_label)

    # THEN assert
    assert mongo_reagent_label == {
        '_id': name,
        'sequence': sequence,
        'category': category,
        'name': name
    }


def test_build_reagent_label_category_Nones(lims_reagent_label):
    # GIVEN a lims_reagent_label with category, name, sequence == None
    category = None
    name = None
    sequence = None

    lims_reagent_label.category = category
    lims_reagent_label.name = name
    lims_reagent_label.sequence = sequence

    # WHEN running build_reagent_label_category:
    mongo_reagent_label = build_reagent_label_category(lims_reagent_label)

    # THEN assert
    assert mongo_reagent_label == {
        '_id': name,
        'sequence': sequence,
        'category': category,
        'name': name
    }
