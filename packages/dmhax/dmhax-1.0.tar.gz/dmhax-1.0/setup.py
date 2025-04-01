from setuptools import setup, find_packages

setup(
    name='dmhax',
    version='1.0',
    packages=find_packages(),
    install_requires = [],
    entry_points = {
        "console_scripts" : [
            "dmx = dmhax:get_help",
            "dmx-sum = dmhax:get_sum_of_plane",
            "dmx-sex = dmhax:get_gender_slice",
            "dmx-slice = dmhax:get_slice",
            "dmx-slice-x` = dmhax:get_slice_x",
            "dmx-slice-y = dmhax:get_slice_y",
            "dmx-slice-z = dmhax:get_slice_z",
            "dmx-dice = dmhax:get_dice",
            "dmx-dice-x = dmhax:get_dice_x",
            "dmx-dice-y = dmhax:get_dice_y",
            "dmx-dice-z = dmhax:get_dice_z",
            "dmx-apriori = dmhax:get_apriori",
            "dmx-partition = dmhax:get_partition",
            "dmx-fp-growth = dmhax:get_fp_growth",
            "dmx-i = dmhax:get_transactions",
        ]
    }
    )