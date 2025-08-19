from dataclasses import dataclass

from Options import Range, Toggle, Choice, PerGameCommonOptions, FreeText


class GameMode(Choice):
    """
    Required goal.
    Baby Hunt: Collect a percentage of Co-Op babies in the item pool to win.
    Bounty Hunt: Unimplemented.
    """
    display_name = "Game Mode"
    option_baby_hunt = 0
    option_bounty_hunt = 1
    default = 0

class MaxBabies(Range):
    """The number of babies available to find in Baby Hunt mode."""
    range_start = 1
    range_end = 50
    default = 50

class BabyRatioRequired(Range):
    """Percentage of babies needed to win in Baby Hunt mode."""
    display_name = "Baby Ratio Required"
    range_start = 1
    range_end = 100
    default = 80

class ShopDonations(Range):
    """Number of shop donation locations to add. Each location costs 15 cents per check at a shop."""
    display = "Shop Donations"
    range_start = 0
    range_end = 50
    default = 10

class GreedDonations(Range):
    """Number of greed donation locations to add. Each location costs 15 cents per check after Ultra Greed."""
    display = "Shop Donations"
    range_start = 0
    range_end = 50
    default = 12

class ConsumableLocations(Range):
    """Number of locations to add that are found by using a special AP Rune."""
    display = "Consumable Locations"
    range_start = 0
    range_end = 50
    default = 20

class ChapterCompletionsanity(Choice):
    """
    Adds locations for clearing Chapter 4, and Chapter 5. Also adds a location for clearing each chapter with each
    character.
    Off: No additional locations are added.
    On Filler: Locations are added as filler.
    On: Locations are added and can contain any item.
    """
    display = "Chapter Completionsanity"
    option_off = 0
    option_on_filler = 1
    option_on = 2
    default = 0

class Bossanity(Choice):
    """
    Adds locations for defeating each boss as any character once.
    Note that this relies a lot on an undefeated boss spawning on a floor.
    Off: No additional locations are added.
    On Filler: Locations are added as filler.
    On: Locations are added and can contain any item.
    """
    display = "Bossanity"
    option_off = 0
    option_on_filler = 1
    option_on = 2
    default = 0

class IncludeChallenges(Choice):
    """
    Include challenges.
    Include: Challenges will reward a check.
    Exclude: Challenges will only reward filler.
    Remove: Challenges will not be added as locations.
    """
    display_name = "Include Challenges"
    option_include = 0
    option_exclude = 1
    option_remove = 2
    default = 2

class IncludeGreedMode(Choice):
    """
    Whether to include greed/greedier mode.
    None: Don't include Greed Mode whatsoever.
    Greed Mode Only: Locations for Greed Mode completions as characters will be added.
    Greedier Mode Only: Locations for Greedier Mode completions as characters will be added.
    Greed and Greedier: Locations for both Greed and Greedier Mode completions as characters will be added.
    """
    display_name = "Include Greed(ier) Mode"
    option_none = 0
    option_greed_mode_only = 1
    option_greedier_mode_only = 2
    option_greed_and_greedier = 3
    default = 1

class IncludeRepetitiousLocations(Choice):
    """
    Whether to include 'repetitious' locations (e.g. 'Break 100 Tinted Rocks').
    Include: Include these locations.
    Exclude: Locations exist, but will be filler.
    Remove: Locations will not be added.
    """
    display_name = "Include Repetitious Locations"
    option_include = 0
    option_exclude = 1
    option_remove = 2
    default = 1

class LockAllItems(Toggle):
    """All items will be locked and placed into the multiworld, even if they are unlocked by default. This includes
    trinkets, cards, and pills. Items that fail to generate in the multiworld will be unlocked by default.
    This means you may start with a 'default' selection of items different from Vanilla (Sad Onion may start locked, and
    Mom's Knife may start unlocked)!"""
    display_name = "Lock All Items"
    default = 0

class PoolRando(Choice):
    """
    Randomize item pools.
    Off: Vanilla item pool experience.
    Shuffle: Items will be shuffled into random pools, but only equal to the number of pools the item was originally in.
    Chaos: Unimplemented
    """
    display_name = "Pool Rando"
    option_off = 0
    option_shuffle = 1
    option_chaos = 2
    default = 0

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
    option_tainted_jacob = 33
    default = 0

class ExcludeCharacters(FreeText):
    """
    Exclude an entire character's locations. This will make it so ALL checks that require playing the character are
    filler. This includes challenges, completion marks, and chapter completionsanity.

    Must be formatted as "Character Name 1, Character Name 2, Character Name 3" and so on.

    Allowed values:
    Isaac, Tainted Isaac, Magdalene, Tainted Magdalene, Cain, Tainted Cain, Judas, Tainted Judas, ???, Tainted ???,
    Eve, Tainted Eve, Samson, Tainted Samson, Lazarus, Tainted Lazarus, Azazel, Tainted Azazel, Eden, Tainted Eden,
    Lost, Tainted Lost, Lilith, Tainted Lilith, Keeper, Tainted Keeper, Apollyon, Tainted Apollyon,
    Forgotten, Tainted Forgotten, Bethany, Tainted Bethany, Jacob and Esau, Tainted Jacob
    """
    display_name = "Exclude Characters"
    default = "Tainted Cain, Tainted Lazarus, Tainted Lost, Jacob and Esau, Tainted Jacob"

    def get_excluded_characters(self):
        return [name.strip() for name in self.value.split(", ")]

class LostDifficulty(Choice):
    """
    Whether the Lost logically needs its Holy Mantle starting upgrade to access any character-specific locations.
    Hard: Lost's Holy Mantle is logically required
    Impossible: Lost's Holy Mantle is not logically required
    """
    display_name = "Lost Difficulty"
    option_hard = 0
    option_impossible = 1
    default = 0

class CharacterCompletionHints(Toggle):
    """
    Fortune Teller machines may give hints for locations relevant to the currently played character.
    """
    display_name = "Character Completion Hints"
    default = 1

class BabyHints(Toggle):
    """
    Fortune Teller machines may give hints for the location of co-op babies in Baby Hunt mode.
    """
    display_name = "Baby Location Hints"
    default = 1

class CharacterHints(Toggle):
    """
    Fortune Teller machines may give hints for the location of characters.
    """
    display_name = "Character Location Hints"
    default = 1

class HintSpecificity(Choice):
    """
    How much information a Fortune Teller hint will give.
    Full: Hints will show the exact location and item name.
    Immersive: Hints for character items will be slightly vague, but still show the item's name and recipient.
    Vague: Same as Immersive, but all item names will be replaced with its progression classification.
    """
    display_name = "Hint Specificity"
    option_full = 0
    option_immersive = 1
    option_vague = 2
    default = 0

@dataclass
class TBOIOptions(PerGameCommonOptions):
    game_mode: GameMode
    max_babies: MaxBabies
    baby_ratio_required: BabyRatioRequired
    lock_all_items: LockAllItems
    pool_rando: PoolRando
    starting_character: StartingCharacter
    exclude_characters: ExcludeCharacters
    lost_difficulty: LostDifficulty
    shop_donations: ShopDonations
    greed_donations: GreedDonations
    consumable_locations: ConsumableLocations
    include_greed_mode: IncludeGreedMode
    include_challenges: IncludeChallenges
    include_repetitious: IncludeRepetitiousLocations
    bossanity: Bossanity
    chapter_completionsanity: ChapterCompletionsanity
    character_completion_hints: CharacterCompletionHints
    baby_hints: BabyHints
    character_hints: CharacterHints
    hint_specificity: HintSpecificity