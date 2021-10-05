# # we define our own function,
# # which can then be used for defining metrics
# #
# # see memory_measure in tree_values.py for
# # an example of a realistic metric function


# def draw_all_trees():
#     nomv_sdp_spp = tree_from_file(inputfile = './trees/nomv_sdp_spp')
#     nomv_ldp_spp = tree_from_file(inputfile = './trees/nomv_ldp_spp')
#     nomv_sdp_lpp = tree_from_file(inputfile = './trees/nomv_sdp_lpp')
#     nomv_ldp_lpp = tree_from_file(inputfile = './trees/nomv_ldp_lpp')

#     rtmv_sdp_spp = tree_from_file(inputfile = './trees/rtmv_sdp_spp')
#     rtmv_ldp_spp = tree_from_file(inputfile = './trees/rtmv_ldp_spp')
#     rtmv_sdp_lpp = tree_from_file(inputfile = './trees/rtmv_sdp_lpp')
#     rtmv_ldp_lpp = tree_from_file(inputfile = './trees/rtmv_ldp_lpp')

#     ppmv_sdp_spp = tree_from_file(inputfile = './trees/ppmv_sdp_spp')
#     ppmv_ldp_spp = tree_from_file(inputfile = './trees/ppmv_ldp_spp')
#     ppmv_sdp_lpp = tree_from_file(inputfile = './trees/ppmv_sdp_lpp')
#     ppmv_ldp_lpp = tree_from_file(inputfile = './trees/ppmv_ldp_lpp')

#     rmnt_sdp_spp = tree_from_file(inputfile = './trees/rmnt_sdp_spp')
#     rmnt_ldp_spp = tree_from_file(inputfile = './trees/rmnt_ldp_spp')
#     rmnt_sdp_lpp = tree_from_file(inputfile = './trees/rmnt_sdp_lpp')
#     rmnt_ldp_lpp = tree_from_file(inputfile = './trees/rmnt_ldp_lpp')

#     texprint(nomv_sdp_spp, filename = './output_trees/print_all/nomv_sdp_spp', tree_directory = './trees')
#     texprint(nomv_ldp_spp, filename = './output_trees/print_all/nomv_ldp_spp', tree_directory = './trees')
#     texprint(nomv_sdp_lpp, filename = './output_trees/print_all/nomv_sdp_lpp', tree_directory = './trees')
#     texprint(nomv_ldp_lpp, filename = './output_trees/print_all/nomv_ldp_lpp', tree_directory = './trees')

#     texprint(rtmv_sdp_spp, filename = './output_trees/print_all/rtmv_sdp_spp', tree_directory = './trees')
#     texprint(rtmv_ldp_spp, filename = './output_trees/print_all/rtmv_ldp_spp', tree_directory = './trees')
#     texprint(rtmv_sdp_lpp, filename = './output_trees/print_all/rtmv_sdp_lpp', tree_directory = './trees')
#     texprint(rtmv_ldp_lpp, filename = './output_trees/print_all/rtmv_ldp_lpp', tree_directory = './trees')

#     texprint(ppmv_sdp_spp, filename = './output_trees/print_all/ppmv_sdp_spp', tree_directory = './trees')
#     texprint(ppmv_ldp_spp, filename = './output_trees/print_all/ppmv_ldp_spp', tree_directory = './trees')
#     texprint(ppmv_sdp_lpp, filename = './output_trees/print_all/ppmv_sdp_lpp', tree_directory = './trees')
#     texprint(ppmv_ldp_lpp, filename = './output_trees/print_all/ppmv_ldp_lpp', tree_directory = './trees')

#     texprint(rmnt_sdp_spp, filename = './output_trees/print_all/rmnt_sdp_spp', tree_directory = './trees')
#     texprint(rmnt_ldp_spp, filename = './output_trees/print_all/rmnt_ldp_spp', tree_directory = './trees')
#     texprint(rmnt_sdp_lpp, filename = './output_trees/print_all/rmnt_sdp_lpp', tree_directory = './trees')
#     texprint(rmnt_ldp_lpp, filename = './output_trees/print_all/rmnt_ldp_lpp', tree_directory = './trees')