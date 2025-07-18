from dataclasses import dataclass

from Options import Range, Toggle, Choice, PerGameCommonOptions


class BabyRatioRequired(Range):
    """Percentage of babies needed to win. There are 49 babies in total."""
    display_name = "Baby Ratio Required"
    range_start = 1
    range_end = 100
    default = 80

class IncludeChallenges(Toggle):
    """Include challenges. If disabled, the locations will be filler."""
    display_name = "Include Challenges"

class IncludeGreedMode(Choice):
    """Whether to include greed/greedier mode. If disabled, the locations will be filler. If any type of Greed Mode
    is excluded, then locations requiring all completion marks will be filler as well."""
    display_name = "Include Greed(ier) Mode"
    option_none = 0
    option_greed_mode_only = 1
    option_greedier_mode_only = 2
    option_greed_and_greedier = 3
    default = 1

class StartingCharacter(Choice):
    """The character that you start with."""
    display_name = "Starting Character"
    option_isaac = 0
    option_magdalene = 1
    option_cain = 2
    option_judas = 3
    option_blue_baby = 4
    option_eve = 5
    option_samson = 6
    option_azazel = 7
    option_lazarus = 8
    option_eden = 9
    option_lost = 10
    option_lilith = 11
    option_keeper = 12
    option_apollyon = 13
    option_forgotten = 14
    option_bethany = 15
    option_jacob_and_esau = 16
    option_tainted_isaac = 17
    option_tainted_magdalene = 18
    option_tainted_cain = 19
    option_tainted_judas = 20
    option_tainted_blue_baby = 21
    option_tainted_eve = 22
    option_tainted_samson = 23
    option_tainted_azazel = 24
    option_tainted_lazarus = 25
    option_tainted_eden = 26
    option_tainted_lost = 27
    option_tainted_lilith = 28
    option_tainted_keeper = 29
    option_tainted_apollyon = 30
    option_tainted_forgotten = 31
    option_tainted_bethany = 32
    option_tainted_jacob_and_esau = 33

@dataclass
class TBOIOptions(PerGameCommonOptions):
    include_greed_mode: IncludeGreedMode
    include_challenges: IncludeChallenges
    baby_ratio_required: BabyRatioRequired
    starting_character: StartingCharacter