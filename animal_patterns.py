from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.utils import is_request_type, is_intent_name
import random, json, sys


# Constants/format strings used as part of message responses

INVOCATION_NAME = "Animal Patterns"
LAUNCH_WELCOME_MESSAGE = "Welcome to {}!".format(INVOCATION_NAME)
LAUNCH_CALL_TO_ACTION = "<s>We need your pattern powers to find them!</s> <p>Here's the first pattern:</p>"
REPROMPT_MESSAGE = "<say-as interpret-as='interjection'>ahem</say-as><s>Here's the pattern again:</s>"
ANIMAL_FOUND_MESSAGE = "<s><say-as interpret-as='interjection'>{}</say-as>, you found the {} </s> {}"
WRONG_ANIMAL_MESSAGE = "<s><say-as interpret-as='interjection'>{}</say-as>, {} wasn't the right animal.</s> <s>Try again!</s>"
NEXT_PATTERN_MESSAGE = "<s>Now here's the next pattern</s>"
LAST_PATTERN_MESSAGE = "<s>Only one more to go.</s> <s>Here's the last pattern</s>"
GOODBYE_MESSAGE = "Goodbye!"
DONE_MESSAGE_START = "<s>And you found all the animals!</s> <say-as interpret-as='interjection'>{}</say-as>"
DONE_MESSAGE_END = "<audio src='https://s3.amazonaws.com/ask-soundlibrary/human/amzn_sfx_large_crowd_cheer_01.mp3'/> <s>{}</s>".format(GOODBYE_MESSAGE)
HELP_MESSAGE = "To play {}, listen to the animal pattern, and say the name of the animal that comes next! {}"
HELP_MESSAGE_PATTERN = "<s>Here's the pattern</s>"
ERROR_MESSAGE = "<s>Sorry, I didn't understand that, what did you say?</s>"
INTRA_PATTERN_BREAK = " <break time='350ms'/> "
INTER_PATTERN_BREAK = " <break time='1s'/> "
CARD_TITLE = "Pattern #{}"
CARD_TITLE_DONE = GOODBYE_MESSAGE
CARD_TEXT_DONE = "You did it!"
CARD_TITLE_HELP = "Help"
WHAT_COMES_NEXT = " <break time='350ms'/> What comes next?"
RIGHT_ANIMAL_INTERJECTIONS = ["alrighty", "way to go", "bravo", "bingo", "righto", "wow"]
ALL_DONE_INTERJECTIONS = ["well done", "hurray"]
WRONG_ANIMAL_INTERJECTIONS = ["nice try", "good try", "almost", "oops", "hmmm"]

# Internal constants

ANIMAL_INTENT_NAME = "AnimalIntent"
ANIMAL_SLOT_NAME = "Animal"

GAME_TYPES = ["farm", "zoo", "pet"]
GAME_META = {
    "farm": {
        "animals": ["dog", "horse", "rooster", "sheep", "turkey"],
        "launch_message": LAUNCH_WELCOME_MESSAGE + "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_horse_gallop_4x_03.mp3'/> <audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_horse_neigh_01.mp3'/> <say-as interpret-as='interjection'>uh oh!</say-as> <s>Old MacDonald left his gate open and his animals ran away from the farm</s>" + LAUNCH_CALL_TO_ACTION,
        "done_message": DONE_MESSAGE_START + "<s>Old MacDonald is so happy to have all his animals back.</s>" + DONE_MESSAGE_END
    },
    "zoo": {
        "animals": ["bear", "elephant", "lion", "monkey", "wolf"],
        "launch_message": LAUNCH_WELCOME_MESSAGE + "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_elephant_05.mp3'/> <say-as interpret-as='interjection'>yikes!</say-as> <s>A bunch of animals from the local zoo are on the loose all over town! </s>" + LAUNCH_CALL_TO_ACTION,
        "done_message": DONE_MESSAGE_START + "<s>Now all the animals are back at the zoo safe and sound.</s>" + DONE_MESSAGE_END
    },
    "pet": {
        "animals": ["dog", "chicken", "cat", "bird", "rat"],
        "launch_message": LAUNCH_WELCOME_MESSAGE + "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_dog_med_bark_2x_01.mp3'/> <say-as interpret-as='interjection'>ruh roh!</say-as> <s>Polly left her back door open and all her pets ran away from home.</s>" + LAUNCH_CALL_TO_ACTION,
        "done_message": DONE_MESSAGE_START + "<s>Polly is so happy to have her pets back at home.</s>" + DONE_MESSAGE_END
    }
}

SESSION_STATE_KEY = "STATE"

SOUNDS = {
    "bear": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_bear_roar_small_01.mp3'/>",
    "bird": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_bird_robin_chirp_1x_01.mp3'/>",
    "cat": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_cat_meow_1x_01.mp3'/>",
    "chicken": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_chicken_cluck_01.mp3'/>",
    "dog": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_dog_med_bark_2x_01.mp3'/>",
    "elephant": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_elephant_01.mp3'/>",
    "horse": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_horse_neigh_01.mp3'/>",
    "lion": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_lion_roar_02.mp3'/>",
    "monkey": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_monkey_chimp_01.mp3'/>",
    "rat": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_rat_squeaks_01.mp3'/>",
    "rooster": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_rooster_crow_01.mp3'/>",
    "sheep": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_sheep_baa_01.mp3'/>",
    "turkey": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_turkey_gobbling_01.mp3'/>",
    "wolf": "<audio src='https://s3.amazonaws.com/ask-soundlibrary/animals/amzn_sfx_wolf_howl_02.mp3'/>"
}

# A list of all pattern types, keyed by difficulty, 1 being the least difficult and 5 being the most difficult.
# The placeholder constant represents the name of an animal.
# The second value in the tuple is the number of distinct animals in the pattern.
# Used by generate_pattern() below to randomly generate a pattern of given difficulty.
PATTERNS = {
    1: [ ("{0} {1}", 2)],
    2: [ ("{0} {0} {1}", 2),
         ("{0} {1} {1}", 2),
         ("{0} {1} {0}", 2)],
    3: [ ("{0} {1} {2}", 3) ],
    4: [ ("{0} {0} {1} {1}", 2),
         ("{0} {1} {1} {0}", 2)],
    5: [ ("{0} {1} {0} {2}", 3),
         ("{0} {0} {1} {2}", 3),
         ("{0} {1} {1} {2}", 3),
         ("{0} {1} {2} {1}", 3),
         ("{0} {1} {2} {2}", 3)]
}

# Helper functions

def get_random(arr):
    """Return random element of array arr."""
    return arr[random.randint(0, len(arr)-1)]


# generate pattern format string given difficulty level
# returns (ssml_pattern, card_pattern, num_animals, expected_index)
def generate_pattern(difficulty):
    """Generate a random pattern given a pattern difficulty level. Used by next_pattern().

    Difficulty ranges from 1 to 5, 1 being the least difficult.
    Returns a tuple of (ssml_pattern, card_pattern, num_animals, expected_index).
    ssml_pattern: format string with placeholders for animal names, used in voice response.
    card_pattern: format string with placeholders for animal names, used in card text.
    num_animals: number of distinct animals in the pattern
    expected_index: index of format string placeholder that corresponds to the right pattern answer
    """
    
    possible_format_strings = []
    patterns_for_difficulty = PATTERNS[difficulty]

    # For given difficulty, generate all possible patterns, using pattern templates in PATTERNS
    for p, animal_count in patterns_for_difficulty:
        p_list = p.split()
        p_with_intra_breaks = INTRA_PATTERN_BREAK.join(p_list)
        p_with_inter_breaks = p_with_intra_breaks + INTER_PATTERN_BREAK + p_with_intra_breaks
        for i in range(0, len(p_list)):
            if i == 0:
                ssml_p = p_with_inter_breaks + WHAT_COMES_NEXT
            else:
                ssml_p = p_with_inter_breaks + INTER_PATTERN_BREAK + INTRA_PATTERN_BREAK.join(p_list[0:i]) + WHAT_COMES_NEXT
            card_p = ' '.join(p_list + p_list + p_list[0:i])
            possible_format_strings.append((ssml_p, card_p, animal_count, int(p_list[i][1])))

    # Return random pattern format string
    return get_random(possible_format_strings)


def next_pattern(state):
    """Update session state object with pattern information for next pattern question.

    Returns the number of remaining questions.
    """
    
    # Move from the previous state to the current state.
    # Only applicable if this is the not the first pattern question.
    # "expected" is only present after the first pattern question.
    if "expected" in state:

        # Previous correct answer is removed as possibility for future questions.
        state["animals_missing"].remove(state["expected"])

        # If all animals have been found, then we're done.
        if len(state["animals_missing"]) == 0:
            return 0

        # For next question, update difficulty based on number of user retries for previous question.
        # Difficulty stays the same for 1 miss.
        if state["retries"] == 0:
            state["difficulty"] = min(state["difficulty"]+1, 5)
        elif state["retries"] > 1:
            state["difficulty"] = max(state["difficulty"]-1, 1)

        # Reset "retries" to 0 for new question
        state["retries"] = 0

    # Randomly select an animal that will be the next right answer.
    expected = get_random(state["animals_missing"])
    state["expected"] = expected

    # Generate random pattern format string with animal placeholders.
    (ssml_p, card_p, num_animals_in_pattern, expected_index) = generate_pattern(state["difficulty"])

    # Randomly select other animals that will appear in pattern,
    #  but don't include the animal chosen to be the next right answer.
    # Fill in placeholder strings with all animals.
    animals_copy = GAME_META[state["game_type"]]["animals"].copy()
    animals_copy.remove(expected)

    if num_animals_in_pattern == 2:
        if expected_index == 0:
            animal_zero = expected
            animal_one = get_random(animals_copy)
        else:
            animal_zero = get_random(animals_copy)
            animal_one = expected

        state["ssml_pattern"] = ssml_p.format(animal_zero, animal_one)
        state["card_pattern"] = card_p.format(animal_zero, animal_one)
    
    else: # num_animals_in_pattern has to be 3
        if expected_index == 0:
            animal_zero = expected
            animal_one = animals_copy[random.randint(0, len(animals_copy)-1)]
            animals_copy.remove(animal_one)
            animal_two = animals_copy[random.randint(0, len(animals_copy)-1)]
        elif expected_index == 1:
            animal_zero = animals_copy[random.randint(0, len(animals_copy)-1)]
            animals_copy.remove(animal_zero)
            animal_one = expected
            animal_two = animals_copy[random.randint(0, len(animals_copy)-1)]
        else:
            animal_zero = animals_copy[random.randint(0, len(animals_copy)-1)]
            animals_copy.remove(animal_zero)
            animal_one = animals_copy[random.randint(0, len(animals_copy)-1)]
            animal_two = expected

        
        state["ssml_pattern"] = ssml_p.format(animal_zero, animal_one, animal_two)
        state["card_pattern"] = card_p.format(animal_zero, animal_one, animal_two)

    return len(state["animals_missing"])


def create_game(handler_input):
    """Create new game, initializing session state, and responding with launch welcome message"""

    # Choose a game type ("farm", "zoo", "pet"), which will determine type of welcome message and other prompts later on.
    game_type = get_random(GAME_TYPES)

    # Initial state, start with pattern difficulty at lowest level.
    state = {
        "game_type": game_type,
        "animals_missing": GAME_META[game_type]["animals"].copy(),
        "difficulty": 1,
        "retries": 0
    }

    # Set first pattern question.
    next_pattern(state)
    handler_input.attributes_manager.session_attributes[SESSION_STATE_KEY] = state

    # Set prompts and card for response.
    speech_text = GAME_META[state["game_type"]]["launch_message"] + state["ssml_pattern"]
    handler_input.response_builder.speak(speech_text).ask(REPROMPT_MESSAGE + state["ssml_pattern"]).set_card(SimpleCard(CARD_TITLE.format(1), state["card_pattern"])).set_should_end_session(False)
        
    return handler_input.response_builder.response



# Request handlers, covering the following intents:
# LaunchRequest
# IntentRequest: AnimalIntent, HelpIntent, StopIntent, CancelIntent, FallbackIntent
# SessionEndedRequest

sb = SkillBuilder()


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))    
def launch_request_handler(handler_input):
    """Create the game. Invoked when user says: 'Alexa, open Animal Patterns.'"""
    
    return create_game(handler_input)


@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name(ANIMAL_INTENT_NAME)(input) or
        is_intent_name("AMAZON.FallbackIntent")(input))
def animal_intent_handler(handler_input):
    """Handle AnimalIntent and FallbackIntent

    Typically invoked when user responds with an animal name for a pattern question.
    Validates whether the provided animal is the right answer. If it is, then the next question is returned,
      unless there are no more questions, in which case the game is ended.
    If the animal name is wrong, the same pattern question is returned with a prompt to retry.

    If this gets invoked out-of-session, a new game is created.
    If this gets invoked through the FallbackIntent, the handler behaves as if an empty animal response was provided.
    """

    try:
        state = handler_input.attributes_manager.session_attributes[SESSION_STATE_KEY]
    except:
        # This is likely an out of session request and there is no prior game state. So let's create a new game.
        return create_game(handler_input)

    animal = ""
    try:
        animal = handler_input.request_envelope.request.intent.slots[ANIMAL_SLOT_NAME].value.lower()
    except:
        # Can get here because of FallbackIntent. Treat as if the provided animal is wrong.
        pass

    # Empty animal is set to "that", which is interpreted as a wrong animal below and makes sense when formatting the response message.
    if animal == "":
        animal = "that"

    # User got the animal right.
    if animal == state["expected"]:
        speech_text = ANIMAL_FOUND_MESSAGE.format(get_random(RIGHT_ANIMAL_INTERJECTIONS), animal, SOUNDS[animal])

        # Set up the next pattern question.
        num_animals_remaining = next_pattern(state)
        num_animals_found = len(GAME_META[state["game_type"]]["animals"]) - num_animals_remaining
        
        if num_animals_remaining > 0:
            if num_animals_remaining == 1:
                speech_text += LAST_PATTERN_MESSAGE + state["ssml_pattern"]
            else:
                speech_text += NEXT_PATTERN_MESSAGE + state["ssml_pattern"]
            
            handler_input.response_builder.speak(speech_text).ask(REPROMPT_MESSAGE + state["ssml_pattern"]).set_card(SimpleCard(CARD_TITLE.format(num_animals_found+1), state["card_pattern"])).set_should_end_session(False)
        else:
            # No more animals to be found, game over.
            speech_text += GAME_META[state["game_type"]]["done_message"].format(get_random(ALL_DONE_INTERJECTIONS))
            handler_input.response_builder.speak(speech_text).set_card(SimpleCard(CARD_TITLE_DONE, CARD_TEXT_DONE)).set_should_end_session(True)
    else:
        # User got the animal wrong. Update retry counter and return same pattern.
        state["retries"] += 1
        speech_text = WRONG_ANIMAL_MESSAGE.format(get_random(WRONG_ANIMAL_INTERJECTIONS), animal) + state["ssml_pattern"]
        num_animals_found = len(GAME_META[state["game_type"]]["animals"]) - len(state["animals_missing"])
        handler_input.response_builder.speak(speech_text).ask(REPROMPT_MESSAGE + state["ssml_pattern"]).set_card(SimpleCard(CARD_TITLE.format(num_animals_found+1), state["card_pattern"])).set_should_end_session(False)
        
    return handler_input.response_builder.response



@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """ Help intent handler

    This returns a response containing a help message, and repeats the pattern for the current question.
    If this is an out-of-session request though, it creates a new game.
    """
    
    try:
        state = handler_input.attributes_manager.session_attributes[SESSION_STATE_KEY]
        speech_text = HELP_MESSAGE.format(INVOCATION_NAME, HELP_MESSAGE_PATTERN + state["ssml_pattern"])
        handler_input.response_builder.speak(speech_text).ask(REPROMPT_MESSAGE + state["ssml_pattern"]).set_card(SimpleCard(CARD_TITLE_HELP, HELP_MESSAGE.format(INVOCATION_NAME, ""))).set_should_end_session(False)
        return handler_input.response_builder.response
    except:
        # Exception can happen for an out of session request, i.e. state is not present.
        # Handle this by creating a new game.
        return create_game(handler_input)


@sb.request_handler(
    can_handle_func=lambda input:
        is_intent_name("AMAZON.CancelIntent")(input) or
        is_intent_name("AMAZON.StopIntent")(input))
def cancel_and_stop_intent_handler(handler_input):
    """ Cancel and stop intents: just say goodbye."""
    
    handler_input.response_builder.speak(GOODBYE_MESSAGE).set_card(
        SimpleCard(INVOCATION_NAME, GOODBYE_MESSAGE))
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_handler(handler_input):
    return handler_input.response_builder.response


# Global exception handler

@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Log the exception to CloudWatch, and return a generic error response."""
    
    print("Encountered following exception: {}".format(exception))
    handler_input.response_builder.speak(ERROR_MESSAGE).ask(ERROR_MESSAGE)
    return handler_input.response_builder.response


# Interceptors for request and response logging

@sb.global_request_interceptor()
def log_request(handler_input):
    """Log request to CloudWatch"""
    print("Skill request: {}\n".format(handler_input.request_envelope.request))

@sb.global_response_interceptor()
def log_response(handler_input, response):
    """Log response to CloudWatch"""
    print("Skill response: {}\n".format(response))


# handler is the lambda function entry point.
handler = sb.lambda_handler()


# For testing only: Invoke lambda handler on event contained in a file in JSON format.
if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        event = json.load(f)
        handler(event, None)
