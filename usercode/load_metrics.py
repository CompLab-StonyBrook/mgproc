# we define our own function,
# which can then be used for defining metrics
#
# see memory_measure in tree_values.py for
# an example of a realistic metric function


# load metrics
base = metrics_from_file(inputfile = './metrics/base', ranks = 1)
rank2 = metrics_from_file(inputfile = './metrics/base', ranks = 2)
filter_u = metrics_from_file(inputfile = './metrics/filtered_u', ranks = 1)

# load names as short cuts
# nomv_rtmv = 'nomv_rtmv'
# nomv_ppmv = 'nomv_ppmv'
# nomv_rmnt = 'nomv_rmnt'


def compare_heavy_np(name, metrics):
	# name = nomv_rtmv, nomv_ppmv, nomv_rmnt
	# metrics = base, filter_u

	filename = f"./comparisons/heavy_np/{name}"
	result = comparisons_from_file(inputfile = filename, directory = './trees/', metrics = metrics)

	result.show()

	return result

def base_compare_this(name):
	# name = nomv_rtmv, nomv_ppmv, nomv_rmnt
	# metrics = base, filter_u

	filename = f"{name}"
	result = comparisons_from_file(inputfile = filename, directory = './trees/', metrics = base)

	result.show()

	return result

def rank2_compare_this(name):
	# name = nomv_rtmv, nomv_ppmv, nomv_rmnt
	# metrics = base, filter_u

	filename = f"{name}"
	result = comparisons_from_file(inputfile = filename, directory = './trees/', metrics = rank2)

	result.show()

	return result