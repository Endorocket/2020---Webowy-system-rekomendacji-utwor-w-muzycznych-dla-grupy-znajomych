import pickle
import pandas as pd
from collections import defaultdict
from surprise import SVD, Dataset, Reader
from surprise.model_selection import KFold
from xlwt import Workbook
wb = Workbook()

sheet1 = wb.add_sheet('Results')

dbfile = open('playlist2_tracks_pickle', 'rb')
playlists = pickle.load(dbfile)

dbfile1 = open('genres2_pickle', 'rb')
genres = pickle.load(dbfile1)

playlisty = []
scores = []

for playlista in playlists:
    for key in playlista:
        scores.append(playlista[key])
        playlisty.append(key)

max_values_list = [max(x) for x in scores]
print(max_values_list)

for num, value in enumerate(max_values_list):
    for num2,x in enumerate(scores[num]):
        scores[num][num2] = 5 * x / value

print(scores)
print(playlisty)
ratings_dict = {'itemID': [],
                'userID': [],
                'rating': []}

for num1,i in enumerate(playlisty):
    for num2,j in enumerate(scores[num1]):
        if scores[num1][num2] != 0:
            ratings_dict['itemID'].append(genres[num2])
            ratings_dict['userID'].append(i)
            ratings_dict['rating'].append(j)

df = pd.DataFrame(ratings_dict)
print(df)

reader = Reader(rating_scale=(0, 5))

def precision_recall_at_k(predictions, k=5, threshold=3.5):
    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = dict()
    recalls = dict()
    for uid, user_ratings in user_est_true.items():

        user_ratings.sort(key=lambda x: x[0], reverse=True)
        relevant = sum((true_r >= threshold) for (_, true_r) in user_ratings)
        recommended = sum((est >= threshold) for (est, _) in user_ratings[:k])
        rel_and_rec = sum(((true_r >= threshold) and (est >= threshold))
                              for (est, true_r) in user_ratings[:k])

        precisions[uid] = rel_and_rec / recommended if recommended != 0 else 1
        recalls[uid] = rel_and_rec / relevant if relevant != 0 else 1

    return precisions, recalls

counter = 0
sheet1.write(counter + 1, 0, 'rank_by_mean_precision')
sheet1.write(counter + 1, 1, 'rank_by_mean_recall')
sheet1.write(counter + 1, 2, 'split_1_precision')
sheet1.write(counter + 1, 3, 'split_1_recall')
sheet1.write(counter + 1, 4, 'split_2_precision')
sheet1.write(counter + 1, 5, 'split_2_recall')
sheet1.write(counter + 1, 6, 'split_3_precision')
sheet1.write(counter + 1, 7, 'split_3_recall')
sheet1.write(counter + 1, 8, 'split_4_precision')
sheet1.write(counter + 1, 9, 'split_4_recall')
sheet1.write(counter + 1, 10, 'split_5_precision')
sheet1.write(counter + 1, 11, 'split_5_recall')
sheet1.write(counter + 1, 12, 'mean_precision')
sheet1.write(counter + 1, 13, 'mean_recall')
sheet1.write(counter + 1, 14, 'n_factors')
sheet1.write(counter + 1, 15, 'n_epochs')
sheet1.write(counter + 1, 16, 'lr_all')
sheet1.write(counter + 1, 17, 'reg_all')
sheet1.write(counter + 1, 18, 'recommended_amount')

n_factors = [x for x in range(40,240,40)]
n_epochs = [x for x in range(5,25,5)]
lr_all = [0.002,0.005,0.02,0.05,0.2,0.5]
reg_all = [0.02,0.05,0.2,0.5,2,5]
metrics = [100]

data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)
kf = KFold(n_splits=5)
list_for_excel = []
for n_factor in n_factors:
    for n_epoch in n_epochs:
        for lr in lr_all:
            for reg in reg_all:
                for metric in metrics:
                    counter +=1
                    print('Counter', counter)
                    results_with_params = []

                    algo = SVD(n_factors=n_factor,n_epochs=n_epoch,lr_all=lr,reg_all=reg)
                    list_of_precisions = []
                    list_of_recalls = []

                    num = 0
                    for trainset, testset in kf.split(data):
                        algo.fit(trainset)
                        predictions = algo.test(testset)
                        precisions, recalls = precision_recall_at_k(predictions, k=metric, threshold=3)

                        avg_precision = sum(prec for prec in precisions.values()) / len(precisions)
                        avg_recall = sum(rec for rec in recalls.values()) / len(recalls)

                        results_with_params.append(avg_precision)
                        results_with_params.append(avg_recall)

                        print('Avg precision ',num+1,': ',avg_precision)
                        print('Avg recall: ',num+1,': ',avg_recall)
                        list_of_precisions.append(avg_precision)
                        list_of_recalls.append(avg_recall)

                        num += 2

                    results_with_params.append(sum(list_of_precisions)/5)
                    results_with_params.append(sum(list_of_recalls)/5)
                    results_with_params.append(n_factor)
                    results_with_params.append(n_epoch)
                    results_with_params.append(lr)
                    results_with_params.append(reg)
                    results_with_params.append(metric)

                    list_for_excel.append(results_with_params)

list_for_excel.sort(key = lambda x: x[11],reverse=True)
for num,small_list in enumerate(list_for_excel):
    small_list.insert(0,num+1)
list_for_excel.sort(key = lambda x: x[11],reverse=True)
for num, small_list in enumerate(list_for_excel):
    sheet1.write(num+2, 0, num+1)
    for num2, stat in enumerate(small_list):
        sheet1.write(num+2, num2+1, stat)

wb.save('results.xls')