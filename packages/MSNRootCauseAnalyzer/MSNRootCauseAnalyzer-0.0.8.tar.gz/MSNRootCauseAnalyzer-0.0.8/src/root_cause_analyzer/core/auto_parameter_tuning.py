# -- * coding: utf-8 -*-
# Description: Automatically tune the min_suprise parameter for the root cause analyzer.
# Pain Point: When setting the min_suprise to 0.0001, if the delta of metric movement is extremely high, the result will include noise; 
# conversely, if the delta is extremely low, the real causes will be overlooked.

import numpy as np

def get_ratio_beta_to_alpha(a, k = 16, bias=1.1):
    """
    regression formula to calculate the ratio of beta to alpha, which is used to adjust the min_suprise parameter.
    k and bias are from the practical tests.
    """
    return np.exp(-k * a) + bias


def js_divergence(p1, p2):
    p1 = p1 + 1e-12 if p1 == 0 else p1
    p2 = p2 + 1e-12 if p2 == 0 else p2
    m = 0.5 * (p1 + p2)
    kl_1 = p1 * np.log(p1 / m)
    kl_2 = p2 * np.log(p2 / m)
    return 0.5 * (kl_1 + kl_2)


def get_adjusted_min_suprise(alpha, pc):
    """
    Calculate the adjusted min_suprise parameter based on alpha and pc.
    alpha: The delta of metric movement.
    beta: The delta of metric movement under the condition of that specific segment.
    pc: the proportion of a certain segment's value to the total value.
    """
    ratio_beta_to_alpha = get_ratio_beta_to_alpha(abs(alpha))
    res = js_divergence(pc, pc * (1 + alpha * ratio_beta_to_alpha))
    return res


if __name__ == "__main__":

    a_list = [0.01, 0.0187, -0.024494, 0.05, -0.103937, -0.2, -0.3, -0.9]
    for a in a_list:
        print(f"alpha: {a}, ratio_beta_to_alpha:{get_ratio_beta_to_alpha(abs(a)):.2f}, min_suprise: {get_adjusted_min_suprise(a, 0.15):.6f}")

    print(js_divergence(0.194738, 0.203253))