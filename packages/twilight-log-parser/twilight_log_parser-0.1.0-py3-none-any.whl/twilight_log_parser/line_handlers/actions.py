import copy
import re
from typing import Dict

from .. import constants
from .base import LineHandler
from ..core import Game


class ARHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for action round lines."""
        super().__init__(
            pattern=(
                rf"Turn (?P<turn>\d+), "
                rf"(?P<ar_owner>{constants.Side.US}|{constants.Side.USSR}) "
                rf"AR(?P<action_round>\d+): (?P<card>.*?): "
                rf"(((?P<play_type>"
                rf"{constants.PlayType.COUP}|"
                rf"{constants.PlayType.PLACE_INFLUENCE}|"
                rf"{constants.PlayType.EVENT}|"
                rf"{constants.PlayType.SPACE_RACE}|"
                rf"{constants.PlayType.REALIGNMENT}))|"
                rf"((US|USSR) discards ((?P<discard_card>.*)))|"
                rf"((.* Score is (?P<vp_player>.*) (?P<score>\d*).))|"
                rf"((?P<Formosan>Formosan) Resolution\* is no longer in play.)).*"
            )
        )

    def handle(self, game: Game, data: Dict, _: str) -> None:
        """Handle action round by processing play type and updating game state."""

        # Special case for WWBY: First awards VPs, then does event.
        # Leave event type empty
        # since it will be filled in by later log lines
        vp_player = data.get("vp_player")
        if vp_player is not None:
            updated_score = (
                -int(data["score"])
                if vp_player == constants.Side.US
                else int(data["score"])
            )
            data["updated_score"] = updated_score
        if data["discard_card"]:
            data["play_type"] = constants.PlayType.DISCARD
            data["discarded_cards"] = copy.deepcopy(
                game.current_play.discarded_cards
            ).union({data["discard_card"]})
        # formoson cancel is handled pretty weirdly - cancel the
        # effect and play type comes in a non-ar line later
        if data["Formosan"]:
            data["play_type"] = None
            data["us_effects"] = copy.deepcopy(game.current_play.us_effects).remove(
                "Formosan Resolution*"
            )
        del data["vp_player"]
        del data["score"]
        del data["discard_card"]
        del data["Formosan"]

        action_round = int(data["action_round"])

        data["action_executor"] = data["ar_owner"]
        if data["play_type"] == constants.PlayType.EVENT:
            game.current_event = data["card"]
            if game.is_us_card(data["card"]):
                data["action_executor"] = constants.Side.US
            elif game.is_ussr_card(data["card"]):
                data["action_executor"] = constants.Side.USSR

            if data["card"].endswith("*"):
                data["removed_cards"] = copy.deepcopy(
                    game.current_play.removed_cards
                ).union({data["card"]})
                data["discarded_cards"] = copy.deepcopy(
                    game.current_play.discarded_cards
                ).difference({data["card"]})
        else:
            data["discarded_cards"] = copy.deepcopy(
                game.current_play.discarded_cards
            ).union({data["card"]})

        data["possible_draw_cards"] = copy.deepcopy(
            game.current_play.possible_draw_cards
        ).difference({data["card"]})
        data["cards_in_hands"] = copy.deepcopy(
            game.current_play.cards_in_hands
        ).difference({data["card"]})

        data["order_in_ar"] = 0
        data["turn"] = int(data["turn"])
        data["action_round"] = action_round
        game.create_new_play(**data)


class NonARPlayHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for non-action round play lines."""
        super().__init__(
            pattern=(
                rf"(?P<play_type>{constants.PlayType.COUP}|"
                rf"{constants.PlayType.PLACE_INFLUENCE}|"
                rf"{constants.PlayType.EVENT}|"
                rf"{constants.PlayType.SPACE_RACE}|"
                rf"{constants.PlayType.REALIGNMENT}).*:.*"
            )
        )

    def handle(self, game: Game, data: Dict, line: str) -> None:
        """Handle non-action round plays by processing play type and updating game
        state."""
        prior_play_rec = game.current_play
        order_in_ar_adjustment = 0

        if prior_play_rec and prior_play_rec.play_type == constants.PlayType.DISCARD:
            prior_non_discard_play_rec = game.get_last_non_discard_play_record(
                ar_owner=prior_play_rec.ar_owner
            )
            if (
                prior_non_discard_play_rec
                and prior_non_discard_play_rec.card
                != constants.SpecialCards.UN_INTERVENTION
            ):
                prior_play_rec = prior_non_discard_play_rec
                data["action_executor"] = prior_play_rec.ar_owner

        if data["play_type"] == constants.PlayType.EVENT:
            event_pattern = rf"(?P<play_type>{constants.PlayType.EVENT}): (?P<card>.*)"
            event_match = re.match(event_pattern, line)
            data = event_match.groupdict()
            for play in game.get_all_plays_from_current_ar():
                if play.card == data["card"]:
                    game.current_play = play
                    game.current_event = play.card
                    prior_play_rec = play

                    # skip if the prior play type is an event,
                    # because we already have a record for that
                    if play.play_type == constants.PlayType.EVENT:
                        return

            game.current_event = data["card"]
            if game.is_us_card(data["card"]):
                data["action_executor"] = constants.Side.US
            else:
                data["action_executor"] = constants.Side.USSR

            if data["card"].endswith("*"):
                data["removed_cards"] = copy.deepcopy(
                    game.current_play.removed_cards
                ).union({data["card"]})
                data["discarded_cards"] = copy.deepcopy(
                    game.current_play.discarded_cards
                ).difference({data["card"]})
                data["cards_in_hands"] = copy.deepcopy(
                    game.current_play.cards_in_hands
                ).difference({data["card"]})
        else:
            if data.get("card"):
                data["discarded_cards"] = copy.deepcopy(
                    game.current_play.discarded_cards
                ).union({data["card"]})
                data["cards_in_hands"] = copy.deepcopy(
                    game.current_play.cards_in_hands
                ).difference({data["card"]})
        if prior_play_rec and data:
            # deal w/ defectors discard
            if (
                data.get("card") == constants.SpecialCards.DEFECTORS
                and prior_play_rec.action_round == 0
            ):
                headline_plays = game.get_all_plays_from_current_ar()
                for play in headline_plays:
                    if (
                        play.card == constants.SpecialCards.DEFECTORS
                        and play.ar_owner == constants.Side.US
                    ):
                        ussr_headline_rec = game.get_ussr_headline()
                        ussr_headline_rec.play_type = constants.PlayType.DISCARD
                        return
            # deal w/ duplicate rows
            if prior_play_rec.card == data.get(
                "card"
            ) and prior_play_rec.play_type == data.get("play_type"):
                return
            # special case to handle weirdness with WWBY
            if prior_play_rec.play_type is None:
                prior_play_rec.play_type = data["play_type"]
                return
            # this is a special case for Grain Sales -
            # if a card is returned, the coup is with
            # Grain sales, though the "return" will be the prior play
            if prior_play_rec.play_type == constants.PlayType.RETURN_TO_HAND:
                prior_play_rec = game.get_last_play_for_kwargs(
                    turn=prior_play_rec.turn,
                    card=constants.SpecialCards.GRAIN_SALES_TO_SOVIETS,
                )
                # once we've found the row we're looking for,
                # we increment it back up so we position this update correctly
                order_in_ar_adjustment = 1

            # this is a special case for Grain Sales where a card
            # is played (not returned) basically we update the
            # prior_play rec instead of creating a new row for this play
            elif (
                prior_play_rec.play_type
                == constants.PlayType.AWAITING_GRAIN_SALES_ACTION
            ):
                order_in_ar_adjustment = -1

            # this is a special case for missile envy,
            # where we need to update the played card
            # to the card that was revealed in an earlier log
            if (
                prior_play_rec.card == constants.SpecialCards.MISSILE_ENVY
                and data["play_type"] != constants.PlayType.EVENT
                and len(prior_play_rec.revealed_cards) > 0
            ):
                data["card"] = prior_play_rec.revealed_cards[0]

            # clear out anything we don't need to copy through from the old play record
            prior_play_rec_copy = game.get_copy_of_current_play_cleaned_up()

            # update the data dict to write into the new play record
            data = {**vars(prior_play_rec_copy), **data}
            data["order_in_ar"] += 1 + order_in_ar_adjustment
            game.create_new_play(**data)


class HeadlineHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for headline lines."""
        super().__init__(
            pattern=(
                r"Turn (?P<turn>\d+), Headline Phase: "
                r"(?P<ussr_card>.*) & (?P<us_card>.*):.*"
            )
        )

    def handle(self, game: Game, data: Dict, _: str) -> None:
        """Handle headline phase by processing both players' headline cards."""
        turn = int(data["turn"])
        action_round = 0
        play_type = constants.PlayType.EVENT

        discarded_cards = copy.deepcopy(game.current_play.discarded_cards)
        possible_draw_cards = copy.deepcopy(game.current_play.possible_draw_cards)
        removed_cards = copy.deepcopy(game.current_play.removed_cards)
        cards_in_hands = copy.deepcopy(game.current_play.cards_in_hands)

        if data["ussr_card"].endswith("*"):
            removed_cards = removed_cards.union({data["ussr_card"]})
            possible_draw_cards = possible_draw_cards.difference({data["ussr_card"]})
            cards_in_hands = cards_in_hands.difference({data["ussr_card"]})
        else:
            discarded_cards = discarded_cards.union({data["ussr_card"]})
            possible_draw_cards = possible_draw_cards.difference({data["ussr_card"]})
            cards_in_hands = cards_in_hands.difference({data["ussr_card"]})

        if data["us_card"].endswith("*"):
            removed_cards = removed_cards.union({data["us_card"]})
            possible_draw_cards = possible_draw_cards.difference({data["us_card"]})
            cards_in_hands = cards_in_hands.difference({data["us_card"]})
        else:
            discarded_cards = discarded_cards.union({data["us_card"]})
            possible_draw_cards = possible_draw_cards.difference({data["us_card"]})
            cards_in_hands = cards_in_hands.difference({data["us_card"]})

        game.create_new_play(
            turn=turn,
            action_round=action_round,
            order_in_ar=0,
            ar_owner=constants.Side.USSR,
            action_executor=constants.Side.USSR,
            card=data["ussr_card"],
            play_type=play_type,
            headline_order=None,
            discarded_cards=discarded_cards,
            possible_draw_cards=possible_draw_cards,
            removed_cards=removed_cards,
            cards_in_hands=cards_in_hands,
        )

        game.create_new_play(
            turn=turn,
            action_round=action_round,
            order_in_ar=0,
            ar_owner=constants.Side.US,
            action_executor=constants.Side.US,
            card=data["us_card"],
            play_type=play_type,
            headline_order=None,
            discarded_cards=discarded_cards,
            possible_draw_cards=possible_draw_cards,
            removed_cards=removed_cards,
            cards_in_hands=cards_in_hands,
        )


class HeadlineDetailsHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for headline details lines."""
        super().__init__(
            pattern=(
                rf"(?P<player>{constants.Side.US}|{constants.Side.USSR}) "
                r"Headlines (?P<card>.*)"
            )
        )

    def handle(self, game: Game, data: Dict, _: str) -> None:
        """Handle headline details by determining headline order."""
        # Get both headline plays for this turn
        headline_plays = [
            play
            for play in game.plays
            if play.turn == game.current_turn and play.action_round == 0
        ]

        # Find the matching headline play for this player
        matching_play = next(
            (
                play
                for play in headline_plays
                if play.action_executor == data["player"] and play.card == data["card"]
            ),
            None,
        )

        if not matching_play:
            # Switch AR owners and action executors for both headline plays
            for play in headline_plays:
                play.ar_owner = (
                    constants.Side.US
                    if play.ar_owner == constants.Side.USSR
                    else constants.Side.USSR
                )
                play.action_executor = (
                    constants.Side.US
                    if play.action_executor == constants.Side.USSR
                    else constants.Side.USSR
                )

        # Find the USSR and US plays
        ussr_play = next(
            play for play in headline_plays if play.ar_owner == constants.Side.USSR
        )
        us_play = next(
            play for play in headline_plays if play.ar_owner == constants.Side.US
        )

        # Compare ops values to determine order
        ussr_ops = game.CARDS[ussr_play.card].ops
        us_ops = game.CARDS[us_play.card].ops

        # Higher ops goes first (order=0), ties go to USSR
        if ussr_ops >= us_ops:
            ussr_play.headline_order = 0
            us_play.headline_order = 1
        else:
            ussr_play.headline_order = 1
            us_play.headline_order = 0


class PlaysCardHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for card play lines."""
        super().__init__(
            pattern=(
                rf"(?P<action_executor>{constants.Side.US}|{constants.Side.USSR}) "
                r"plays (?P<card>.*)"
            )
        )

    def handle(self, game: Game, data: Dict[str, str], _: str) -> None:
        """Handle card plays by processing play type and updating game state."""
        # Case for grain, UN
        prior_play_rec = game.get_copy_of_current_play_cleaned_up()

        # sometimes we see duplictes in "plays" lines, so just skip it
        prior_plays = game.get_all_plays_from_current_ar()
        for play in prior_plays:
            if play.card == data["card"]:
                return

        data = {**vars(prior_play_rec), **data}
        data["order_in_ar"] += 1

        if prior_play_rec.card == constants.SpecialCards.UN_INTERVENTION:
            data["play_type"] = constants.PlayType.DISCARD
            data["discarded_cards"] = copy.deepcopy(
                game.current_play.discarded_cards
            ).union({data["card"]})

            data["possible_draw_cards"] = copy.deepcopy(
                game.current_play.possible_draw_cards
            ).difference({data["card"]})
            data["cards_in_hands"] = copy.deepcopy(
                game.current_play.cards_in_hands
            ).difference({data["card"]})
        elif prior_play_rec.card == constants.SpecialCards.GRAIN_SALES_TO_SOVIETS:
            # at this point it's unclear how this card will get played
            # with grain sales - so we will use the following records to determine
            data["play_type"] = constants.PlayType.AWAITING_GRAIN_SALES_ACTION
        game.create_new_play(**data)


class SpaceRaceHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for space race lines."""
        super().__init__(
            pattern=(
                r"(?P<player>.*) advances to (?P<space_position>\d*) "
                r"in the Space Race."
            )
        )

    def handle(self, game: Game, data: Dict[str, str], _: str) -> None:
        """Handle space race advances by updating space position."""
        prior_play_rec = game.get_last_play_for_kwargs(ar_owner=data["player"])
        prior_play_rec.updated_space_position = int(data["space_position"])


class TargetCountryHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for target country lines."""
        super().__init__(pattern=r"(?:Target: |War in )(?P<target_country>.*)")

    def handle(self, game: Game, data: Dict[str, str], _: str) -> None:
        """Handle target country by adding to target countries list."""
        target_country = data["target_country"]

        current_play = game.current_play
        if (
            current_play.action_round == 0
            and game.current_event != game.current_play.card
        ):
            current_play = game.get_last_play_for_kwargs(
                turn=game.current_turn,
                card=game.current_event,
            )

        current_play.target_countries.append(target_country)


class RollHandler(LineHandler):
    def __init__(self) -> None:
        """Initialize handler for die roll lines."""
        super().__init__(
            pattern=rf"""(?x)
                    (?:
                        # Basic roll
                        (?P<player>{constants.Side.US}|{constants.Side.USSR})\s+rolls\s+
                        (?P<die_roll1>\d+)(?:\s.*)?$|
                        # Space race
                        Die roll:\s*(?P<die_roll2>\d+)\s*--\s*(?:Success|Failed)!\s*
                        \(Needed\s*(?P<needed>\d+)\s*or\s*less\)|
                        # Realignment
                        (?:SUCCESS|FAILURE):\s*(?P<die_roll3>\d+)\s*\[\s*\+\s*
                        (?P<ops>\d+)\s*-\s*(?P<multiplier>\d+)x(?P<stability>\d+)\s*=\s*
                        # War
                        (?P<net_result>-?\d+)\s*\]|
                        (?:VICTORY|DEFEAT):\s*(?P<die_roll4>\d+)
                        (?:\s*\(\+(?P<bonus>\d+)\))?(?:\s*\(-(?P<penalty>\d+)\))?
                        (?:\s*>=\s*|\s*<\s*)(?P<target>\d+)
                    )"""
        )

    def handle(self, game: Game, data: Dict[str, str], _: str) -> None:
        """Handle die roll lines by recording rolls for each player."""
        for key in data.keys():
            if key.startswith("die_roll"):
                roll = data[key]
                if roll is not None:
                    die_roll = int(roll)
                    break

        player = data.get("player", None)

        current_play = game.current_play
        if (
            current_play.action_round == 0
            and game.current_event != game.current_play.card
        ):
            current_play = game.get_last_play_for_kwargs(
                turn=game.current_turn,
                card=game.current_event,
            )

        if player is None:
            player = current_play.action_executor

        if player == constants.Side.US:
            current_play.us_die_rolls.append(die_roll)
        else:
            current_play.ussr_die_rolls.append(die_roll)
