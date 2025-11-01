pronouns = {
    "I": 1,
    "he": 2,
    "she": 2,
    "it": 2,
    "they": 1,
    "we": 1,
    "you": 1
}

sentence_types = {
    "affirmative sentences": 1,
    "negative sentences": 1,
    "interrogative sentences": 1,
    "interrogative-negative sentences in a formal style": 1,
    "interrogative-negative sentences in an informal style": 1,
    "interrogative sentences with a question word": 1,
}

obsidian_links = {
    "present continuous": "obsidian://open?vault=main&file=present%20continuous%20tense",
    "present simple": "obsidian://open?vault=main&file=present%20indefinite%20form%20of%20the%20verb",
    "present perfect": "obsidian://open?vault=main&file=present%20perfect%20tense",
    "present perfect continuous": "obsidian://open?vault=main&file=present%20perfect%20continuous%20form%20of%20the%20verb",

    "past simple": "obsidian://open?vault=main&file=past%20indefinite%20form%20of%20the%20verb",
    "past continuous": "obsidian://open?vault=main&file=past%20continuous%20form%20of%20the%20verb",
    "past perfect": "obsidian://open?vault=main&file=past%20perfect%20tense",
    "past perfect continuous": "obsidian://open?vault=main&file=past%20perfect%20continuous%20tense",

    "future simple": "obsidian://open?vault=main&file=future%20indefinite%20tense",
    "future continuous": "obsidian://open?vault=main&file=future%20continuous%20tense",
    "future perfect": "obsidian://open?vault=main&file=future%20perfect%20indefinite%20tense",
    "future perfect continuous": "obsidian://open?vault=main&file=future%20perfect%20continuous%20tense",
}

tenses = {
    "present continuous": 1,
    "present simple": 1,
    "present perfect": 1,
    "present perfect continuous": 2,

    "past simple": 3,
    "past continuous": 4,
    "past perfect": 3,
    "past perfect continuous": 0,

    "future simple": 0,
    "future continuous": 0,
    "future perfect": 0,
    "future perfect continuous": 0,
}

usages = {
    "present continuous": {
        "to talk about events/state which are true **around the moment of speaking or now**": 1,
        "simultaneous/parallel actions that are occurring in a certain period of time": 1,
        "to describe actions which are repeated or regular, but which we believe to be temporary": 1,
        "to talk about a gradual change": 1,
        "to emphasize that the action or state is continuing for a certain period of time": 1,
        "unnatural, unusual action or state that is temporary": 1,
        "used to add emotional coloring to continuously repeated (actions/states)": 1,
        "used to add emotional coloring to constant, repeated, unplanned or undesired (actions/states)": 1,
        "to show that we have already decided something and usually that we have already made a plan or arrangements": 1
    },
    "present simple": {
        "to express a repeated action or to state a permanent characteristic that describes an object or phenomenon in the present or in an absolute sense": 5,
        "to talk about general facts that are always true and permanent about the world": 5,
        "to talk about general facts that we think are true and permanent at the present time": 5,
        "to talk about regular or habitual events": 5,
        "to describe a series of actions – one action after another": 2,
        "to give instructions or directions": 2,
        "to talk about feelings and reactions at the moment of speaking (with verbs of senses and perception)": 3,
        "to refer to a future action that is considered a certain fact, or because there is a clear or fixed schedule or timetable": 3,
        "in subordinate clauses of time and condition to indicate an action in the future": 4,
        "with speech act verbs (verbs which perform the act that they describe)": 1,
        "with speech act verbs in formal statements and in business or legal communications": 1,
        "in news headlines to report past events. It emphasises the drama or immediacy of an event": 1,
        "used by sports commentators to give commentaries or report actions as they are happening": 1,
    },
    "present perfect": {
        "to talk about a finished event or state that has a connection with the present (result)": 3,
        "to talk about a finished event or state in the very recent past in order to emphasize the current state (The Nearest Past)": 2,
        "to talk about experiences up to now": 2,
        "for a unique experience when we are using a superlative": 2,
        "with \"the first time\" when we’re talking about an immediate, continuing or recent event": 2,
        "to tell the news/current state": 2,
        "in newspaper headlines or TV news programmes to report a recent past event": 1,
        "to introduce an \"open\" general point about something (in question or statement)": 2,
        "to talk about a present situation that began at a specific point in the past and is still going on in the present": 2,
        "to express simultaneous ongoing actions": 2,
        "to ask about the duration of a state or activity": 2,
        "to refer to things we intend to do in the future but which are not done": 2,
        "to emphasise that something is done or achieved, often before the expected time": 2,
        "to emphasise that something we expected to happen continues not to happen": 2,
        "instead of present perfect continuous with stative verbs": 1,
    },
    "present perfect continuous": {
        "to talk about a recently finished activity that was ongoing up to now and that has a connection with the present (result)": 1,
        "for an activity that began at a point in the past and is still continuing (at the moment of speech)": 1,
        "to talk about repeated activities which started at a particular time in the past and are still continuing up until now": 1,
        "to ask and answer questions about the duration of an activity": 1,
        "to describe an unusual or uncharacteristic action that is temporary": 1,
        "to add emotional coloring (such as annoyance or criticism) to a statement, especially when describing repeated or irritating actions — often with adverbs like `always`, `constantly`, etc.": 1,
    },
    "past simple": {
        "to talk about definite time in the past (often we specify when something happened, e.g. yesterday, three weeks ago, last year, when I was young)": 1,
        "to indicate a single action in the past": 1,
        "to express a repeated action/event that happened more than once  (habitual events)": 1,
        "to indicate a permanent feature (state) of the object": 1,
        "to express a sequence of actions in the past": 1,
        "to express a polite, modest, or unobtrusive request, wish, or question": 2,
        "to form the verb constructions of subjunctive mood II: when expressing an event considered unreal": 2,
    },
    "past continuous": {
        "to talk about actions and states in progress (happening) around a **particular time** in the past": 2,
        "simultaneous/parallel actions": 1,
        "a longer action that was in progress when another action occurred (interruption)": 2,
        "to describe something **temporary** that was happening in our life in the past": 2,
        "to emphasise that the action or state continued for a period of time in the past": 2,
        "used to add emotional coloring to continuously repeated (events/states)": 2,
        "used to add emotional coloring to constant, repeated, unplanned or undesired (events/states)": 2,
        "unnatural, unusual action or state that is temporary": 2,
        "to give a reason or context for an event": 2,
        "to talk about repeated 'background' events in the past. It can suggest that the situation was temporary or subject to change": 2,
        "to create a background or atmosphere when telling a story - **(artistic)**": 1,
    },
    "past perfect": {
        "to describe an action or state that has already occurred up to a certain point in the past": 1,
        "to describe an action or state that has already not occurred up to a certain point in the past": 1,
        "to indicate an action/state in the past in the subjunctive mood II": 1,
        "to refer to situations which have changed": 1,
        "some special patterns: `I hadn't + V3… , when`:": 1,
        "instead of past perfect continuous with stative verbs": 1
    }
}


if __name__ == "__main__":

    tenses_sum = sum(filter(lambda x: x > 0, tenses.values()))

    for tense, usages_ in usages.items():
        print(f"{tense}: {tenses[tense]}/{tenses_sum} = {round((tenses[tense] / tenses_sum) * 100, 2)}%")

        summ = sum(usages_.values())
        for key, value in usages_.items():
            print(f"\t{key[:25]}..: {value}/{summ} = {round((value/summ) * 100, 2)}%")
        print()
