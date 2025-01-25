from . import AccModel
import pandas as pd
import numpy as np
from shap import Explainer
from shap.maskers import Independent, Masker

class AccMasker(Masker):
    def __init__(
        self, X:pd.DataFrame, acc_model:AccModel, 
        age_column='age', 
        delta_age=5, 
        algo='age_vs_ages', 
        max_num_closest_samples=250,
        min_num_closest_samples=5, 
        verbose=False
    ):
        self.ages = X[age_column]
        self.ages_sorted = self.ages.sort_values().values

        self.X = X.drop(columns=[age_column])
        self.predicted_ages = pd.Series(
            acc_model.predict(self.X), index=self.X.index
        )
        self.predicted_ages_sorted = self.predicted_ages.sort_values().values

        self.accelerations = pd.Series(
            acc_model.predictacc(self.X, self.ages), index=self.X.index
        )
        self.age_acc = pd.DataFrame(
            {'age': self.ages, 'acc': self.accelerations}
        )
        self.age_sorted_acc = self.age_acc.sort_values(by="age")

        self.age_column = age_column
        self.delta_age = delta_age
        self.max_num_closest_samples = max_num_closest_samples
        self.min_num_closest_samples = min_num_closest_samples
        self.shape = self.X.shape
        self.acc_model = acc_model
        self.feature_names = self.X.columns
        self.supports_delta_masking = True
        self.verbose = verbose
        
        self.algo = algo

    def mask_shapes(self, *args):
        return [self.X.shape[1:2], [0]]

    def find_best_age_range(self, age, age_sorted, min_samples=250):
        ages = age_sorted
        pos = np.searchsorted(ages, age)
        l = pos
        r = pos + 1
        cm = ages[pos]
        cms = []
        for i in range(min_samples):
            if cm / (r - l) >= age and l > 0:
                l -= 1
                cms += [ages[l]]
                cm += ages[l]
            elif r < len(ages):
                cm += ages[r]
                cms += [ages[r]]
                r += 1

        min_age = ages[l]
        max_age = ages[r - 1]
        # print(f'Best interval: age[{l}] = {min_age} -> age[{r - 1}] = {max_age}')
        # print('Mean age:', ages[l:r].mean())
        # plt.plot(cms)
        return min_age, max_age

    def find_best_acc_age_range(self, age, age_sorted_acc, min_samples=100):
        ages = age_sorted_acc['age'].values
        accs = age_sorted_acc['acc'].values
        pos = np.searchsorted(ages, age)
        l = pos
        r = pos + 1
        cm = accs[pos]
        cms = []
        for i in range(min_samples):
            if cm / (r - l) >= 0 and l > 0:
                l -= 1
                cms += [accs[l]]
                cm += accs[l]
            elif r < len(accs):
                cm += accs[r]
                cms += [accs[r]]
                r += 1

        min_age = ages[l]
        max_age = ages[r - 1]
        # print(f'Best interval: age[{l}] = {min_age} -> age[{r - 1}] = {max_age}')
        # print('Mean age:', ages[l:r].mean())
        # print('Mean acc:', accs[l:r].mean())
        return min_age, max_age

    def __call__(self, mask, x, age):
        age = age.item()
        # mask_age = (age - self.delta_age < self.ages) & \
        #     (self.ages < age + self.delta_age)

        # min_age, max_age = self.find_best_age_range(age, self.predicted_ages_sorted)
        # mask_age = (min_age < self.predicted_ages) & (self.predicted_ages < max_age)

        if self.algo == 'age_vs_ages':
            min_age, max_age = self.find_best_age_range(
                age, self.ages_sorted, self.max_num_closest_samples
            )
            mask_age = (min_age < self.ages) & (self.ages < max_age)
            if self.verbose:
                print('Age', age)
                print(f'Best interval: cage min {min_age} -> cage max = {max_age}')
                print('Mean cage:', self.predicted_ages[mask_age].mean())
                print('Mean age:', self.ages[mask_age].mean())
                print('Min age:', self.ages[mask_age].min())
                print('Max age:', self.ages[mask_age].max())
                print('Num samples:', len(self.ages[mask_age]))
    
        
        if self.algo == 'age_vs_cages':
            min_age, max_age = self.find_best_age_range(
                age, self.predicted_ages_sorted, self.max_num_closest_samples
            )
            mask_age = (min_age < self.predicted_ages) & (self.predicted_ages < max_age)
            if self.verbose:
                print('Age', age)
                print(f'Best interval: cage min {min_age} -> cage max = {max_age}')
                print('Mean cage:', self.predicted_ages[mask_age].mean())
                print('Mean age:', self.ages[mask_age].mean())
                print('Min age:', self.ages[mask_age].min())
                print('Max age:', self.ages[mask_age].max())
    

        # min_age, max_age = self.find_best_age_range(age, self.age_sorted_acc)
        # mask_age = (min_age < self.ages) & (self.ages < max_age)

        num_samples = mask_age.sum()
        # print('Num samples', num_samples)
        if num_samples < self.min_num_closest_samples:
            raise ValueError(
                f'Not enough samples for age: {age:0.1f} years. ' + 
                f'Found only {num_samples} in {min_age:0.1f} to {max_age:0.1f} years'
            )
        masker = Independent(self.X[mask_age], max_samples=num_samples)
        res = masker(mask, x)

        num_all_masks = res[0][0].shape[0]
        num_masks = num_all_masks // num_samples
        assert num_masks * num_samples == num_all_masks

        # Both ages and avg ages produces same results in shap values
        ages = pd.concat(
            [self.ages[mask_age]] * num_masks, 
            ignore_index=True
        )
        ages = pd.DataFrame(
            [np.mean(self.ages[mask_age])] * num_all_masks
        )

        return (res[0][0], ages), res[1]

class AccModelExplainer(AccModel):
    def make_shap_explainer_acc(
        self, X:pd.DataFrame, 
        algorithm="permutation",
        seed=42,
        age_column='age', 
        acc_masker_config={
            "delta_age": 5, 
            "algo": 'age_vs_ages', 
            "max_num_closest_samples": 250,
            "min_num_closest_samples": 5
        },
    ):
        def acc_predictor(masked_data, ages=None):
            df = pd.DataFrame(masked_data, columns=list(X.columns).remove(age_column))

            acc = self.predictacc(
                df,
                pd.DataFrame(ages)
            )
            return acc
        
        acc_masker = AccMasker(X, acc_model=self, age_column=age_column, **acc_masker_config)
        self.acc_explainer = Explainer(
            acc_predictor,
            acc_masker,
            algorithm=algorithm,
            seed=seed
        )

        return self.acc_explainer

    def make_shap_explainer(self, X, max_samples=100):
        self.explainer = Explainer(
            self.predict,
            Independent(X, max_samples=max_samples),
        )
        return self.explainer