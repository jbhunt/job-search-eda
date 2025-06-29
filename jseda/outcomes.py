from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler
import polars as pl
from matplotlib import pyplot as plt
import numpy as np
from sklearn.utils import resample

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

        subset = self.df.filter(pl.col('Submitted').is_null().not_()).select([
            'Industry',
            'Referral',
            'Pay minimum',
            'Pay maximum',
            'Interviewed',
        ])

        # Industry (0 = non-academic, 1 = academic)
        subset = subset.with_columns(
            (
                pl.when(pl.col("Industry") == "Academia")
                .then(1)
                .otherwise(0)
                .alias("Industry")
                .cast(pl.Int8)
            )
        )

        # Pay minimum
        subset = subset.with_columns(
            (
                pl.col("Pay minimum")
                .str.replace_all(r"\D", "")
                .cast(pl.Int64, strict=False)
                .alias("Pay minimum")
            )
        )
        subset = subset.with_columns(
            pl.col('Pay minimum').fill_null(subset['Pay minimum'].median())
        )

        # Pay maximum
        subset = subset.with_columns(
            (
                pl.col("Pay maximum")
                .str.replace_all(r"\D", "")
                .cast(pl.Int64, strict=False)
                .alias("Pay maximum")
            )
        )
        subset = subset.with_columns(
            pl.col('Pay maximum').fill_null(subset['Pay maximum'].median())
        )

        # Referral (0 = no, 1 = yes)
        subset = subset.with_columns(
            (
                pl.when(pl.col("Referral") == "Yes")
                .then(1)
                .otherwise(0)
                .alias("Referral")
                .cast(pl.Int8)
            )
        )

        # Outcome (0 = rejection, 1 = interview)
        subset = subset.with_columns(
            (
                pl.when(pl.col("Interviewed") == "Yes")
                .then(1)
                .otherwise(0)
                .alias("Interviewed")
                .cast(pl.Int8)
            )
        )

        #
        X = subset.select(['Industry', 'Referral', 'Pay minimum', 'Pay maximum']).to_numpy()
        X = MinMaxScaler().fit_transform(X)
        y = subset.select(['Interviewed']).to_numpy().ravel()
        reg = LogisticRegression()
        reg.fit(X, y)
        features = ['Industry (Academia)', 'Referral (Yes)', 'Pay minimum', 'Pay maximum']

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