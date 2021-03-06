from kaa.experi_init import *
from kaa.temp.pca_strat import SlidingPCAStrat
from kaa.templates import MultiStrategy

from models.LL import LL, LL_UnitBox
from kaa.log import Output
from kaa.modes import BundleTransMode


def test_LL():
    num_steps = 200
    model = LL()

    experi_input = dict(model=model, #Encompass strat initilizations?
                        strat=None,
                        label="SapoLL",
                        num_steps=num_steps)

    harosc = ProjectionPlotExperiment(experi_input)
    harosc.execute(0, 1, 2, plot_border_traj=False)

def test_arch_LL():
    use_supp = True
    use_pregen = False

    num_trajs = 5000

    delta = 0.2
    num_steps_one = int(20 / delta)
    num_steps_two = int(20 / delta)
    num_steps_three = int(20 / delta)

    init_box_one = ((1.19, 1.21), (1.04, 1.06), (1.49, 1.51), (2.39, 2.41), (0.99, 1.01), (0.09, 0.11), (0.44, 0.46))
    init_box_two = ((1.15, 1.25), (1, 1.1), (1.45, 1.55), (2.35, 2.45), (0.95, 1.05), (0.05, 0.15), (0.4, 0.5))
    init_box_three = ((1.1, 1.3), (0.95, 1.15), (1.4, 1.6), (2.3, 2.5), (0.9, 1.1), (0, 0.2), (0.35, 0.55))


    model_one = LL_UnitBox(delta=delta, init_box=init_box_one)
    model_two = LL_UnitBox(delta=delta, init_box=init_box_two)
    model_three = LL_UnitBox(delta=delta, init_box=init_box_three)

    pca_window_size = 10
    lin_window_size = 5

    #pca_strat_one = SlidingPCAStrat(model_one, lifespan=pca_window_size)
    #lin_strat_one = SlidingLinStrat(model_one, lifespan=lin_window_size)

    #ran_static_strat_one = RandomDiagStaticStrat(model_one, 40)
    pca_strat_one = SlidingPCAStrat(model_one, 10)

    experi_input_one = dict(model=model_one,
                            strat=pca_strat_one,
                            label=f"LALO21 W=0.01",
                            num_steps=num_steps_one,
                            supp_mode = use_supp,
                            pregen_mode = use_pregen,
                            num_trajs=num_trajs,
                            trans_mode=BundleTransMode.AFO,
                            restrict_inter = (-10, 10))


    #pca_strat_two = SlidingPCAStrat(model_two, lifespan=pca_window_size)
    #lin_strat_two = SlidingLinStrat(model_two, lifespan=lin_window_size)

    #ran_static_strat_two = RandomDiagStaticStrat(model_two, 30)
    pca_strat_two = SlidingPCAStrat(model_two, 10)

    experi_input_two = dict(model=model_two,
                            strat=pca_strat_two,
                            label=f"LALO21 W=0.05",
                            num_steps=num_steps_two,
                            supp_mode = use_supp,
                            pregen_mode = use_pregen,
                            num_trajs=num_trajs,
                            trans_mode=BundleTransMode.AFO,
                            restrict_inter = (-10, 10))

    #ran_static_strat_three = RandomDiagStaticStrat(model_three, 30)
    pca_strat_three = SlidingPCAStrat(model_three, 10)

    experi_input_three = dict(model=model_three,
                            strat=pca_strat_three,
                            label=f"LALO21 W=0.1",
                            num_steps=num_steps_three,
                            supp_mode = use_supp,
                            pregen_mode = use_pregen,
                            num_trajs=num_trajs,
                            trans_mode=BundleTransMode.AFO,
                            restrict_inter = (-10, 10))

    experi = ProjectionPlotExperiment(experi_input_one, experi_input_two, experi_input_three, label="LALO20")
    experi_data = experi.execute(3, ylims=(1.5,5), abs_time=20)
    Output.prominent(f"Final Width for LALO21 W=0.01: {experi_data[0][1][3]}")
    Output.prominent(f"Final Width for LALO21 W=0.05: {experi_data[1][1][3]}")
    Output.prominent(f"Final Width for LALO21 W=0.1: {experi_data[2][1][3]}")

    return experi_data