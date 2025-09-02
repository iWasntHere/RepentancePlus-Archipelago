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
    default = 60

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

class ExcludeChallenges(Toggle):
    """
    Exclude challenges from possibly having a required item. This makes them entirely optional.
    """
    display_name = "Exclude Challenges"
    default = 1

class IncludeGreedMode(Choice):
    """
    Whether greed/greedier mode locations can have required items.
    This will extend to any locations that require the Greed Mode marks, such as "all marks" locations.
    None: Both Greed and Greedier modes will not be required to reach the goal.
    Greed Mode Only: Locations for Greed Mode might be required.
    Greedier Mode Only: Locations for Greedier Mode might be required.
    Greed and Greedier: Locations for both Greed and Greedier Mode might be required.
    """
    display_name = "Include Greed(ier) Mode"
    option_none = 0
    option_greed_mode_only = 1
    option_greedier_mode_only = 2
    option_greed_and_greedier = 3
    default = 1

class ExcludeRepetitiousLocations(Choice):
    """
    Exclude 'repetitious' locations (e.g. 'Break 100 Tinted Rocks') from possible having a required item.
    This makes them entirely optional.
    """
    display_name = "Exclude Repetitious Locations"
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

class FillerWeight(Range):
    """
    Base class for weighted filler.
    """
    range_start = 0
    range_end = 100
    default = 50

class ActiveRechargeWeight(FillerWeight):
    """How often filler items will be an active item recharge."""
    display_name = "Active Recharge Weight"
    default = 20

class TemporaryShieldWeight(FillerWeight):
    """How often filler items will be a temporary shield."""
    display_name = "Temporary Shield Weight"
    default = 30

class ThreeCoinsWeight(FillerWeight):
    """How often filler items will be three random coins."""
    display_name = "Three Coins Weight"
    default = 15

class ThreeCardsWeight(FillerWeight):
    """How often filler items will be three random cards."""
    display_name = "Three Cards Weight"
    default = 30

class ThreeRunesWeight(FillerWeight):
    """How often filler items will be three random runes."""
    display_name = "Three Runes Weight"
    default = 30

class ThreePillsWeight(FillerWeight):
    """How often filler items will be three random pills."""
    display_name = "Three Pills Weight"
    default = 15

class ThreeHeartsWeight(FillerWeight):
    """How often filler items will be three random hearts."""
    display_name = "Three Hearts Weight"
    default = 30

class ThreeBombsWeight(FillerWeight):
    """How often filler items will be three random bombs."""
    display_name = "Three Bombs Weight"
    default = 30

class ThreeKeysWeight(FillerWeight):
    """How often filler items will be three random keys."""
    display_name = "Three Keys Weight"
    default = 30

class FoolTrapWeight(FillerWeight):
    """How often filler items will force you to use The Fool."""
    display_name = "Fool Trap Weight"
    default = 5

class HighPriestessTrapWeight(FillerWeight):
    """How often filler items will force you to use The High Priestess."""
    display_name = "High Priestess Trap Weight"
    default = 3

class TowerTrapWeight(FillerWeight):
    """How often filler items will force you to use The Tower."""
    display_name = "Tower Trap Weight"
    default = 5

class EmperorTrapWeight(FillerWeight):
    """How often filler items will force you to use The Emperor."""
    display_name = "Emperor Trap Weight"
    default = 3

class DamoclesTrapWeight(FillerWeight):
    """How often filler items will force you to use Damocles."""
    display_name = "Damocles Trap Weight"
    default = 1

class ReverseChariotTrapWeight(FillerWeight):
    """How often filler items will force you to use The Chariot?."""
    display_name = "Chariot? Trap Weight"
    default = 5

class ReverseStarsTrapWeight(FillerWeight):
    """How often filler items will force you to use The Stars?."""
    display_name = "Stars? Trap Weight"
    default = 3

class ForgetMeNowTrapWeight(FillerWeight):
    """How often filler items will regenerate the current floor."""
    display_name = "Forget Me Now Trap Weight"
    default = 3

class TMTrainerTrapWeight(FillerWeight):
    """How often filler items will force TMTrainer into your inventory."""
    display_name = "TMTrainer Trap Weight"
    default = 1

class ClickerTrapWeight(FillerWeight):
    """How often filler items will randomly swap your character."""
    display_name = "Clicker Trap Weight"
    default = 1

class RunTrapWeight(FillerWeight):
    """How often filler items will force you to use The High Priestess?."""
    display_name = "Run Trap Weight"
    default = 3

class ReverseWheelOfFortuneTrapWeight(FillerWeight):
    """How often filler items will force you to use The Wheel of Fortune?."""
    display_name = "Wheel of Fortune? Trap Weight"
    default = 3

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
    exclude_challenges: ExcludeChallenges
    exclude_repeition: ExcludeRepetitiousLocations
    bossanity: Bossanity
    chapter_completionsanity: ChapterCompletionsanity
    character_completion_hints: CharacterCompletionHints
    baby_hints: BabyHints
    character_hints: CharacterHints
    hint_specificity: HintSpecificity

    active_recharge_weight: ActiveRechargeWeight
    temporary_shield_weight: TemporaryShieldWeight
    three_coins_weight: ThreeCoinsWeight
    three_cards_weight: ThreeCardsWeight
    three_runes_weight: ThreeRunesWeight
    three_pills_weight: ThreePillsWeight
    three_hearts_weight: ThreeHeartsWeight
    three_bombs_weight: ThreeBombsWeight
    three_keys_weight: ThreeKeysWeight

    fool_trap_weight: FoolTrapWeight
    high_priestess_trap_weight: HighPriestessTrapWeight
    tower_trap_weight: TowerTrapWeight
    emperor_trap_weight: EmperorTrapWeight
    damocles_trap_weight: DamoclesTrapWeight
    reverse_chariot_trap_weight: ReverseChariotTrapWeight
    reverse_stars_trap_weight: ReverseStarsTrapWeight
    forget_me_now_trap_weight: ForgetMeNowTrapWeight
    tmtrainer_trap_weight: TMTrainerTrapWeight
    clicker_trap_weight: ClickerTrapWeight
    run_trap_weight: RunTrapWeight
    reverse_wheel_of_fortune_trap_weight: ReverseWheelOfFortuneTrapWeight