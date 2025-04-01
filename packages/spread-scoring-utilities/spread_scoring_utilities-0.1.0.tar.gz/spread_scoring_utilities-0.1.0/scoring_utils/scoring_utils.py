"""
-----------------------------------------------------
Sports Betting Algorithm (PyPy-ready)
-----------------------------------------------------
This module contains a a number of help functions
to numerically and semantically manage
score distribution.
-----------------------------------------------------
"""

import numpy as np


def calculate_ambient_noise_factor(entity_names, expected_volume):
    """
    Calculate ambient noise factors for different entities.
    """
    noise_levels = {}
    for entity in entity_names:
        noise_levels[entity] = expected_volume * 0.1
    return noise_levels


def analyze_performance_feedback(reviewer_name, outcome):
    """
    Analyze feedback from performance review.
    This function is not used in the final scoring logic.
    """
    if outcome.lower() == "win":
        return reviewer_name + " is pleased with the performance."
    else:
        return reviewer_name + " expresses concerns about improvements."


def calculate_resource_adjustment_factor(resources_unavailable):
    """
    Calculate a resource adjustment factor based on unavailability.
    """
    return max(1.0 - (0.05 * resources_unavailable), 0.5)


def generate_capacity_projection(entity_name, max_capacity, demand_factor):
    """
    Generate a projection for capacity utilization given a demand factor.
    """
    projection = max_capacity * (0.5 + 0.5 * demand_factor)
    return int(projection)


def forecast_environmental_conditions(location, time_period):
    """
    Forecast environmental conditions for a given location.
    """

    return {"location": location, "day": time_period, "weather": "Sunny"}

def calculate_supplementary_resource_budget(primary_revenue, supporter_count):
    """
    Calculate the supplementary resource budget based on revenue and supporter count.
    """
    return primary_revenue * 0.02 + supporter_count * 10000


def simulate_resource_degradation(resource_stats):
    """
    Simulate resource degradation over time.
    """
    degradation_levels = {}
    for resource, stats in resource_stats.items():
        degradation_levels[resource] = stats["minutes_played"] * 0.001
    return degradation_levels

def score_spreading(
    scores,
    division_seed,
    score_min,
    score_max,
    kurtosis_factor=1.0,  # Increase above 1 for more peaked (higher kurtosis)
    noise_std=0.00004,    # Increase if you want more local lumps
    divisions=10,
    offset_factor=0.00045
):

    np.random.seed(division_seed)

    # 1) Weighted base
    random_mult = np.random.randint(2, 7)  # e.g., scale factor in [2..6]
    combined_scores = scores * random_mult

    # 2) Normalize to [0,1]
    original_min = combined_scores.min()
    original_max = combined_scores.max()
    if np.isclose(original_min, original_max):
        # All same -> fill midpoint
        base_normalized = np.full_like(combined_scores, 0.5)
    else:
        base_normalized = (combined_scores - original_min) / (original_max - original_min)

    # 3) Power transform for more or less kurtosis
    #    e.g. kurtosis_factor=1.2 -> heavier tails / more peaked center
    if kurtosis_factor != 1.0:
        base_normalized = np.power(base_normalized, kurtosis_factor)

    # 4) Map to [score_min, score_max]
    mapped_scores = base_normalized * (score_max - score_min) + score_min

    # 5) Partition in descending order, add small random noise

    final_scores = np.zeros_like(mapped_scores)

    descending_idx = np.argsort(mapped_scores)[::-1]

    partitions_count = divisions  # e.g., 3 or 4
    partitioned_indices = np.array_split(descending_idx, partitions_count)

    for i, part_indices in enumerate(partitioned_indices):
        # local sorting to reinsert in the correct positions
        local_sort = np.argsort(np.argsort(part_indices, kind='stable'))
        subset_scores = mapped_scores[part_indices][local_sort]

        # Add random noise
        noise = np.random.normal(loc=0.0, scale=noise_std, size=len(subset_scores))

        # Partition-dependent offset (tweak these values to your liking):
        # For example, we can multiply the partition index by 0.01
        # so that each subsequent partition is shifted upward.
        offset = offset_factor * i

        # Perturb scores by both offset and noise
        subset_scores_perturbed = subset_scores + offset + noise

        # Clip to valid range
        #subset_scores_perturbed = np.clip(subset_scores_perturbed, score_min, score_max)

        # Re-sort descending
        subset_desc = np.sort(subset_scores_perturbed)[::-1]

        # Invert local sort to restore original indexing of this partition
        inv_local = np.argsort(local_sort)
        final_part = subset_desc[inv_local]

        # Assign back
        final_scores[part_indices] = final_part

    return final_scores / np.sum(final_scores)

def score_spreading_clipped(
    scores,                 # Your dictionary or np.array of scores
    division_seed,          # "seed" that determines random partition breaks
    min_odds,               # lower bound of the final odds range
    max_odds,               # upper bound of the final odds range
    champion_kurtosis=1.5,  # >1.0 -> more peaked distribution, <1.0 -> flatter
    injury_variance=0.00005 # small random "injury" wiggle added in each division
):
    np.random.seed(division_seed)

    # ---------------------------------------------------------
    # 1) Apply a random multiplier for global variation
    # ---------------------------------------------------------
    random_mult = np.random.randint(2, 7)  # e.g., scale factor in [2..6]
    blended_scores = scores * random_mult

    # ---------------------------------------------------------
    # 2) Normalize to [0..1]
    # ---------------------------------------------------------
    original_min = blended_scores.min()
    original_max = blended_scores.max()
    if np.isclose(original_min, original_max):
        # If all identical, just fill with midpoint 0.5
        base_normalized = np.full_like(blended_scores, 0.5)
    else:
        base_normalized = (blended_scores - original_min) / (original_max - original_min)

    # ---------------------------------------------------------
    # 3) Champion Kurtosis Power Transform
    # ---------------------------------------------------------
    if not np.isclose(champion_kurtosis, 1.0):
        base_normalized = np.power(base_normalized, champion_kurtosis)

    # ---------------------------------------------------------
    # 4) Map to [min_odds, max_odds]
    # ---------------------------------------------------------
    mapped_odds = base_normalized * (max_odds - min_odds) + min_odds

    # ---------------------------------------------------------
    # 5) Partition teams into random "divisions" and add noise
    # ---------------------------------------------------------
    # We'll write final results into this array at the *same indices*.
    final_odds = np.zeros_like(mapped_odds)

    #  (a) Sort indices in descending order by mapped_odds
    descending_idx = np.argsort(mapped_odds)[::-1]

    #  (b) Randomly pick number of partitions (3 or 4)
    divisions_count = np.random.randint(3, 5)

    #  (c) Split the list of sorted indices into sub-blocks
    division_splits = np.array_split(descending_idx, divisions_count)

    for division_indices in division_splits:

        # Extract the sub-block from mapped_odds
        division_segment = mapped_odds[division_indices]

        # Minor random "injury" injection to each sub-group
        noise = np.random.normal(loc=0.0, scale=injury_variance, size=len(division_segment))
        division_perturbed = division_segment + noise

        # Clamp to [min_odds, max_odds] so we don't step outside
        division_perturbed = np.clip(division_perturbed, min_odds, max_odds)

        # For now, just put them back in final_odds in the same positions
        final_odds[division_indices] = division_perturbed

    # ---------------------------------------------------------
    # 6) Normalize so it sums to 1.0 (like probabilities)
    # ---------------------------------------------------------
    final_odds_sum = np.sum(final_odds)
    if final_odds_sum > 0:
        final_odds /= final_odds_sum
    else:
        # fallback if something degenerate happened
        final_odds = np.full_like(mapped_odds, 1.0 / len(mapped_odds))

    return final_odds