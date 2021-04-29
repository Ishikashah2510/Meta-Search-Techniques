from django.shortcuts import render
import pandas as pd
import string


def main_page_redirect(request):
    return render(request, 'main_page.html')


def input_data(request):
    if request.method == 'POST':
        data = request.FILES['data']
        ranking = request.POST.get('ranking')
        data = pd.read_csv(data, header=0)
        if ranking.lower() == 'borda'.lower():
            vote_count, sorted_values, winner = borda_ranking(data)
            return render(request, 'main_page.html', {'count_table': vote_count,
                                                      'ordered_list': sorted_values,
                                                      'winner': winner,
                                                      'x': 0})
        elif ranking.lower() == 'condorcet'.lower():
            vote_count, sorted_values, winner = condorcet_ranking(data)
            return render(request, 'main_page.html', {'count_table': vote_count,
                                                      'ordered_list': sorted_values,
                                                      'winner': winner,
                                                      'x': 1})
        else:
            vote_count, sorted_values, winner = reciprocal_ranking(data)
            return render(request, 'main_page.html', {'count_table': vote_count,
                                                      'ordered_list': sorted_values,
                                                      'winner': winner,
                                                      'x': 0})


def borda_ranking(data):
    num_of_candidates = len(data)
    candidate_list = string.ascii_uppercase
    candidate_list = candidate_list[:num_of_candidates]
    vote_count = {}
    for candidate in candidate_list:
        vote_count[candidate] = 0
    for j in data.columns:
        for i in range(num_of_candidates):
            vote_count[data[j].iloc[i]] += ((num_of_candidates - i) * int(j))
    sorted_vals = sorted(vote_count.items(), key=lambda x: -x[1])
    sorted_values = []
    for a in sorted_vals:
        sorted_values.append(a[0])

    del sorted_vals
    del candidate_list
    del num_of_candidates
    del data

    winner = sorted_values[0]
    return vote_count, sorted_values, winner


def condorcet_ranking(data):
    num_of_candidates = len(data)
    candidate_list = string.ascii_uppercase
    candidate_list = candidate_list[:num_of_candidates]
    pair_winner = {}
    pairs = []
    for candidate in candidate_list:
        for candidate2 in candidate_list:
            if candidate != candidate2 and (candidate, candidate2) not in pairs:
                if (candidate2, candidate) not in pairs:
                    pairs.append((candidate, candidate2))
    for p in pairs:
        votea, voteb = 0, 0
        for j in data.columns:
            for i in range(num_of_candidates - 1):
                if data[j].iloc[i] == p[0] and p[1] in list(data.loc[i+1:, j]):
                    votea += int(j)
                elif data[j].iloc[i] == p[1] and p[0] in list(data.loc[i+1:, j]):
                    voteb += int(j)
        if votea > voteb:
            pair_winner[p] = [p[0], (votea, voteb)]
        else:
            pair_winner[p] = [p[1], (votea, voteb)]

    wins = {}
    for pair, winner in pair_winner.items():
        if winner[0] in wins.keys():
            wins[winner[0]] += 1
        else:
            wins[winner[0]] = 1
    sorted_vals = sorted(wins.items(), key=lambda x: -x[1])

    winner = ''
    if sorted_vals[0][1] == (num_of_candidates - 1):
        winner = sorted_vals[0][0]

    del candidate_list
    del num_of_candidates
    del data
    del wins

    return pair_winner, sorted_vals, winner


def reciprocal_ranking(data):
    num_of_candidates = len(data)
    candidate_list = string.ascii_uppercase
    candidate_list = candidate_list[:num_of_candidates]
    candidate_score = {}
    for candidate in candidate_list:
        candidate_score[candidate] = 0
    for j in data.columns:
        for i in range(num_of_candidates):
            candidate_score[data[j].iloc[i]] += (1 / (i + 1))
    sorted_vals = sorted(candidate_score.items(), key=lambda x: -x[1])
    sorted_values = []
    for a in sorted_vals:
        sorted_values.append(a[0])

    del sorted_vals
    del candidate_list
    del num_of_candidates
    del data

    winner = sorted_values[0]
    return candidate_score, sorted_values, winner
