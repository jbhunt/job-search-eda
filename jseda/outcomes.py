from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
import polars as pl
from matplotlib import pyplot as plt
import numpy as np
from sklearn.utils import resample
from datetime import datetime

class OutcomesAnalysis():
    """
    """

    def __init__(self, data):
        """
        """

        self.df = pl.read_csv(data)

        return
    
    def _regress(self):
        """
        """

        subset = self.df.filter(pl.col('date_submitted').is_null().not_()).select([
            'industry',
            'referral',
            'pay_minimum',
            'pay_maximum',
            'interviewed',
            'outcome',
            'date_posted',
            'date_submitted',
        ])

        # Industry (0 = non-academic, 1 = academic)
        subset = subset.with_columns(
            (
                pl.when(pl.col("industry") == "Academia")
                .then(1)
                .otherwise(0)
                .alias("industry")
                .cast(pl.Int8)
            )
        )

        # Pay minimum
        subset = subset.with_columns(
            (
                pl.col("pay_minimum")
                .str.replace_all(r"\D", "")
                .cast(pl.Int64, strict=False)
                .alias("pay_minimum")
            )
        )
        subset = subset.with_columns(
            pl.col('pay_minimum').fill_null(subset['pay_minimum'].median())
        )

        # Pay maximum
        subset = subset.with_columns(
            (
                pl.col("pay_maximum")
                .str.replace_all(r"\D", "")
                .cast(pl.Int64, strict=False)
                .alias("pay_maximum")
            )
        )
        subset = subset.with_columns(
            pl.col('pay_maximum').fill_null(subset['pay_maximum'].median())
        )

        # Referral (0 = no, 1 = yes)
        subset = subset.with_columns(
            (
                pl.when(pl.col("referral") == "Yes")
                .then(1)
                .otherwise(0)
                .alias("referral")
                .cast(pl.Int8)
            )
        )

        # Outcome (0 = rejection, 1 = interview)
        subset = subset.with_columns(
            (
                pl.when(pl.col("interviewed") == "Yes")
                .then(1)
                .otherwise(0)
                .alias("onterviewed")
                .cast(pl.Int8)
            )
        )

        #
        X = subset.select(['industry', 'referral', 'pay_minimum', 'pay_maximum']).to_numpy()
        x1 = subset.select(['industry']).to_numpy().ravel()
        x2 = subset.select(['referral']).to_numpy().ravel()
        x3 = subset.select(['pay_minimum', 'pay_maximum']).to_numpy().mean(1)
        x4 = list()
        for i, t1 in enumerate(subset['date_posted']):
            if t1 is None:
                dt = np.nan
            else:
                t1 = datetime.strptime(t1, "%m/%d/%Y")
                t2 = subset['date_submitted'][i]
                if t2 is None:
                    dt = np.nan
                else:
                    t2 = datetime.strptime(t2, "%m/%d/%Y")
                    dt = (t2 - t1).days
            x4.append(dt)
        x4 = np.array(x4)
        X = np.vstack([x1, x2, x3, x4]).T        
        X = MinMaxScaler().fit_transform(X)
        y = np.around(subset.select(['outcome']).to_numpy().ravel(), 0)
        m = np.logical_or(np.isnan(y), np.isnan(X).any(1))
        X = np.delete(X, m, axis=0)
        y = np.delete(y, m)
        reg = LogisticRegression()
        reg.fit(X, y)
        features = ['Industry (Academia)', 'Referral (Yes)', 'Average pay', 'Application lag']

        # Use boostrapping/resampling to compute CIs
        b = 0
        B = 1000
        coefs = np.empty((B, X.shape[1]))
        while b < B:
            try:
                Xb, yb = resample(X, y, replace=True, stratify=y)
                model  = LogisticRegression()
                model.fit(Xb, yb)
                coefs[b] = model.coef_.flatten()
                b += 1
            except:
                continue
        ci95 = np.percentile(coefs, [2.5, 97.5], axis=0)

        return reg, ci95.T, features
    
    def plot(
        self,
        figsize=(6.5, 2.35)
        ):
        """
        """

        reg, ci95, features = self._regress()
        fig, ax = plt.subplots()
        odds = np.exp(reg.coef_.flatten())
        ncoef = len(odds)
        index = np.argsort(odds)
        odds = odds[index]
        ci95 = np.exp(ci95)[index, :]
        labels = np.array(features)[index].tolist()
        ax.hlines(
            np.arange(ncoef),
            ci95[:, 0],
            ci95[:, 1],
            color=[f'C{i}' for i in range(ncoef)],
            zorder=-1,
            lw=1,
        )
        ax.scatter(
            odds,
            np.arange(ncoef),
            s=30,
            marker='D',
            edgecolor='none',
            c=[f'C{i}' for i in range(ncoef)]
        )
        xlim = ax.get_xlim()
        ax.set_xlim([0, xlim[1]])
        ylim = np.array(ax.get_ylim()) * 1.1
        ax.vlines(1, *ylim, color='k', linestyles=':', lw=1)
        ax.set_ylim(ylim)
        ax.set_yticks(np.arange(ncoef))
        ax.set_yticklabels(labels)
        ax.set_xlabel(r'Odds ratio (exp($\beta$))')
        fig.set_figwidth(figsize[0])
        fig.set_figheight(figsize[1])
        fig.tight_layout()

        return fig, ax