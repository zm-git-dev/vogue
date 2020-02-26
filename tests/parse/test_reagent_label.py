from vogue.parse.build.reagent_label import reagent_label_data


#def test_get_define_step_data(simple_artifact):
    # GIVEN a lims_reagent_label with category, name, sequence given
    
#    name = 'IDT_10nt_NXT_109'

def test_reagent_label_data(bcl_step):
    # GIVEN a bcl_step 
    
    # WHEN extracting the valid keys from the json, using validate_conf
    indexes = reagent_label_data(bcl_step=bcl_step)

    # THEN the output should be a list
    assert indexes == {}
