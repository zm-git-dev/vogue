from vogue.parse.build.reagent_label import reagent_label_data


def test_reagent_label_data(build_bcl_step):
    # GIVEN a bcl_step with one sample run on 4 lanes

    index = "A07-UDI0049"
    bcl_step_id = "24-100451"
    flowcell_id = "hej"
    index_target_reads = "25"
    sample = "ACC6457A1"
    flowcell_type = "S4"
    define_step_udfs = {}
    index_total_reads = {
        1: {
            "# Reads": 5000000
        },
        2: {
            "# Reads": 5000000
        },
        3: {
            "# Reads": 5000000
        },
        4: {
            "# Reads": 5000000
        },
    }

    step = build_bcl_step(
        index=index,
        bcl_step_id=bcl_step_id,
        flowcell_id=flowcell_id,
        index_target_reads=index_target_reads,
        index_total_reads=index_total_reads,
        sample=sample,
        flowcell_type=flowcell_type,
        define_step_udfs=define_step_udfs,
    )

    # WHEN getting the reagent label data
    indexes = reagent_label_data(bcl_step=step)

    # THEN the output should be this
    assert indexes == {
        index: {
            "_id":
            f"{index}_{flowcell_id}",
            "url":
            index.replace(" ", ""),
            "index_total_reads":
            sum([v.get("# Reads", 0) for k, v in index_total_reads.items()]),
            "index_target_reads":
            float(index_target_reads) * 1000000,
            "flowcell_target_reads":
            float(index_target_reads) * 1000000,
            "index":
            index,
            "sample":
            sample,
            "lanes":
            index_total_reads,
            "flowcell_id":
            "hej",
            "flowcell_type":
            "",
            "define_step_udfs": {},
            "bcl_step_id":
            "24-100451",
            "flowcell_total_reads":
            sum([v.get("# Reads", 0) for k, v in index_total_reads.items()]),
        }
    }


def test_reagent_label_data_missing_udf(build_bcl_step):
    # GIVEN a bcl_step with one sample that gave no reads. And has a Index name with a space.

    index = "A07- UDI0049"
    bcl_step_id = "24-100451"
    flowcell_id = "hej"
    index_target_reads = "25"
    sample = "ACC6457A1"
    flowcell_type = "S4"
    define_step_udfs = {}
    index_total_reads = {1: {"# Reads": 0}}

    step = build_bcl_step(
        index=index,
        bcl_step_id=bcl_step_id,
        flowcell_id=flowcell_id,
        index_target_reads=index_target_reads,
        index_total_reads=index_total_reads,
        sample=sample,
        flowcell_type=flowcell_type,
        define_step_udfs=define_step_udfs,
    )

    # WHEN getting the reagent label data
    indexes = reagent_label_data(bcl_step=step)

    # THEN the output should be this
    assert indexes == {
        index: {
            "_id":
            f"{index}_{flowcell_id}",
            "url":
            index.replace(" ", ""),
            "index_total_reads":
            sum([v.get("# Reads", 0) for k, v in index_total_reads.items()]),
            "index_target_reads":
            float(index_target_reads) * 1000000,
            "flowcell_target_reads":
            float(index_target_reads) * 1000000,
            "index":
            index,
            "sample":
            sample,
            "lanes":
            index_total_reads,
            "flowcell_id":
            "hej",
            "flowcell_type":
            "",
            "define_step_udfs": {},
            "bcl_step_id":
            "24-100451",
            "flowcell_total_reads":
            sum([v.get("# Reads", 0) for k, v in index_total_reads.items()]),
        }
    }


def test_reagent_label_data_no_target(build_bcl_step):
    # GIVEN a bcl_step with one sample run on 4 lanes but target reads is None

    index = "A07-UDI0049"
    bcl_step_id = "24-100451"
    flowcell_id = "hej"
    index_target_reads = None
    sample = "ACC6457A1"
    flowcell_type = "S4"
    define_step_udfs = {}
    index_total_reads = {
        1: {
            "# Reads": 5000000
        },
        2: {
            "# Reads": 5000000
        },
        3: {
            "# Reads": 5000000
        },
        4: {
            "# Reads": 5000000
        },
    }

    step = build_bcl_step(
        index=index,
        bcl_step_id=bcl_step_id,
        flowcell_id=flowcell_id,
        index_target_reads=index_target_reads,
        index_total_reads=index_total_reads,
        sample=sample,
        flowcell_type=flowcell_type,
        define_step_udfs=define_step_udfs,
    )

    # WHEN getting the reagent label data
    indexes = reagent_label_data(bcl_step=step)

    # THEN the output should be this
    assert indexes == {
        index: {
            "_id":
            f"{index}_{flowcell_id}",
            "url":
            index.replace(" ", ""),
            "index_total_reads":
            sum([v.get("# Reads", 0) for k, v in index_total_reads.items()]),
            "flowcell_target_reads":
            0,
            "index":
            index,
            "sample":
            sample,
            "lanes":
            index_total_reads,
            "flowcell_id":
            "hej",
            "flowcell_type":
            "",
            "define_step_udfs": {},
            "bcl_step_id":
            "24-100451",
            "flowcell_total_reads":
            sum([v.get("# Reads", 0) for k, v in index_total_reads.items()]),
        }
    }
