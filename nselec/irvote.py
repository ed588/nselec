# instant-runoff preferential stuff
from collections import Counter
from math import ceil
from copy import deepcopy


def compute_winner(votes):
    votes = deepcopy(list(votes))
    # votelist should be a list of lists of ints
    # we assume the votes are all already checked
    num_votes = len(votes)
    if num_votes == 0:
        # we have reached a tie!
        return None
    needed_majority = ceil(num_votes / 2.0)
    while True:
        # nb: this may not be the original "first" choice if we've eliminated a candidate
        first_choices = [vote[0] for vote in votes]
        # now, count them:
        c_first_choices = Counter(first_choices)
        best_first_choice = c_first_choices.most_common(1)[0]
        if best_first_choice[1] >= needed_majority:
            return best_first_choice[0]
        else:
            # we need to find the lowest, or joint lowest candidate(s)
            # and remove them from all votes, then start again.
            single_worst = c_first_choices.most_common()[:-2:-1][0][1]
            # gets the last place one, for its value.
            worst_candidates = [
                i[0] for i in c_first_choices.items() if i[1] == single_worst
            ]
            new_votes = []
            for vote in votes:
                if vote[0] in worst_candidates:
                    vote.pop(0)
                if vote:
                    new_votes.append(vote)
        votes = new_votes
